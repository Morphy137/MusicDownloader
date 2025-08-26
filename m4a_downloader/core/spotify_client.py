"""Spotify API interaction module - Optimized version"""
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

class SpotifyClient:
    def __init__(self):
        """Inicialización optimizada - Conexión inmediata y rápida"""
        self.client_id = os.getenv("SPOTIPY_CLIENT_ID")
        self.client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
        
        if not self.client_id or not self.client_secret:
            raise EnvironmentError(
                "Missing Spotify API credentials. "
                "Set SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET environment variables."
            )
        
        # Crear conexión inmediatamente con configuración optimizada
        try:
            client_credentials_manager = SpotifyClientCredentials(
                client_id=self.client_id, 
                client_secret=self.client_secret
            )
            
            self.sp = spotipy.Spotify(
                client_credentials_manager=client_credentials_manager,
                requests_timeout=5,    # Timeout muy corto
                retries=0,            # Sin reintentos para conexión rápida
            )
            
            # Test inmediato de conexión
            self.sp.search(q="test", type="track", limit=1)
            logger.debug("✅ Conexión con Spotify establecida")
            
        except Exception as e:
            logger.error(f"Error conectando con Spotify: {e}")
            raise Exception(f"No se pudo conectar con Spotify API: {e}")

    def get_track_info(self, track_url: str) -> Dict[str, str]:
        """Get track information from Spotify - Optimizado"""
        try:
            track = self.sp.track(track_url)
            
            # Acceso optimizado a album art
            album_art = ""
            if track["album"]["images"]:
                album_art = track["album"]["images"][0]["url"]  # Usar primera imagen disponible
            
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
            
        except spotipy.exceptions.SpotifyException as e:
            if e.http_status == 404:
                raise ValueError(f"Track no encontrado: {track_url}")
            elif e.http_status == 401:
                raise ValueError("Credenciales de Spotify inválidas")
            else:
                raise ValueError(f"Error de Spotify API: {e}")

    def get_playlist_tracks(self, playlist_url: str) -> Tuple[str, List[Dict]]:
        """Get all tracks from a Spotify playlist - Ultra optimizado"""
        try:
            # Obtener info básica de playlist
            pl = self.sp.playlist(playlist_url, fields="name,tracks.total")
            playlist_name = pl.get("name", "Unnamed Playlist")
            total_tracks = pl["tracks"]["total"]
            
            logger.debug(f"📋 Playlist '{playlist_name}' tiene {total_tracks} tracks")
            
            # Obtener TODOS los tracks de una vez con campos mínimos necesarios
            tracks = []
            offset = 0
            limit = 100  # Máximo permitido
            
            while offset < total_tracks:
                results = self.sp.playlist_tracks(
                    playlist_url, 
                    offset=offset, 
                    limit=limit,
                    fields="items.track(name,artists,album(name,release_date,images),external_ids,track_number)"
                )
                
                batch_tracks = [item["track"] for item in results["items"] if item["track"]]
                tracks.extend(batch_tracks)
                
                if len(results["items"]) < limit:
                    break
                    
                offset += limit
            
            # Convertir todo de una vez sin logs innecesarios
            track_infos = []
            for track in tracks:
                try:
                    album_art = ""
                    if track["album"]["images"]:
                        album_art = track["album"]["images"][0]["url"]
                    
                    track_info = {
                        "artist_name": track["artists"][0]["name"],
                        "track_title": track["name"],
                        "track_number": track["track_number"],
                        "isrc": track["external_ids"].get("isrc", ""),
                        "album_art": album_art,
                        "album_name": track["album"]["name"],
                        "release_date": track["album"]["release_date"],
                        "artists": [artist["name"] for artist in track["artists"]],
                    }
                    
                    track_infos.append(track_info)
                        
                except Exception as e:
                    logger.warning(f"Error procesando track {track.get('name', 'Unknown')}: {e}")
                    continue
            
            logger.debug(f"✅ {len(track_infos)} tracks procesados")
            return playlist_name, track_infos
            
        except spotipy.exceptions.SpotifyException as e:
            if e.http_status == 404:
                raise ValueError(f"Playlist no encontrada: {playlist_url}")
            elif e.http_status == 401:
                raise ValueError("Credenciales de Spotify inválidas")
            else:
                raise ValueError(f"Error de Spotify API: {e}")
        except Exception as e:
            logger.error(f"Error obteniendo playlist: {e}")
            raise ValueError(f"Error obteniendo playlist: {e}")