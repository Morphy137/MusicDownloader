import os
import shutil
from urllib.parse import parse_qs, urlparse

def clean_temp_folder(folder):
    if os.path.exists(folder):
        shutil.rmtree(folder)


YOUTUBE_HOSTS = {
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "music.youtube.com",
    "youtu.be",
}


def detect_url_source(url):
    """Return a stable content type for supported Spotify and YouTube URLs."""
    parsed = urlparse(url.strip())
    host = parsed.netloc.lower()
    path = parsed.path.lower()
    query = parse_qs(parsed.query)

    if "spotify.com" in host or host == "spoti.fi":
        if "/track/" in path:
            return "spotify_track"
        if "/album/" in path:
            return "spotify_album"
        if "/playlist/" in path:
            return "spotify_playlist"
        return "spotify"

    if host in YOUTUBE_HOSTS:
        if "list" in query or path.startswith("/playlist"):
            return "youtube_playlist"
        if host == "youtu.be" or "v" in query or path.startswith("/shorts/"):
            return "youtube_video"
        return "youtube"

    return "unknown"


def is_spotify_url(url):
    return detect_url_source(url).startswith("spotify")


def is_youtube_url(url):
    return detect_url_source(url).startswith("youtube")


def sanitize_filename_part(value):
    return "".join(ch for ch in str(value) if ch not in '\\/:*?"<>|').strip()
