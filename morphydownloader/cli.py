import typer
from rich.console import Console
from .core.spotify_client import SpotifyClient
from .core.youtube_downloader import YouTubeDownloader
from .core.metadata import MetadataSetter
from .utils import clean_temp_folder
import os
import time

app = typer.Typer()
console = Console()


# --- CLI Typer command (mantener para terminal) ---
@app.command()
def download_cli(
    url: str = typer.Option(..., "--url", "-u", help="URL de Spotify (track o playlist)"),
    output: str = typer.Option("music", help="Directorio de salida")
):
    """Descarga canciones o playlists de Spotify como mp3 (CLI)."""
    return download(url, output)

# --- Función normal para GUI y otros usos ---
def download(
    url,
    output="music",
    progress_callback=None,
    log_callback=None
):
    """Descarga canciones o playlists de Spotify como mp3."""
    spotify = SpotifyClient()
    playlist_folder = output
    is_playlist = False
    if "track" in url:
        songs = [spotify.get_track_info(url)]
    else:
        is_playlist = True
        playlist_name, songs = spotify.get_playlist_tracks(url)
        # Sanitizar nombre de carpeta
        import re
        safe_name = re.sub(r'[^\u0000-\u007f\w\-\s\.]', '', playlist_name).strip()
        playlist_folder = os.path.join(output, safe_name)
    yt_downloader = YouTubeDownloader(output_dir=os.path.join(playlist_folder, "tmp"))
    os.makedirs(playlist_folder, exist_ok=True)
    start_time = time.time()
    downloaded = 0
    import re
    total = len(songs)
    def log(msg, level="info"):
        if log_callback:
            log_callback(msg, level)
        else:
            if level == "error":
                console.print(f"[red]{msg}[/red]")
            elif level == "success":
                console.print(f"[green]{msg}[/green]")
            elif level == "warning":
                console.print(f"[yellow]{msg}[/yellow]")
            else:
                console.print(msg)
    for i, track_info in enumerate(songs, start=1):
        # Formato consistente: "Título - Artista.mp3"
        title = re.sub(r'[\\/:*?"<>|]', '', track_info['track_title'])
        artist = re.sub(r'[\\/:*?"<>|]', '', track_info['artist_name'])
        expected_name = f"{title} - {artist}.mp3"
        destination = os.path.join(playlist_folder, expected_name)
        if os.path.exists(destination):
            log(f"({i}/{total}) {expected_name} ya existe. Saltando...", level="warning")
            if progress_callback:
                progress_callback(i, total)
            continue
        # Término de búsqueda: "Título Artista audio"
        search_term = f"{track_info['track_title']} {track_info['artist_name']} audio"
        try:
            video_link = yt_downloader.find_youtube(search_term)
            log(f"({i}/{len(songs)}) Descargando '{track_info['track_title']} - {track_info['artist_name']}'...")
            audio = yt_downloader.download_audio(video_link)
            if audio:
                MetadataSetter.set_metadata(track_info, audio)
                # Renombrar el archivo descargado si es necesario
                if os.path.abspath(audio) != os.path.abspath(destination):
                    os.replace(audio, destination)
                downloaded += 1
                log(f"Descargado: {expected_name}", level="success")
            else:
                log("El archivo ya existe. Saltando...", level="warning")
            if progress_callback:
                progress_callback(i, total)
        except Exception as e:
            log(f"Error en {track_info['track_title']}: {e}", level="error")
            if progress_callback:
                progress_callback(i, total)
    clean_temp_folder(os.path.join(playlist_folder, "tmp"))
    end_time = time.time()
    log(f"\nUbicación de descarga: {os.path.abspath(playlist_folder)}\n")
    log(f"DESCARGA COMPLETADA: {downloaded}/{len(songs)} canción(es) descargada(s).", level="success")
    log(f"Tiempo total tomado: {round(end_time - start_time)} segundos")

if __name__ == "__main__":
    app()
