"""YouTube audio downloader module - Improved version"""
import os
import yt_dlp
from typing import Optional, List
import logging
import re

logger = logging.getLogger(__name__)

class YouTubeDownloader:
    def __init__(self, output_dir: str = "music/tmp", quality: str = '192'):
        self.output_dir = output_dir
        self.quality = quality
        os.makedirs(self.output_dir, exist_ok=True)
        
    def _get_search_variants(self, query: str) -> List[str]:
        """Generate search variants for better results"""
        base_query = query.replace(" audio", "").strip()
        
        # Limpiar caracteres especiales que pueden causar problemas
        clean_query = re.sub(r'[^\w\s-]', '', base_query)
        
        return [
            f'ytsearch10:"{query}"',  # Aumentado a 10 resultados
            f'ytsearch10:{query}',
            f'ytsearch10:{clean_query}',
            f'ytsearch10:{clean_query} official',
            f'ytsearch10:{clean_query} lyrics',
            f'ytsearch10:{clean_query} music video'
        ]
    
    def _is_shorts_video(self, entry):
        """Determinar si un video es un Short de YouTube"""
        if not entry:
            return True
        
        # Verificar URL
        url = entry.get('url', '')
        if '/shorts/' in url:
            return True
        
        # Verificar tipo
        if entry.get('ie_key', '') == 'YoutubeShort':
            return True
        
        # Verificar duración (Shorts son <= 60 segundos)
        duration = entry.get('duration')
        if duration is not None and duration <= 60:
            return True
        
        # Verificar título (algunos contienen indicadores)
        title = entry.get('title', '').lower()
        shorts_indicators = ['#shorts', '#short', 'tiktok', 'vertical']
        if any(indicator in title for indicator in shorts_indicators):
            return True
        
        return False
    
    def _is_good_match(self, entry, query):
        """Determinar si un video es una buena coincidencia para la consulta"""
        if not entry:
            return False
        
        title = entry.get('title', '').lower()
        description = entry.get('description', '').lower()
        
        # Palabras clave que indican buena calidad
        good_keywords = ['official', 'music video', 'lyrics', 'full', 'hd', 'hq']
        bad_keywords = ['cover', 'remix', 'live', 'acoustic', 'instrumental', 'karaoke', 'reaction']
        
        # Bonus por palabras buenas
        good_score = sum(1 for keyword in good_keywords if keyword in title)
        
        # Penalización por palabras malas
        bad_score = sum(1 for keyword in bad_keywords if keyword in title)
        
        # Verificar que tenga una duración razonable (30 segundos - 10 minutos)
        duration = entry.get('duration')
        if duration:
            if duration < 30 or duration > 600:  # Menos de 30s o más de 10min
                bad_score += 2
        
        # Verificar view count (videos con más vistas suelen ser mejor calidad)
        view_count = entry.get('view_count', 0)
        if view_count > 1000000:  # Más de 1M de vistas
            good_score += 1
        elif view_count < 10000:  # Menos de 10K de vistas
            bad_score += 1
        
        return good_score > bad_score
    
    def find_youtube(self, query: str) -> str:
        """Find best YouTube match for query, ignoring YouTube Shorts"""
        if not query.strip():
            raise ValueError("Search query cannot be empty")

        for variant in self._get_search_variants(query):
            try:
                ydl_opts = {
                    'quiet': True,
                    'skip_download': True,
                    'extract_flat': True,
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(variant, download=False)
                    entries = info.get('entries', [])

                    # Filtrar shorts y obtener información adicional
                    filtered_entries = []
                    for entry in entries:
                        if entry and 'id' in entry and not self._is_shorts_video(entry):
                            # Obtener información adicional del video
                            try:
                                detailed_info = ydl.extract_info(
                                    f"https://www.youtube.com/watch?v={entry['id']}", 
                                    download=False
                                )
                                if detailed_info and not self._is_shorts_video(detailed_info):
                                    filtered_entries.append(detailed_info)
                            except Exception as e:
                                logger.debug(f"Could not get detailed info for {entry['id']}: {e}")
                                # Si no podemos obtener info detallada, usar la básica
                                if not self._is_shorts_video(entry):
                                    filtered_entries.append(entry)
                    
                    if filtered_entries:
                        # Ordenar por calidad de coincidencia
                        scored_entries = []
                        for entry in filtered_entries:
                            if self._is_good_match(entry, query):
                                scored_entries.append(entry)
                        
                        # Si tenemos matches con buena puntuación, usar el primero
                        if scored_entries:
                            best_match = scored_entries[0]
                        else:
                            # Si no, usar el primer resultado filtrado
                            best_match = filtered_entries[0]
                        
                        return f"https://www.youtube.com/watch?v={best_match['id']}"

            except Exception as e:
                logger.debug(f"Search variant failed: {variant}, error: {e}")
                continue

        raise ValueError(f"No YouTube video found for: {query}")
    
    def download_audio(self, yt_link: str) -> str:
        """Download audio from YouTube link with improved settings"""
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
            # Opciones adicionales para mejor compatibilidad
            'socket_timeout': 30,
            'retries': 3,
            'fragment_retries': 3,
            'ignoreerrors': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(yt_link, download=True)
                # Construir el nombre del archivo final
                base_filename = ydl.prepare_filename(info)
                mp3_filename = os.path.splitext(base_filename)[0] + '.mp3'
                return mp3_filename
            except Exception as e:
                logger.error(f"Error downloading {yt_link}: {e}")
                raise