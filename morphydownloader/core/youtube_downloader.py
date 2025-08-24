"""YouTube audio downloader module - Optimized version with fast matching"""
import os
import yt_dlp
from typing import Optional, List, Dict
import logging
import re
from difflib import SequenceMatcher
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

logger = logging.getLogger(__name__)

class YouTubeDownloader:
    def __init__(self, output_dir: str = "music/tmp", quality: str = '192'):
        self.output_dir = output_dir
        self.quality = quality
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Cache para búsquedas recientes
        self.search_cache = {}
        
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
            f'ytsearch5:"{clean_artist}" "{clean_title}"',  # Búsqueda exacta con comillas
            f'ytsearch5:{clean_artist} {clean_title} official',  # Con "official"
            f'ytsearch5:{clean_artist} {clean_title}',  # Sin comillas
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
            score += 0.35
        
        # 3. Filtros rápidos de calidad (15% del peso)
        duration = entry.get('duration', 0)
        
        # Duración ideal: 1-8 minutos (la mayoría de canciones)
        if 60 <= duration <= 480:
            score += 0.1
        
        # Canal oficial rápido
        uploader_lower = entry.get('uploader', '').lower()
        if any(indicator in uploader_lower for indicator in ['official', 'records', 'vevo', 'topic']):
            score += 0.05
        
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
                
                if best_video and best_score > 0.4:  # Umbral más bajo para ser más rápido
                    return {'entry': best_video, 'score': best_score}
                    
        except Exception as e:
            logger.debug(f"Query failed: {query[:50]}... - {e}")
            
        return None
    
    def find_youtube(self, track_info: dict) -> str:
        """Búsqueda ultra-optimizada en YouTube"""
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
        
        # Si no encontramos nada bueno, error descriptivo
        elapsed_time = time.time() - start_time
        logger.warning(f"No suitable video found for: {artist} - {title} (searched {elapsed_time:.1f}s)")
        raise ValueError(f"No suitable YouTube video found for: {artist} - {title}")
    
    def download_audio(self, yt_link: str) -> str:
        """Download audio from YouTube link with optimized settings"""
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio[ext=mp3]/bestaudio',
            'outtmpl': os.path.join(self.output_dir, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'extractaudio': True,
            'audioformat': 'mp3',
            'audioquality': self.quality,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': self.quality,
            }],
            'socket_timeout': 20,  # Reducido de 30 a 20
            'retries': 2,          # Reducido de 3 a 2
            'fragment_retries': 2, # Reducido de 3 a 2
            'ignoreerrors': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(yt_link, download=True)
                base_filename = ydl.prepare_filename(info)
                mp3_filename = os.path.splitext(base_filename)[0] + '.mp3'
                return mp3_filename
            except Exception as e:
                logger.error(f"Error downloading {yt_link}: {e}")
                raise