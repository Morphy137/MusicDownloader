"""MP3 metadata setter module - Enhanced SSL and certificate handling"""
from mutagen.mp4 import MP4, MP4Cover
from mutagen.id3 import ID3, APIC
import urllib.request
import tempfile
import ssl
import os
import sys
import logging

logger = logging.getLogger(__name__)

class MetadataSetter:
    @staticmethod
    def get_ssl_context():
        """Crear contexto SSL optimizado para descargas de portadas"""
        try:
            # Intentar usar certifi si está disponible
            try:
                import certifi
                ssl_context = ssl.create_default_context(cafile=certifi.where())
                logger.debug("SSL context created using certifi")
                return ssl_context
            except ImportError:
                logger.warning("certifi not available, using default SSL context")
            
            # Crear contexto SSL por defecto
            ssl_context = ssl.create_default_context()
            
            # Si estamos en un ejecutable empaquetado, ser más permisivo
            if hasattr(sys, '_MEIPASS'):
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                logger.debug("Running in packaged mode, relaxed SSL verification")
            
            return ssl_context
            
        except Exception as e:
            logger.warning(f"Failed to create SSL context: {e}")
            # Última opción: contexto muy permisivo
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            return ssl_context
    
    @staticmethod
    def set_metadata(metadata, file_path):
        """Set metadata for m4a file"""
        try:
            # Set basic metadata
            mp4file = MP4(file_path)
            mp4file['\xa9nam'] = metadata.get("track_title", "")  # Title
            mp4file['\xa9ART'] = ", ".join(metadata.get("artists", []))  # Artist
            mp4file['\xa9alb'] = metadata.get("album_name", "")  # Album
            mp4file['\xa9day'] = metadata.get("release_date", "")  # Year
            mp4file['trkn'] = [(metadata.get("track_number", 0), 0)]  # Track number
            mp4file.save()
            logger.debug(f"Basic metadata set for {os.path.basename(file_path)}")
            
            # Handle album art
            album_art_url = metadata.get("album_art", "")
            if album_art_url:
                try:
                    MetadataSetter._set_album_art_with_fallbacks(file_path, album_art_url)
                    logger.debug(f"Album art successfully set for {os.path.basename(file_path)}")
                except Exception as e:
                    logger.warning(f"Failed to set album art: {e}")
        except Exception as e:
            logger.error(f"Failed to set metadata for {file_path}: {e}")
            raise
    
    @staticmethod
    def _set_album_art_with_fallbacks(file_path, album_art_url):
        """Set album art with multiple fallback strategies"""
        strategies = [
            MetadataSetter._download_with_certifi,
            MetadataSetter._download_with_default_ssl,
            MetadataSetter._download_without_ssl_verification,
        ]
        
        last_error = None
        for i, strategy in enumerate(strategies, 1):
            try:
                logger.debug(f"Trying album art download strategy {i}/{len(strategies)}")
                strategy(file_path, album_art_url)
                return  # Success!
            except Exception as e:
                last_error = e
                logger.debug(f"Strategy {i} failed: {e}")
                continue
        
        # All strategies failed
        raise last_error or Exception("All album art download strategies failed")
    
    @staticmethod
    def _download_with_certifi(file_path, album_art_url):
        """Strategy 1: Download using certifi certificates"""
        try:
            import certifi
        except ImportError:
            raise Exception("certifi not available")
        
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        MetadataSetter._download_and_set_art(file_path, album_art_url, ssl_context)
    
    @staticmethod
    def _download_with_default_ssl(file_path, album_art_url):
        """Strategy 2: Download with default SSL context"""
        ssl_context = ssl.create_default_context()
        MetadataSetter._download_and_set_art(file_path, album_art_url, ssl_context)
    
    @staticmethod
    def _download_without_ssl_verification(file_path, album_art_url):
        """Strategy 3: Download without SSL verification (last resort)"""
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        MetadataSetter._download_and_set_art(file_path, album_art_url, ssl_context)
    
    @staticmethod
    def _download_and_set_art(file_path, album_art_url, ssl_context):
        """Download and set album art with given SSL context for MP3 or m4a"""
        # Create request with proper headers
        request = urllib.request.Request(
            album_art_url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
        )
        
        try:
            # Download to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                with urllib.request.urlopen(request, context=ssl_context, timeout=20) as response:
                    # Verify content type
                    content_type = response.headers.get('Content-Type', '')
                    if not content_type.startswith('image/'):
                        raise Exception(f"Invalid content type: {content_type}")
                    
                    # Read and write data
                    data = response.read()
                    if len(data) < 1000:  # Too small to be a valid image
                        raise Exception(f"Downloaded data too small: {len(data)} bytes")
                    
                    temp_file.write(data)
                temp_path = temp_file.name
            
            # Verify we can read the image back
            with open(temp_path, 'rb') as img_file:
                album_art_data = img_file.read()
            
            # Clean up temp file
            os.unlink(temp_path)
            
            # Determine MIME type from URL or content
            mime_type = "image/jpeg"  # Default
            if album_art_url.lower().endswith('.png'):
                mime_type = "image/png"
            elif album_art_url.lower().endswith('.webp'):
                mime_type = "image/webp"
            
            # Check file extension to determine format
            if file_path.lower().endswith('.m4a'):
                # Handle m4a
                audio = MP4(file_path)
                # Remove previous covers to avoid duplicates
                audio.pop('covr', None)
                audio['covr'] = [MP4Cover(album_art_data, imageformat=MP4Cover.FORMAT_JPEG if mime_type == "image/jpeg" else MP4Cover.FORMAT_PNG)]
                audio.save()
            else:
                # Handle MP3
                audio = ID3(file_path)
                audio.delall("APIC")
                audio.add(APIC(
                    encoding=0,  # Latin1 para max compatibilidad
                    mime=mime_type,
                    type=3,  # Cover (front)
                    desc="Cover",
                    data=album_art_data
                ))
                audio.save(v2_version=3)  # ID3v2.3 para compatibilidad
            
            logger.debug(f"Album art set successfully: {len(album_art_data)} bytes, {mime_type}, file: {file_path}")
            
        except urllib.error.HTTPError as e:
            raise Exception(f"HTTP error {e.code}: {e.reason}")
        except urllib.error.URLError as e:
            raise Exception(f"URL error: {e.reason}")
        except ssl.SSLError as e:
            raise Exception(f"SSL error: {e}")
        except Exception as e:
            raise Exception(f"Download error: {e}")
    
    @staticmethod
    def verify_metadata_capabilities():
        """Verify that all metadata capabilities are working"""
        issues = []
        
        # Check SSL/certifi
        try:
            import certifi
            ssl_context = ssl.create_default_context(cafile=certifi.where())
        except ImportError:
            issues.append("certifi module not available - album art downloads may fail")
        except Exception as e:
            issues.append(f"SSL context creation failed: {e}")
        
        # Check mutagen
        try:
            from mutagen.easyid3 import EasyID3
            from mutagen.id3 import APIC, ID3
        except ImportError as e:
            issues.append(f"mutagen import failed: {e}")
        
        return issues

# Función de utilidad para verificar capacidades al inicio
def check_metadata_dependencies():
    """Check metadata dependencies and print status"""
    issues = MetadataSetter.verify_metadata_capabilities()
    
    if not issues:
        print("✅ Metadata dependencies OK")
        return True
    else:
        print("⚠️ Metadata issues found:")
        for issue in issues:
            print(f"  • {issue}")
        return False