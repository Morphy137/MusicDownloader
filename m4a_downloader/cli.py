import typer
from rich.console import Console
from .core.spotify_client import SpotifyClient
from .core.youtube_downloader import YouTubeDownloader
from .core.metadata import MetadataSetter
from .utils import clean_temp_folder
from .config import Config
from .gui.config_dialog import get_saved_audio_format, get_saved_audio_quality, get_saved_parallel_downloads
import os
import time
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

app = typer.Typer()
console = Console()

@app.command()
def download_cli(
    url: str = typer.Option(..., "--url", "-u", help="URL de Spotify (track o playlist)"),
    output: str = typer.Option("music", help="Directorio de salida"),
    format: str = typer.Option(None, "--format", "-f", help="Formato de audio (m4a/mp3)"),
    quality: str = typer.Option(None, "--quality", "-q", help="Calidad de audio para MP3 (128/192/256/320)"),
    parallel: int = typer.Option(None, "--parallel", "-p", help="Número de descargas paralelas (1-8)")
):
    """Descarga canciones o playlists de Spotify como M4A o MP3 (CLI)."""
    return download(url, output, format, quality, parallel)

def download(url, output="music", audio_format=None, quality=None, parallel=None, progress_callback=None, log_callback=None):
    """Función principal de descarga - Mejorada con soporte MP3/M4A y descargas paralelas configurables"""
    
    def log(msg, level="info"):
        if log_callback:
            log_callback(msg, level)
        else:
            colors = {
                "error": "[red]", 
                "success": "[green]", 
                "warning": "[yellow]",
                "info": ""
            }
            end_color = "[/red]" if level == "error" else "[/green]" if level == "success" else "[/yellow]" if level == "warning" else ""
            console.print(f"{colors.get(level, '')}{msg}{end_color}")
    
    try:
        # Determinar formato, calidad y paralelismo
        if not audio_format:
            audio_format = get_saved_audio_format()
        if not quality:
            quality = get_saved_audio_quality()
        if not parallel:
            parallel = get_saved_parallel_downloads()
            
        # Validar formato
        if audio_format not in Config.SUPPORTED_FORMATS:
            audio_format = Config.DEFAULT_FORMAT
            log(f"Formato no válido, usando: {audio_format}", "warning")
            
        # Validar calidad
        if quality not in Config.SUPPORTED_QUALITY:
            quality = Config.DEFAULT_QUALITY
            log(f"Calidad no válida, usando: {quality}", "warning")
            
        # Validar paralelismo
        if not isinstance(parallel, int) or not (1 <= parallel <= 8):
            parallel = 2
            log(f"Número de descargas paralelas no válido, usando: {parallel}", "warning")
            
        # Verificar FFmpeg si se necesita MP3
        if audio_format == 'mp3':
            if Config.check_ffmpeg():
                log(f"FFmpeg encontrado: {Config.get_ffmpeg_path()}", "success")
            else:
                log("FFmpeg no encontrado, cambiando a M4A", "warning")
                audio_format = 'm4a'
        
        format_info = Config.get_format_info(audio_format)
        log(f"Configuración: {audio_format.upper()} - {quality} kbps - {parallel} descargas paralelas", "info")
        log(f"Descripción: {format_info['description']}", "info")
        
        # Inicializar cliente Spotify
        spotify = SpotifyClient()
        
        # Determinar tipo de contenido y obtener datos
        playlist_folder = output
        is_playlist = False
        
        if "track" in url:
            log("🎵 Obteniendo información de la canción...")
            songs = [spotify.get_track_info(url)]
        else:
            log("📋 Obteniendo información de la playlist...")
            is_playlist = True
            playlist_name, songs = spotify.get_playlist_tracks(url)
            # Limpiar nombre de carpeta
            safe_name = re.sub(r'[^\w\-\s\.]', '', playlist_name).strip()
            playlist_folder = os.path.join(output, safe_name)
        
        # Configurar directorios
        temp_dir = os.path.join(playlist_folder, "tmp")
        os.makedirs(playlist_folder, exist_ok=True)
        
        # Inicializar descargador de YouTube con formato y calidad
        yt_downloader = YouTubeDownloader(
            output_dir=temp_dir, 
            quality=quality,
            audio_format=audio_format
        )
        
        log(f"🚀 Iniciando descarga de {len(songs)} canción(es) en formato {audio_format.upper()} con {parallel} descargas paralelas...")
        
        start_time = time.time()
        downloaded = 0
        total = len(songs)
        
        # Descargar una sola canción (para paralelización)
        def download_song(track_info, i):
            title = re.sub(r'[\\/:*?"<>|]', '', track_info['track_title'])
            artist = re.sub(r'[\\/:*?"<>|]', '', track_info['artist_name'])
            expected_name = f"{title} - {artist}.{audio_format}"
            destination = os.path.join(playlist_folder, expected_name)
            
            # Skip si ya existe
            if os.path.exists(destination):
                log(f"({i}/{total}) {expected_name} ya existe. Saltando...", "warning")
                if progress_callback:
                    progress_callback(i, total)
                return 0  # No descargada
            
            try:
                log(f"({i}/{total}) Buscando '{track_info['track_title']} - {track_info['artist_name']}'...")
                video_link = yt_downloader.find_youtube(track_info)
                
                log(f"({i}/{total}) Descargando desde YouTube...")
                audio_file = yt_downloader.download_audio(video_link)
                
                if audio_file and os.path.exists(audio_file):
                    # Aplicar metadatos
                    try:
                        MetadataSetter.set_metadata(track_info, audio_file)
                        log(f"({i}/{total}) Metadatos aplicados correctamente")
                    except Exception as e:
                        log(f"({i}/{total}) Warning: Error aplicando metadatos: {e}", "warning")
                    
                    # Mover archivo final
                    if os.path.abspath(audio_file) != os.path.abspath(destination):
                        os.replace(audio_file, destination)
                    
                    log(f"✅ Descargado: {expected_name}", "success")
                    return 1  # Descargada exitosamente
                else:
                    log(f"❌ Error descargando {track_info['track_title']}", "error")
                    return 0
                
            except Exception as e:
                log(f"❌ Error en {track_info['track_title']}: {e}", "error")
                return 0
            
            finally:
                if progress_callback:
                    progress_callback(i, total)
        
        # Paralelización: Usar ThreadPoolExecutor con max_workers configurables
        max_workers = min(parallel, len(songs))  # No usar más workers que canciones
        
        log(f"🔧 Usando {max_workers} workers para descargas paralelas", "info")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for i, track_info in enumerate(songs, start=1):
                futures.append(executor.submit(download_song, track_info, i))
            
            for future in as_completed(futures):
                downloaded += future.result() or 0  # Sumar descargas exitosas
        
        # Limpieza final
        clean_temp_folder(temp_dir)
        end_time = time.time()
        
        # Resultados finales
        log(f"\n📁 Ubicación: {os.path.abspath(playlist_folder)}")
        log(f"✅ COMPLETADO: {downloaded}/{len(songs)} canción(es) descargada(s) en formato {audio_format.upper()}", "success")
        log(f"⏱️ Tiempo total: {round(end_time - start_time)} segundos")
        log(f"🚀 Descargas paralelas utilizadas: {max_workers}")
        
        if audio_format == 'mp3' and downloaded > 0:
            log(f"🔧 Conversiones MP3 realizadas con FFmpeg", "info")
        
        # Estadísticas de rendimiento
        if downloaded > 0:
            avg_time_per_song = (end_time - start_time) / downloaded
            log(f"📊 Tiempo promedio por canción: {avg_time_per_song:.1f} segundos", "info")
        
    except Exception as e:
        log(f"❌ Error fatal: {e}", "error")
        raise

if __name__ == "__main__":
    app()