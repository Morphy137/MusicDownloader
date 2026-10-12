import pytest
from m4a_downloader.utils import detect_url_source, is_spotify_url, is_youtube_url, is_soundcloud_url, is_search_query
from m4a_downloader.core.youtube_downloader import YouTubeDownloader
from m4a_downloader.core.metadata import MetadataSetter

def test_detect_url_source_spotify():
    track_url = "https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh"
    album_url = "https://open.spotify.com/album/1A2B3C4D5E"
    playlist_url = "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"

    assert detect_url_source(track_url) == "spotify_track"
    assert detect_url_source(album_url) == "spotify_album"
    assert detect_url_source(playlist_url) == "spotify_playlist"
    assert is_spotify_url(track_url) is True

def test_detect_url_source_youtube():
    video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    playlist_url = "https://www.youtube.com/playlist?list=PL1234567890"

    assert detect_url_source(video_url) == "youtube_video"
    assert detect_url_source(playlist_url) == "youtube_playlist"
    assert is_youtube_url(video_url) is True

def test_detect_url_source_soundcloud():
    sc_track = "https://soundcloud.com/octobersveryown/drake-gods-plan"
    sc_set = "https://soundcloud.com/user-12345/sets/my-favorite-tracks"

    assert detect_url_source(sc_track) == "soundcloud_track"
    assert detect_url_source(sc_set) == "soundcloud_playlist"
    assert is_soundcloud_url(sc_track) is True

def test_detect_url_source_search_query():
    query = "Daft Punk One More Time"
    empty = ""

    assert detect_url_source(query) == "search_query"
    assert is_search_query(query) is True
    assert detect_url_source(empty) == "unknown"

def test_youtube_downloader_soundcloud_entries():
    yt = YouTubeDownloader(output_dir="music/tmp")
    entries = yt.get_web_entries("https://soundcloud.com/octobersveryown/drake-gods-plan")

    assert len(entries) == 1
    assert "God's Plan" in entries[0]["title"]
    assert entries[0]["url"].startswith("http")

def test_youtube_downloader_search_entries():
    yt = YouTubeDownloader(output_dir="music/tmp")
    entries = yt.get_web_entries("Daft Punk One More Time")

    assert len(entries) == 1
    assert "One More Time" in entries[0]["title"]

def test_metadata_setter_capabilities():
    issues = MetadataSetter.verify_metadata_capabilities()
    # verify_metadata_capabilities returns a list of issue strings or empty list
    assert isinstance(issues, list)
