"""MP3 metadata setter module"""
import urllib.request
from mutagen.easyid3 import EasyID3
from mutagen.id3 import APIC, ID3

class MetadataSetter:
    @staticmethod
    def set_metadata(metadata, file_path):
        mp3file = EasyID3(file_path)
        mp3file.update({
            "albumartist": metadata["artist_name"],
            "artist": ", ".join(metadata["artists"]),
            "album": metadata["album_name"],
            "title": metadata["track_title"],
            "date": metadata["release_date"],
            "tracknumber": str(metadata["track_number"]),
            "isrc": metadata["isrc"],
        })
        mp3file.save()
        with urllib.request.urlopen(metadata["album_art"]) as albumart:
            audio = ID3(file_path)
            audio["APIC"] = APIC(
                encoding=3, mime="image/jpeg", type=3, desc="Cover", data=albumart.read())
            audio.save()
