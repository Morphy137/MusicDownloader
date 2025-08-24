"""YouTube audio downloader module"""
import os
import yt_dlp
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

class YouTubeDownloader:
    def __init__(self, output_dir: str = "music/tmp", quality: str = '192'):
        self.output_dir = output_dir
        self.quality = quality
        os.makedirs(self.output_dir, exist_ok=True)
        
    def _get_search_variants(self, query: str) -> List[str]:
        """Generate search variants for better results"""
        base_query = query.replace(" audio", "").strip()
        return [
            f'ytsearch5:"{query}"',
            f'ytsearch5:{query}',
            f'ytsearch5:{base_query}',
            f'ytsearch5:{base_query} official'
        ]
    
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

                    # Filtrar shorts: url contiene '/shorts/' o ie_key == 'YoutubeShort' o duración < 60s
                    filtered = [
                        e for e in entries
                        if (
                            'id' in e and
                            ('url' not in e or '/shorts/' not in e['url']) and
                            e.get('ie_key', '') != 'YoutubeShort' and
                            (e.get('duration') is None or e['duration'] > 60)
                        )
                    ]
                    if filtered:
                        return f"https://www.youtube.com/watch?v={filtered[0]['id']}"

            except Exception as e:
                logger.debug(f"Search variant failed: {variant}, error: {e}")
                continue

        raise ValueError(f"No YouTube video found for: {query}")
    
    def download_audio(self, yt_link: str) -> str:
        """Download audio from YouTube link"""
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(self.output_dir, '%(title)s.%(ext)s'),
            'quiet': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': self.quality,
            }],
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(yt_link, download=True)
            return ydl.prepare_filename(info).rsplit('.', 1)[0] + '.mp3'