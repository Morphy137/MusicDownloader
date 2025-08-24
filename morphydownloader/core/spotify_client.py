"""Spotify API interaction module"""
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

class SpotifyClient:
    def __init__(self):
        self.client_id = os.getenv("SPOTIPY_CLIENT_ID")
        self.client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
        
        if not self.client_id or not self.client_secret:
            raise EnvironmentError(
                "Missing Spotify API credentials. "
                "Set SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET."
            )
            
        self.sp = spotipy.Spotify(
            client_credentials_manager=SpotifyClientCredentials(
                client_id=self.client_id, 
                client_secret=self.client_secret
            )
        )

    def get_track_info(self, track_url: str) -> Dict[str, str]:
        """Get track information from Spotify"""
        try:
            track = self.sp.track(track_url)
            
            # Safe access to album art
            album_art = ""
            if track["album"]["images"]:
                # Prefer medium size (index 1), fallback to any available
                album_art = (track["album"]["images"][1]["url"] 
                           if len(track["album"]["images"]) > 1 
                           else track["album"]["images"][0]["url"])
            
            return {
                "artist_name": track["artists"][0]["name"],
                "track_title": track["name"],
                "track_number": track["track_number"],
                "isrc": track["external_ids"].get("isrc", ""),
                "album_art": album_art,
                "album_name": track["album"]["name"],
                "release_date": track["album"]["release_date"],
                "artists": [artist["name"] for artist in track["artists"]],
            }
        except Exception as e:
            logger.error(f"Failed to get track info: {e}")
            raise

    def get_playlist_tracks(self, playlist_url: str) -> Tuple[str, List[Dict]]:
        """Get all tracks from a Spotify playlist"""
        try:
            pl = self.sp.playlist(playlist_url)
            
            # Check if playlist is accessible
            if not pl.get("public", True) and not pl.get("collaborative", False):
                raise ValueError("Playlist is private and not accessible.")
            
            playlist_name = pl.get("name", "Unnamed Playlist")
            
            # Get all tracks (handle pagination)
            tracks = []
            results = self.sp.playlist_tracks(playlist_url)
            
            while results:
                tracks.extend([item["track"] for item in results["items"] if item["track"]])
                results = self.sp.next(results) if results['next'] else None
            
            track_infos = []
            for track in tracks:
                try:
                    track_info = self.get_track_info(f"https://open.spotify.com/track/{track['id']}")
                    track_infos.append(track_info)
                except Exception as e:
                    logger.warning(f"Failed to get info for track {track.get('name', 'Unknown')}: {e}")
                    continue
            
            return playlist_name, track_infos
            
        except Exception as e:
            logger.error(f"Failed to get playlist tracks: {e}")
            raise