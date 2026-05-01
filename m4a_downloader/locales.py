"""
Módulo para el manejo de idiomas (Internacionalización) en la aplicación.
"""
from PySide6.QtCore import QSettings

TRANSLATIONS = {
    "es": {
        "title": "Harmony",
        "app_subtitle": "Descargador M4A/MP3",
        "spotify_url": "URL de Spotify o YouTube:",
        "paste_url_placeholder": "Pega una canción, álbum, playlist o video...",
        "audio_config": "Configuración de Audio",
        "format": "Formato:",
        "quality": "Calidad:",
        "ffmpeg_available": "FFmpeg: Disponible",
        "ffmpeg_unavailable": "FFmpeg: No disponible",
        "no_conversion": "Sin conversión",
        "output_folder": "Carpeta de destino:",
        "browse": "Buscar",
        "download": "Descargar",
        "cancel": "Cancelar",
        "open": "Abrir",
        "folder_not_found": "Carpeta no encontrada",
        "downloading": "Descargando",
        "preparing_song": "Preparando descarga de canción en {format}...",
        "preparing_playlist": "Preparando descarga de playlist en {format}...",
        "preparing_album": "Preparando descarga de álbum en {format}...",
        "preparing": "Preparando descarga en {format}...",
        "settings": "Configuración",
        
        # Dialogo de Configuración
        "welcome": "¡Bienvenido a Harmony!",
        "initial_setup_subtitle": "Configuración inicial - Credenciales y formato",
        "tab_credentials": "Credenciales",
        "tab_format": "Formato de Audio",
        "tab_settings": "Configuración general",
        "test_credentials": "Test Credenciales",
        "save_continue": "Guardar y Continuar",
        "spotify_welcome": "Harmony descarga desde Spotify y YouTube. Las credenciales solo son necesarias para enlaces de Spotify; YouTube funciona directo.",
        "spotify_instructions": "Crea una aplicación en el Dashboard Developer de Spotify:",
        "open_dashboard": "Abrir Spotify Developer Dashboard",
        "client_id": "Client ID:",
        "client_secret": "Client Secret:",
        "show_secret": "Mostrar Client Secret",
        
        # Opciones Nuevas
        "language": "Idioma (Language):",
        "theme": "Tema:",
        "file_naming": "Plantilla de Archivos:",
        "create_subfolders": "Crear subcarpetas para Álbumes/Playlists",
        "download_lyrics": "Buscar e incrustar letras (Lyrics)",
        
        # Alertas
        "error": "Error",
        "success": "Éxito",
        "enter_url": "Por favor, ingresa una URL de Spotify o YouTube.",
        "invalid_url": "Debe ser una URL válida de Spotify o YouTube.",
        "ffmpeg_missing_warn": "Has seleccionado MP3 pero FFmpeg no está instalado.\n¿Deseas continuar con M4A en su lugar?",
        "cancel_confirm": "¿Estás seguro de que quieres cerrar? La descarga se cancelará.",
        
        # Nombres de Plantillas Visuales
        "naming_default": "Predeterminado: Título",
        "naming_artist_title": "Artista - Título",
        "naming_track_title": "Num - Título",
        
        # Grupos de Configuración
        "appearance_group": "Apariencia e Idioma",
        "files_group": "Archivos y Carpetas",
        "advanced_group": "Avanzado",
        "parallel_downloads": "Descargas Paralelas:",
        "dont_show_startup": "No mostrar configuración al inicio",
        "check_ffmpeg": "Verificar FFmpeg",
        
        # Temas
        "theme_dark_mora": "Mora Oscura (Defecto)",
        "theme_dark_ocean": "Océano Noche",
        "theme_dark_forest": "Bosque Oscuro",
        "theme_dark_neon": "Púrpura Neón",
        "theme_light_snow": "Blanco Nieve",
        "theme_light_sky": "Cielo Claro",
        "theme_light_mint": "Menta Fresca",
        "theme_light_cream": "Crema Suave",
    },
    "en": {
        "title": "Harmony",
        "app_subtitle": "M4A/MP3 Downloader",
        "spotify_url": "Spotify or YouTube URL:",
        "paste_url_placeholder": "Paste a track, album, playlist, or video...",
        "audio_config": "Audio Settings",
        "format": "Format:",
        "quality": "Quality:",
        "ffmpeg_available": "FFmpeg: Available",
        "ffmpeg_unavailable": "FFmpeg: Unavailable",
        "no_conversion": "No conversion",
        "output_folder": "Output folder:",
        "browse": "Browse",
        "download": "Download",
        "cancel": "Cancel",
        "open": "Open",
        "folder_not_found": "Folder not found",
        "downloading": "Downloading",
        "preparing_song": "Preparing track download in {format}...",
        "preparing_playlist": "Preparing playlist download in {format}...",
        "preparing_album": "Preparing album download in {format}...",
        "preparing": "Preparing download in {format}...",
        "settings": "Settings",
        
        # Settings Dialog
        "welcome": "Welcome to Harmony!",
        "initial_setup_subtitle": "Initial Setup - Credentials and audio format",
        "tab_credentials": "Credentials",
        "tab_format": "Audio Format",
        "tab_settings": "General Settings",
        "test_credentials": "Test Credentials",
        "save_continue": "Save & Continue",
        "spotify_welcome": "Harmony downloads from Spotify and YouTube. Credentials are only needed for Spotify links; YouTube works directly.",
        "spotify_instructions": "To use it, create an app in the Spotify Developer dashboard:",
        "open_dashboard": "Open Spotify Developer Dashboard",
        "client_id": "Client ID:",
        "client_secret": "Client Secret:",
        "show_secret": "Show Client Secret",
        
        # New options
        "language": "Language (Idioma):",
        "theme": "Theme:",
        "file_naming": "File Naming Format:",
        "create_subfolders": "Create subfolders for Albums/Playlists",
        "download_lyrics": "Search and embed song Lyrics",
        
        # Alerts
        "error": "Error",
        "success": "Success",
        "enter_url": "Please enter a Spotify or YouTube URL.",
        "invalid_url": "It must be a valid Spotify or YouTube URL.",
        "ffmpeg_missing_warn": "You picked MP3 but FFmpeg is not installed.\nDo you want to continue with M4A instead?",
        "cancel_confirm": "Are you sure you want to close? Download will be canceled.",
        
        # Naming Defaults
        "naming_default": "Default: Title",
        "naming_artist_title": "Artist - Title",
        "naming_track_title": "Track Num - Title",
        
        # Configuration Groups
        "appearance_group": "Appearance & Language",
        "files_group": "Files & Folders",
        "advanced_group": "Advanced Settings",
        "parallel_downloads": "Parallel Downloads:",
        "dont_show_startup": "Don't show config at startup",
        "check_ffmpeg": "Check FFmpeg",
        
        # Themes
        "theme_dark_mora": "Dark Blackberry (Default)",
        "theme_dark_ocean": "Night Ocean",
        "theme_dark_forest": "Dark Forest",
        "theme_dark_neon": "Neon Purple",
        "theme_light_snow": "Snow White",
        "theme_light_sky": "Clear Sky",
        "theme_light_mint": "Fresh Mint",
        "theme_light_cream": "Soft Cream",
    }
}

class Translator:
    def __init__(self):
        # El usuario pidió el default en inglés
        settings = QSettings('MorphyDownloader', 'Config')
        self.language = settings.value('language', 'en')
        if self.language not in TRANSLATIONS:
            self.language = 'en'
            
    def set_language(self, lang_code):
        if lang_code in TRANSLATIONS:
            self.language = lang_code
            settings = QSettings('MorphyDownloader', 'Config')
            settings.setValue('language', lang_code)
            
    def get(self, key, **kwargs):
        lang_dict = TRANSLATIONS.get(self.language, TRANSLATIONS['en'])
        # Si la llave no está, retorna el texto en inglés, si tampoco, retorna la llave a secas.
        text = lang_dict.get(key, TRANSLATIONS['en'].get(key, key))
        if kwargs:
            try:
                return text.format(**kwargs)
            except KeyError:
                return text
        return text

# Instancia global (Singleton)
translator = Translator()

def _(key, **kwargs):
    """Función atajo para invocar el traductor."""
    return translator.get(key, **kwargs)
