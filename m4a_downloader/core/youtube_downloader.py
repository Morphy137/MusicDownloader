"""YouTube audio downloader module - Optimized version with MP3/M4A support"""
import os
import yt_dlp
from typing import Optional, List, Dict
import logging
import re
from difflib import SequenceMatcher
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import subprocess
import shutil
from ..config import Config

logger = logging.getLogger(__name__)

class YouTubeDownloader:
    def __init__(self, output_dir: str = "music/tmp", quality: str = '192', audio_format: str = 'm4a'):
        self.output_dir = output_dir
        self.quality = quality
        self.audio_format = audio_format.lower()
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Cache para búsquedas recientes
        self.search_cache = {}
        
        # Verificar FFmpeg si se necesita MP3
        if self.audio_format == 'mp3' and not Config.check_ffmpeg():
            logger.warning("MP3 format selected but FFmpeg not found. Falling back to M4A.")
            self.audio_format = 'm4a'
        
    def _normalize_text(self, text: str) -> str:
        """Normalizar texto para comparaciones más efectivas"""
        if not text:
            return ""
        
        # Remover caracteres especiales y normalizar
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remover palabras comunes que pueden confundir
        stop_words = ['official', 'video', 'music', 'audio', 'hd', 'hq', 'lyrics', 'the', 'a', 'an']
        words = [w for w in text.split() if w not in stop_words]
        
        return ' '.join(words)
    
    def _get_optimized_search_queries(self, track_info: dict) -> List[str]:
        """Generar consultas de búsqueda optimizadas - menos variantes, más efectivas"""
        artist = track_info.get('artist_name', '')
        title = track_info.get('track_title', '')
        
        # Normalizar para búsqueda
        clean_artist = re.sub(r'[^\w\s-]', '', artist)
        clean_title = re.sub(r'[^\w\s-]', '', title)
        
        # Solo 3-4 consultas más efectivas en orden de prioridad
        queries = [
            f'ytsearch2:"{clean_artist}" "{clean_title}"',  # Solo 2 resultados
            f'ytsearch2:{clean_artist} {clean_title}',
        ]
        
        # Solo agregar consulta adicional si el título es muy específico
        if len(clean_title.split()) > 2:
            queries.append(f'ytsearch5:{clean_artist} {clean_title} audio')
        
        return queries
    
    def _quick_score_video(self, entry, track_info: dict) -> float:
        """Scoring rápido y eficiente - solo métricas esenciales"""
        if not entry or not entry.get('title'):
            return 0.0
        
        artist_norm = self._normalize_text(track_info.get('artist_name', ''))
        title_norm = self._normalize_text(track_info.get('track_title', ''))
        
        video_title_norm = self._normalize_text(entry.get('title', ''))
        uploader_norm = self._normalize_text(entry.get('uploader', ''))
        
        score = 0.0
        
        # 1. Coincidencia de título (50% del peso)
        if title_norm in video_title_norm or video_title_norm in title_norm:
            score += 0.5
        else:
            # Si no hay coincidencia exacta, usar similitud rápida solo si es necesario
            title_similarity = SequenceMatcher(None, title_norm, video_title_norm).ratio()
            if title_similarity > 0.6:
                score += title_similarity * 0.3
        
        # 2. Coincidencia de artista (35% del peso)
        if artist_norm in video_title_norm or artist_norm in uploader_norm:
            score += 0.25
        
        # 3. Filtros rápidos de calidad (15% del peso)
        duration = entry.get('duration', 0)
        
        # Duración ideal: 1-8 minutos (la mayoría de canciones)
        if 60 <= duration <= 480:
            score += 0.1
        
        # Canal oficial rápido
        uploader_lower = entry.get('uploader', '').lower()
        if any(indicator in uploader_lower for indicator in ['official', 'records', 'vevo', 'topic']):
            score += 0.15
        
        # Penalizaciones rápidas
        title_lower = entry.get('title', '').lower()
        
        # Shorts - penalización fuerte
        if duration <= 60 or '/shorts/' in entry.get('webpage_url', ''):
            score *= 0.3
            
        # Otros filtros negativos
        bad_keywords = ['cover', 'remix', 'live', 'acoustic', 'karaoke', 'reaction']
        if any(keyword in title_lower for keyword in bad_keywords):
            score *= 0.7
        
        return min(1.0, score)
    
    def _search_single_query(self, query: str, track_info: dict) -> Optional[Dict]:
        """Buscar en una sola query y retornar el mejor resultado"""
        try:
            ydl_opts = {
                'quiet': True,
                'skip_download': True,
                'extract_flat': False,
                'force_json': True,
                'no_warnings': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(query, download=False)
                entries = info.get('entries', [])
                
                if not entries:
                    return None
                
                # Evaluar solo los primeros resultados y tomar el mejor inmediatamente
                best_video = None
                best_score = 0.0
                
                for entry in entries[:3]:  # Solo evaluar primeros 3 resultados
                    if not entry or 'id' not in entry:
                        continue
                        
                    score = self._quick_score_video(entry, track_info)
                    
                    if score > best_score:
                        best_video = entry
                        best_score = score
                    
                    # Si encontramos algo muy bueno (>0.7), usar inmediatamente
                    if score > 0.7:
                        logger.debug(f"Quick match found: {entry.get('title')} (score: {score:.2f})")
                        return {'entry': entry, 'score': score}
                
                if best_video and best_score > 0.6:  # Umbral más bajo para ser más rápido
                    return {'entry': best_video, 'score': best_score}
                    
        except Exception as e:
            logger.debug(f"Query failed: {query[:50]}... - {e}")
            
        return None
    
    def find_youtube(self, track_info: dict) -> str:
        """Búsqueda ultra-optimizada en YouTube con fallback agregando 'song' al título si no se encuentra resultado adecuado"""
        if not track_info or not track_info.get('track_title'):
            raise ValueError("Track info cannot be empty")

        artist = track_info.get('artist_name', '')
        title = track_info.get('track_title', '')

        # Cache check
        cache_key = f"{artist}_{title}".lower()
        if cache_key in self.search_cache:
            cached_result = self.search_cache[cache_key]
            logger.debug(f"Using cached result for: {artist} - {title}")
            return cached_result

        logger.debug(f"Searching YouTube for: {artist} - {title}")
        start_time = time.time()

        queries = self._get_optimized_search_queries(track_info)

        # Buscar secuencialmente, parando en el primer buen resultado
        for query in queries:
            result = self._search_single_query(query, track_info)

            if result and result['score'] > 0.4:
                video_url = f"https://www.youtube.com/watch?v={result['entry']['id']}"

                # Cache del resultado
                self.search_cache[cache_key] = video_url

                # Limpiar cache si se vuelve muy grande
                if len(self.search_cache) > 100:
                    # Remover entradas más antiguas (simple FIFO)
                    oldest_keys = list(self.search_cache.keys())[:20]
                    for key in oldest_keys:
                        del self.search_cache[key]

                elapsed_time = time.time() - start_time
                logger.info(f"Found: {result['entry'].get('title')} by {result['entry'].get('uploader')} "
                            f"(score: {result['score']:.2f}, time: {elapsed_time:.1f}s)")

                return video_url

        # Fallback: agregar 'song' al final del título y buscar de nuevo, usar el primer resultado
        logger.info(f"No suitable video found for: {artist} - {title}, retrying with 'song' appended...")
        fallback_title = f"{title} song"
        fallback_query = f'ytsearch1:"{artist}" "{fallback_title}"'
        try:
            ydl_opts = {
                'quiet': True,
                'skip_download': True,
                'extract_flat': False,
                'force_json': True,
                'no_warnings': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(fallback_query, download=False)
                entries = info.get('entries', [])
                if entries:
                    entry = entries[0]
                    # Validar que el entry tiene 'id' y 'title' para evitar cuelgues
                    if 'id' in entry and 'title' in entry:
                        video_url = f"https://www.youtube.com/watch?v={entry['id']}"
                        self.search_cache[cache_key] = video_url
                        elapsed_time = time.time() - start_time
                        logger.info(f"Fallback used: {entry.get('title')} by {entry.get('uploader')} (time: {elapsed_time:.1f}s)")
                        return video_url
                    else:
                        logger.warning(f"Fallback entry missing 'id' or 'title': {entry}")
        except Exception as e:
            logger.warning(f"Fallback search failed for: {artist} - {fallback_title}: {e}")

        # Si no encontramos nada bueno, error descriptivo
        elapsed_time = time.time() - start_time
        logger.warning(f"No suitable video found for: {artist} - {title} (searched {elapsed_time:.1f}s)")
        raise ValueError(f"No suitable YouTube video found for: {artist} - {title}")
    
    def _get_ydl_opts(self) -> dict:
        """Obtener opciones de yt-dlp según el formato seleccionado"""
        base_opts = {
            'outtmpl': os.path.join(self.output_dir, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'socket_timeout': 20,
            'retries': 2,
            'fragment_retries': 2,
            'ignoreerrors': False,
        }
        
        if self.audio_format == 'mp3':
            # Para MP3: descargar M4A y convertir con FFmpeg
            base_opts.update({
                'format': 'bestaudio[ext=m4a]/bestaudio',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': self.quality,
                }],
            })
        else:
            # Para M4A: descarga directa
            base_opts.update({
                'format': 'bestaudio[ext=m4a]/bestaudio',
            })
        
        return base_opts
    
    def _convert_to_mp3(self, m4a_file: str) -> str:
        """Convertir archivo M4A a MP3 usando FFmpeg directamente"""
        if not os.path.exists(m4a_file):
            raise FileNotFoundError(f"M4A file not found: {m4a_file}")
        
        # Generar nombre del archivo MP3
        mp3_file = m4a_file.replace('.m4a', '.mp3')
        
        # Comando FFmpeg para conversión
        ffmpeg_cmd = [
            'ffmpeg', '-y',  # -y para sobrescribir sin preguntar
            '-i', m4a_file,  # archivo de entrada
            '-codec:a', 'libmp3lame',  # codec MP3
            '-b:a', f'{self.quality}k',  # bitrate
            '-avoid_negative_ts', 'make_zero',  # evitar timestamps negativos
            mp3_file  # archivo de salida
        ]
        
        try:
            # Ejecutar FFmpeg
            logger.debug(f"Converting {m4a_file} to MP3...")
            result = subprocess.run(
                ffmpeg_cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos timeout
            )
            
            if result.returncode != 0:
                logger.error(f"FFmpeg conversion failed: {result.stderr}")
                raise RuntimeError(f"FFmpeg conversion failed: {result.stderr}")
            
            # Eliminar archivo M4A original
            os.remove(m4a_file)
            logger.debug(f"Successfully converted to {mp3_file}")
            
            return mp3_file
            
        except subprocess.TimeoutExpired:
            logger.error("FFmpeg conversion timed out")
            raise RuntimeError("FFmpeg conversion timed out")
        except Exception as e:
            logger.error(f"Error during FFmpeg conversion: {e}")
            raise
    
    def download_audio(self, yt_link: str) -> str:
        """Download audio from YouTube link in specified format"""
        ydl_opts = self._get_ydl_opts()
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(yt_link, download=True)
                
                if self.audio_format == 'mp3':
                    # yt-dlp ya debería haber convertido a MP3 con postprocessor
                    # Buscar el archivo MP3 resultante
                    base_filename = ydl.prepare_filename(info)
                    mp3_filename = base_filename.replace('.m4a', '.mp3').replace('.webm', '.mp3')
                    
                    # Si yt-dlp no pudo convertir, intentar conversión manual
                    if not os.path.exists(mp3_filename) and os.path.exists(base_filename):
                        logger.info("yt-dlp conversion failed, trying manual FFmpeg conversion...")
                        if Config.check_ffmpeg():
                            mp3_filename = self._convert_to_mp3(base_filename)
                        else:
                            logger.warning("FFmpeg not available for manual conversion")
                            return base_filename  # Devolver M4A como fallback
                    
                    return mp3_filename
                else:
                    # M4A directo
                    base_filename = ydl.prepare_filename(info)
                    return base_filename
                    
            except Exception as e:
                logger.error(f"Error downloading {yt_link}: {e}")
                raise
    
    def get_output_filename(self, track_info: dict) -> str:
        """Generar nombre de archivo de salida basado en el formato"""
        artist = re.sub(r'[\\/:*?"<>|]', '', track_info.get('artist_name', ''))
        title = re.sub(r'[\\/:*?"<>|]', '', track_info.get('track_title', ''))
        extension = self.audio_format
        return f"{title} - {artist}.{extension}"