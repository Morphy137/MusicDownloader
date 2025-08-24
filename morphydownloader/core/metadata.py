"""MP3 metadata setter module - Improved version"""
import urllib.request
import urllib.error
import ssl
import tempfile
import os
from mutagen.easyid3 import EasyID3
from mutagen.id3 import APIC, ID3
import logging

logger = logging.getLogger(__name__)

class MetadataSetter:
    @staticmethod
    def set_metadata(metadata, file_path):
        """Set metadata for MP3 file with improved album art handling"""
        try:
            # Set basic metadata
            mp3file = EasyID3(file_path)
            mp3file.update({
                "albumartist": metadata.get("artist_name", ""),
                "artist": ", ".join(metadata.get("artists", [])),
                "album": metadata.get("album_name", ""),
                "title": metadata.get("track_title", ""),
                "date": metadata.get("release_date", ""),
                "tracknumber": str(metadata.get("track_number", "")),
                "isrc": metadata.get("isrc", ""),
            })
            mp3file.save()
            
            # Handle album art with better error handling and SSL context
            album_art_url = metadata.get("album_art", "")
            if album_art_url:
                try:
                    MetadataSetter._set_album_art(file_path, album_art_url)
                except Exception as e:
                    logger.warning(f"Failed to set album art for {file_path}: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to set metadata for {file_path}: {e}")
            raise
    
    @staticmethod
    def _set_album_art(file_path, album_art_url):
        """Set album art with improved download handling"""
        # Create SSL context that doesn't verify certificates (for compatibility)
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # Create request with proper headers
        request = urllib.request.Request(
            album_art_url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        )
        
        try:
            # Download to temporary file first
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                with urllib.request.urlopen(request, context=ssl_context, timeout=30) as response:
                    temp_file.write(response.read())
                temp_path = temp_file.name
            
            # Read the downloaded image
            with open(temp_path, 'rb') as img_file:
                album_art_data = img_file.read()
            
            # Remove temporary file
            os.unlink(temp_path)
            
            # Set the album art
            audio = ID3(file_path)
            audio["APIC"] = APIC(
                encoding=3, 
                mime="image/jpeg", 
                type=3, 
                desc="Cover", 
                data=album_art_data
            )
            audio.save()
            
            logger.debug(f"Successfully set album art for {file_path}")
            
        except urllib.error.URLError as e:
            logger.warning(f"Network error downloading album art: {e}")
            raise
        except Exception as e:
            logger.warning(f"Error setting album art: {e}")
            raise