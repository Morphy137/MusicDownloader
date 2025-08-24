"""
Core modules for MorphyDownloader
"""

from .spotify_client import SpotifyClient
from .youtube_downloader import YouTubeDownloader
from .metadata import MetadataSetter

__all__ = ['SpotifyClient', 'YouTubeDownloader', 'MetadataSetter']