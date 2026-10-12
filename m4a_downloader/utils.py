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

SOUNDCLOUD_HOSTS = {
    "soundcloud.com",
    "www.soundcloud.com",
    "m.soundcloud.com",
    "on.soundcloud.com",
}


def detect_url_source(url):
    """Return a stable content type for supported Spotify, YouTube, SoundCloud URLs or plain search queries."""
    text = url.strip()
    if not text:
        return "unknown"

    parsed = urlparse(text if "://" in text else f"https://{text}" if any(text.startswith(h) for h in YOUTUBE_HOSTS | SOUNDCLOUD_HOSTS | {"spotify.com", "open.spotify.com"}) else text)
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

    if any(sc_host in host for sc_host in SOUNDCLOUD_HOSTS):
        if "/sets/" in path:
            return "soundcloud_playlist"
        segments = [s for s in path.split("/") if s]
        if len(segments) >= 2:
            return "soundcloud_track"
        return "soundcloud"

    # If text is not an HTTP URL or known domain, treat as plain search query
    if not text.startswith("http://") and not text.startswith("https://"):
        return "search_query"

    return "unknown"


def is_spotify_url(url):
    return detect_url_source(url).startswith("spotify")


def is_youtube_url(url):
    return detect_url_source(url).startswith("youtube")


def is_soundcloud_url(url):
    return detect_url_source(url).startswith("soundcloud")


def is_search_query(url):
    return detect_url_source(url) == "search_query"


def sanitize_filename_part(value):
    return "".join(ch for ch in str(value) if ch not in '\\/:*?"<>|').strip()
