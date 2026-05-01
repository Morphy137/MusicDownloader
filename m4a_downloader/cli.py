import typer
from rich.console import Console
from .core.spotify_client import SpotifyClient
from .core.youtube_downloader import YouTubeDownloader
from .core.metadata import MetadataSetter
from .utils import clean_temp_folder, detect_url_source, sanitize_filename_part
from .config import Config
from .gui.config_dialog import get_saved_audio_format, get_saved_audio_quality, get_saved_parallel_downloads
import os
import time
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from PySide6.QtCore import QSettings

def get_formatted_filename(track_info, template, audio_format):
    mapping = {
        "{title}": sanitize_filename_part(track_info.get('track_title', 'Unknown')) or "Unknown",
        "{artist}": sanitize_filename_part(track_info.get('artist_name', 'Unknown')) or "Unknown",
        "{album}": sanitize_filename_part(track_info.get('album_name', 'Unknown')) or "Unknown",
        "{track_number}": f"{track_info.get('track_number', 0):02d}",
        "{ext}": audio_format
    }
    filename = template
    for k, v in mapping.items():
        filename = filename.replace(k, v)
    return filename

app = typer.Typer()
console = Console()

@app.command()
def download_cli(
    url: str = typer.Option(..., "--url", "-u", help="URL de Spotify o YouTube"),
    output: str = typer.Option("music", help="Directorio de salida"),
    format: str = typer.Option(None, "--format", "-f", help="Formato de audio (m4a/mp3)"),
    quality: str = typer.Option(None, "--quality", "-q", help="Calidad de audio para MP3 (128/192/256/320)"),
    parallel: int = typer.Option(None, "--parallel", "-p", help="Número de descargas paralelas (1-8)")
):
    """Descarga canciones, videos o playlists de Spotify/YouTube como M4A o MP3 (CLI)."""
    return download(url, output, format, quality, parallel)

def download(url, output="music", audio_format=None, quality=None, parallel=None, progress_callback=None, log_callback=None):
    """Función principal de descarga - Mejorada con soporte MP3/M4A y descargas paralelas configurables"""
    
    def log(msg, level="info"):
        if log_callback:
            log_callback(msg, level)
        else:
            encoding = getattr(console.file, "encoding", None) or "utf-8"
            msg = str(msg).encode(encoding, errors="replace").decode(encoding, errors="replace")
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
        
        source_type = detect_url_source(url)
        if source_type == "unknown":
            raise ValueError("URL no reconocida. Usa una URL de Spotify o YouTube válida.")
        
        # Determinar tipo de contenido y obtener datos
        playlist_folder = output
        is_playlist = False
        
        settings = QSettings('MorphyDownloader', 'Config')
        create_subfolders = settings.value('create_subfolders', False, type=bool)
        naming_format = settings.value('naming_format', '{title}.{ext}')
        
        if source_type.startswith("spotify"):
            spotify = SpotifyClient()

        if source_type == "spotify_track":
            log("🎵 Obteniendo información de la canción...")
            songs = [spotify.get_track_info(url)]
            if create_subfolders:
                safe_album = sanitize_filename_part(songs[0].get('album_name', 'Tracks')) or "Tracks"
                playlist_folder = os.path.join(output, safe_album)
        elif source_type == "spotify_album":
            log("💿 Obteniendo información del álbum...")
            is_playlist = True
            playlist_name, songs = spotify.get_album_tracks(url)
            if create_subfolders:
                safe_name = sanitize_filename_part(playlist_name) or "Album"
                playlist_folder = os.path.join(output, safe_name)
        elif source_type == "spotify_playlist":
            log("📋 Obteniendo información de la playlist...")
            is_playlist = True
            playlist_name, songs = spotify.get_playlist_tracks(url)
            if create_subfolders:
                safe_name = sanitize_filename_part(playlist_name) or "Playlist"
                playlist_folder = os.path.join(output, safe_name)
        elif source_type.startswith("youtube"):
            log("▶️ Analizando URL de YouTube...")
            yt_probe = YouTubeDownloader(
                output_dir=output,
                quality=quality,
                audio_format=audio_format
            )
            entries = yt_probe.get_youtube_entries(url)
            is_playlist = len(entries) > 1 or source_type == "youtube_playlist"
            playlist_name = entries[0].get("playlist_title") or "YouTube"
            if is_playlist and create_subfolders:
                safe_name = sanitize_filename_part(playlist_name) or "YouTube Playlist"
                playlist_folder = os.path.join(output, safe_name)
            songs = entries
            if is_playlist:
                log(f"📋 Playlist de YouTube detectada: {len(songs)} video(s)")
            else:
                log("🎬 Video de YouTube detectado")
        else:
            raise ValueError("Tipo de URL no soportado")
        
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
        
        # Descargar una sola canción
        def get_available_destination(destination):
            if not os.path.exists(destination):
                return destination
            base, ext = os.path.splitext(destination)
            counter = 2
            while True:
                candidate = f"{base} ({counter}){ext}"
                if not os.path.exists(candidate):
                    return candidate
                counter += 1

        def download_spotify_song(track_info, i):
            expected_name = get_formatted_filename(track_info, naming_format, audio_format)
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

        def download_youtube_item(entry, i):
            try:
                log(f"({i}/{total}) Leyendo metadata de YouTube: {entry.get('title', 'Video')}")
                track_info = yt_downloader.get_youtube_metadata(
                    entry["url"],
                    track_number=entry.get("track_number", i),
                    playlist_title=entry.get("playlist_title", "")
                )
                expected_name = get_formatted_filename(track_info, naming_format, audio_format)
                destination = os.path.join(playlist_folder, expected_name)

                if os.path.exists(destination):
                    log(f"({i}/{total}) {expected_name} ya existe. Saltando...", "warning")
                    return 0

                log(f"({i}/{total}) Descargando video de YouTube...")
                audio_file = yt_downloader.download_audio(entry["url"], playlist=False)

                if audio_file and os.path.exists(audio_file):
                    try:
                        MetadataSetter.set_metadata(track_info, audio_file)
                        log(f"({i}/{total}) Metadatos de YouTube aplicados")
                    except Exception as e:
                        log(f"({i}/{total}) Warning: Error aplicando metadatos: {e}", "warning")

                    final_destination = get_available_destination(destination)
                    if os.path.abspath(audio_file) != os.path.abspath(final_destination):
                        os.replace(audio_file, final_destination)

                    log(f"✅ Descargado: {os.path.basename(final_destination)}", "success")
                    return 1

                log(f"❌ Error descargando {entry.get('title', 'video')}", "error")
                return 0

            except Exception as e:
                log(f"❌ Error en {entry.get('title', 'video')}: {e}", "error")
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
                worker_func = download_youtube_item if source_type.startswith("youtube") else download_spotify_song
                futures.append(executor.submit(worker_func, track_info, i))
            
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
