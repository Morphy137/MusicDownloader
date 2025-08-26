import typer
from rich.console import Console
from .core.spotify_client import SpotifyClient
from .core.youtube_downloader import YouTubeDownloader
from .core.metadata import MetadataSetter
from .utils import clean_temp_folder
import os
import time
import re
from concurrent.futures import ThreadPoolExecutor, as_completed  # Nuevo import para paralelización

app = typer.Typer()
console = Console()

@app.command()
def download_cli(
    url: str = typer.Option(..., "--url", "-u", help="URL de Spotify (track o playlist)"),
    output: str = typer.Option("music", help="Directorio de salida")
):
    """Descarga canciones o playlists de Spotify como m4a (CLI)."""
    return download(url, output)

def download(url, output="music", progress_callback=None, log_callback=None):
    """Función principal de descarga - Mejorada con mejor búsqueda en YouTube"""
    
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
        
        yt_downloader = YouTubeDownloader(output_dir=temp_dir)
        
        log(f"🚀 Iniciando descarga de {len(songs)} canción(es)...")
        
        start_time = time.time()
        downloaded = 0
        total = len(songs)
        
        # descargar una sola canción (para paralelización)
        def download_song(track_info, i):
            title = re.sub(r'[\\/:*?"<>|]', '', track_info['track_title'])
            artist = re.sub(r'[\\/:*?"<>|]', '', track_info['artist_name'])
            expected_name = f"{title} - {artist}.m4a"  # Cambia a .mp3 si usas MP3
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
                    MetadataSetter.set_metadata(track_info, audio_file)
                    
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
        
        # Paralelización: Usar ThreadPoolExecutor con max_workers=2
        with ThreadPoolExecutor(max_workers=2) as executor:
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
        log(f"✅ COMPLETADO: {downloaded}/{len(songs)} canción(es) descargada(s)", "success")
        log(f"⏱️ Tiempo total: {round(end_time - start_time)} segundos")
        
    except Exception as e:
        log(f"❌ Error fatal: {e}", "error")
        raise

if __name__ == "__main__":
    app()