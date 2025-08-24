"""Spotify API interaction module - Optimized version"""
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

class SpotifyClient:
    def __init__(self):
        """Inicialización optimizada - NO crear conexión hasta que sea necesaria"""
        self.client_id = os.getenv("SPOTIPY_CLIENT_ID")
        self.client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
        
        if not self.client_id or not self.client_secret:
            raise EnvironmentError(
                "Missing Spotify API credentials. "
                "Set SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET environment variables."
            )
        
        # NO inicializar spotipy aquí - lazy loading
        self._sp = None
    
    @property 
    def sp(self):
        """Lazy loading de la conexión Spotify"""
        if self._sp is None:
            try:
                logger.debug("Iniciando conexión con Spotify API...")
                
                # Configuración optimizada para conexión rápida
                client_credentials_manager = SpotifyClientCredentials(
                    client_id=self.client_id, 
                    client_secret=self.client_secret
                )
                
                self._sp = spotipy.Spotify(
                    client_credentials_manager=client_credentials_manager,
                    requests_timeout=10,  # Timeout más corto
                    retries=1,           # Menos reintentos
                )
                
                logger.debug("✅ Conexión con Spotify establecida")
                
            except Exception as e:
                logger.error(f"Error conectando con Spotify: {e}")
                raise Exception(f"No se pudo conectar con Spotify API: {e}")
        
        return self._sp

    def get_track_info(self, track_url: str) -> Dict[str, str]:
        """Get track information from Spotify - Con mejor logging"""
        try:
            logger.debug(f"Obteniendo información de track: {track_url}")
            
            track = self.sp.track(track_url)
            
            # Safe access to album art
            album_art = ""
            if track["album"]["images"]:
                # Prefer medium size (index 1), fallback to any available
                album_art = (track["album"]["images"][1]["url"] 
                           if len(track["album"]["images"]) > 1 
                           else track["album"]["images"][0]["url"])
            
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
            
            logger.debug(f"✅ Track obtenido: {track_info['track_title']} - {track_info['artist_name']}")
            return track_info
            
        except spotipy.exceptions.SpotifyException as e:
            if e.http_status == 404:
                raise ValueError(f"Track no encontrado: {track_url}")
            elif e.http_status == 401:
                raise ValueError("Credenciales de Spotify inválidas")
            else:
                raise ValueError(f"Error de Spotify API: {e}")
        except Exception as e:
            logger.error(f"Error obteniendo track info: {e}")
            raise ValueError(f"Error obteniendo información del track: {e}")

    def get_playlist_tracks(self, playlist_url: str) -> Tuple[str, List[Dict]]:
        """Get all tracks from a Spotify playlist - Optimized"""
        try:
            logger.debug(f"Obteniendo playlist: {playlist_url}")
            
            pl = self.sp.playlist(playlist_url, fields="name,public,collaborative,tracks.total")
            
            # Check if playlist is accessible
            if not pl.get("public", True) and not pl.get("collaborative", False):
                raise ValueError("La playlist es privada y no es accesible.")
            
            playlist_name = pl.get("name", "Unnamed Playlist")
            total_tracks = pl["tracks"]["total"]
            
            logger.debug(f"📋 Playlist '{playlist_name}' tiene {total_tracks} tracks")
            
            # Get all tracks with pagination (optimized)
            tracks = []
            offset = 0
            limit = 100  # Máximo permitido por Spotify
            
            while offset < total_tracks:
                logger.debug(f"Obteniendo tracks {offset}-{min(offset + limit, total_tracks)}")
                
                results = self.sp.playlist_tracks(
                    playlist_url, 
                    offset=offset, 
                    limit=limit,
                    fields="items.track(id,name,artists,album,external_ids,track_number)"
                )
                
                batch_tracks = [item["track"] for item in results["items"] if item["track"]]
                tracks.extend(batch_tracks)
                
                if len(results["items"]) < limit:
                    break
                    
                offset += limit
            
            logger.debug(f"✅ Obtenidos {len(tracks)} tracks de la playlist")
            
            # Convert to track info format
            track_infos = []
            for i, track in enumerate(tracks, 1):
                try:
                    # Usar información ya obtenida en lugar de hacer llamadas individuales
                    album_art = ""
                    if track["album"]["images"]:
                        album_art = (track["album"]["images"][1]["url"] 
                                   if len(track["album"]["images"]) > 1 
                                   else track["album"]["images"][0]["url"])
                    
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
                    
                    if i % 10 == 0:  # Log cada 10 tracks
                        logger.debug(f"Procesados {i}/{len(tracks)} tracks")
                        
                except Exception as e:
                    logger.warning(f"Error procesando track {track.get('name', 'Unknown')}: {e}")
                    continue
            
            logger.debug(f"✅ Playlist procesada: {len(track_infos)} tracks listos")
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