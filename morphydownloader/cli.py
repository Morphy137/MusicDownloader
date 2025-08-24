import typer
from rich.console import Console
from .core.spotify_client import SpotifyClient
from .core.youtube_downloader import YouTubeDownloader
from .core.metadata import MetadataSetter
from .utils import clean_temp_folder
import os
import time
import re

app = typer.Typer()
console = Console()

@app.command()
def download_cli(
    url: str = typer.Option(..., "--url", "-u", help="URL de Spotify (track o playlist)"),
    output: str = typer.Option("music", help="Directorio de salida")
):
    """Descarga canciones o playlists de Spotify como mp3 (CLI)."""
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
        
        for i, track_info in enumerate(songs, start=1):
            # Formato de archivo: "Título - Artista.mp3"
            title = re.sub(r'[\\/:*?"<>|]', '', track_info['track_title'])
            artist = re.sub(r'[\\/:*?"<>|]', '', track_info['artist_name'])
            expected_name = f"{title} - {artist}.mp3"
            destination = os.path.join(playlist_folder, expected_name)
            
            # Skip si ya existe
            if os.path.exists(destination):
                log(f"({i}/{total}) {expected_name} ya existe. Saltando...", "warning")
                if progress_callback:
                    progress_callback(i, total)
                continue
            
            try:
                # Mejorada: Pasar toda la información del track
                log(f"({i}/{total}) Buscando '{track_info['track_title']} - {track_info['artist_name']}'...")
                
                # Buscar en YouTube con información completa
                video_link = yt_downloader.find_youtube(track_info)
                
                log(f"({i}/{total}) Descargando desde YouTube...")
                audio_file = yt_downloader.download_audio(video_link)
                
                if audio_file and os.path.exists(audio_file):
                    # Aplicar metadatos
                    MetadataSetter.set_metadata(track_info, audio_file)
                    
                    # Mover archivo final
                    if os.path.abspath(audio_file) != os.path.abspath(destination):
                        os.replace(audio_file, destination)
                    
                    downloaded += 1
                    log(f"✅ Descargado: {expected_name}", "success")
                else:
                    log(f"❌ Error descargando {track_info['track_title']}", "error")
                
                if progress_callback:
                    progress_callback(i, total)
                    
            except Exception as e:
                log(f"❌ Error en {track_info['track_title']}: {e}", "error")
                if progress_callback:
                    progress_callback(i, total)
                continue
        
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