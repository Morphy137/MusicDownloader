# MorphyDownloader

MorphyDownloader es una aplicación moderna para descargar canciones, álbumes o playlists de Spotify en formato MP3, obteniendo el audio desde YouTube y añadiendo metadatos completos automáticamente. Incluye tanto una interfaz gráfica (GUI) intuitiva como una potente línea de comandos (CLI).

---

## ¿Cómo funciona?

1. Obtiene la información de canciones, álbumes o playlists desde Spotify usando la API oficial.
2. Busca la mejor coincidencia de cada canción en YouTube usando yt-dlp.
3. Descarga el audio en la mejor calidad disponible y lo convierte a MP3 usando ffmpeg.
4. Añade metadatos completos (título, artista, álbum, carátula, año, etc.) usando mutagen.
5. Todo el proceso es automático, robusto y con logs claros tanto en CLI como en GUI.

---

## Características principales

- Descarga playlists, álbumes o canciones individuales de Spotify.
- Interfaz gráfica (GUI) moderna y fácil de usar (PySide6/Qt).
- CLI avanzada basada en Typer y Rich.
- Búsqueda flexible en YouTube para encontrar la mejor versión.
- Conversión automática a MP3 (requiere ffmpeg instalado).
- Añade metadatos y carátula de Spotify.
- Compatible con Python 3.12+.
- Modular y fácil de extender.

---

## Instalación y requisitos

1. **Python 3.12 o superior**
2. **ffmpeg** instalado y en el PATH ([descargar aquí](https://www.gyan.dev/ffmpeg/builds/))
3. Instala las dependencias:
   ```sh
   pip install -r requirements.txt
   ```
4. Crea una app en el [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/) y obtén tu `Client ID` y `Client Secret`.
5. Crea un archivo `SPOTIFYPASS.txt` con:
   ```
   $env:SPOTIPY_CLIENT_ID='TU_CLIENT_ID'
   $env:SPOTIPY_CLIENT_SECRET='TU_CLIENT_SECRET'
   ```

---

## Uso rápido

### Interfaz gráfica (GUI)

Para lanzar la GUI:

```sh
python main.py
```

Podrás pegar la URL de Spotify, elegir la carpeta de destino y ver el progreso y logs en tiempo real.

### Línea de comandos (CLI)

Ejemplo para descargar una playlist:

```sh
python -m morphydownloader.cli --url "https://open.spotify.com/playlist/ID_DE_LA_PLAYLIST" --output music
```

Opciones principales:

- `--url` : URL de la playlist, álbum o canción de Spotify
- `--output`: Carpeta de destino para los MP3

---

## Estructura del proyecto

- `main.py`: Punto de entrada. Lanza la GUI por defecto o la CLI si se indica.
- `morphydownloader/`: Código fuente principal.
  - `cli.py`: Lógica de la CLI.
  - `gui/qt_gui.py`: Interfaz gráfica Qt.
  - `core/`: Módulos de integración con Spotify, YouTube y metadatos.
  - `config.py`, `utils.py`: Utilidades y configuración.
- `assets/`: Iconos y recursos gráficos.
- `requirements.txt`: Dependencias Python.

---

## Dependencias principales

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) (descarga y búsqueda en YouTube)
- [spotipy](https://github.com/spotipy-dev/spotipy) (API de Spotify)
- [mutagen](https://github.com/quodlibet/mutagen) (metadatos MP3)
- [PySide6](https://doc.qt.io/qtforpython/) (GUI Qt)
- [typer](https://github.com/tiangolo/typer) (CLI)
- [rich](https://github.com/Textualize/rich) (salida colorida)
- [ffmpeg](https://ffmpeg.org/) (debes instalarlo manualmente)

---

## Notas y recomendaciones

- El proyecto está modularizado y es fácil de mantener y extender.
- Si tienes problemas con la búsqueda en YouTube, asegúrate de tener la última versión de yt-dlp y ffmpeg.
- Los archivos temporales y tokens se regeneran automáticamente.
- ¡Si te gusta este proyecto, considera darle una ⭐ en GitHub y compartirlo!

---

## Licencia

MIT License

---

**¡Gracias por usar MorphyDownloader!**
Si tienes sugerencias, abre un issue o pull request.

## ¿Cómo funciona?

1. Obtiene la información de canciones, álbumes o playlists desde Spotify usando la API oficial.
2. Busca la mejor coincidencia de cada canción en YouTube usando yt-dlp.
3. Descarga el audio en la mejor calidad disponible y lo convierte a MP3 usando ffmpeg.
4. Añade metadatos completos (título, artista, álbum, carátula, año, etc.) usando mutagen.
5. Todo el proceso es automático y robusto, con manejo de errores y logs claros.

## Características principales

- Descarga playlists, álbumes o canciones individuales de Spotify.
- Búsqueda avanzada y flexible en YouTube para encontrar la mejor versión.
- Conversión automática a MP3 (se requiere ffmpeg instalado).
- Añade metadatos y carátula de Spotify.
- CLI moderna y fácil de usar basada en Typer.
- Compatible con Python 3.12+.

## Instalación y requisitos

1. **Python 3.12 o superior**
2. **ffmpeg** instalado y en el PATH ([descargar aquí](https://www.gyan.dev/ffmpeg/builds/))
3. Instala las dependencias:
   ```sh
   pip install -r requirements.txt
   ```
4. Crea una app en el [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/) y obtén tu `Client ID` y `Client Secret`.
5. Crea un archivo `SPOTIFYPASS.txt` con:
   ```
   $env:SPOTIPY_CLIENT_ID='TU_CLIENT_ID'
   $env:SPOTIPY_CLIENT_SECRET='TU_CLIENT_SECRET'
   ```

## Uso

Ejemplo para descargar una playlist:

```sh
python -m morphy_downloader.cli --url "https://open.spotify.com/playlist/ID_DE_LA_PLAYLIST" --output music
```

Opciones principales:

- `--url` : URL de la playlist, álbum o canción de Spotify
- `--output`: Carpeta de destino para los MP3

## Dependencias principales

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) (descarga y búsqueda en YouTube)
- [spotipy](https://github.com/spotipy-dev/spotipy) (API de Spotify)
- [mutagen](https://github.com/quodlibet/mutagen) (metadatos MP3)
- [moviepy](https://github.com/Zulko/moviepy) (procesado de audio/video)
- [typer](https://github.com/tiangolo/typer) (CLI)
- [rich](https://github.com/Textualize/rich) (salida colorida)
- [ffmpeg](https://ffmpeg.org/) (debes instalarlo manualmente)

## Notas

- El proyecto está modularizado y es fácil de mantener y extender.
- Si tienes problemas con la búsqueda en YouTube, asegúrate de tener la última versión de yt-dlp y ffmpeg.
- Los archivos temporales y tokens se regeneran automáticamente.

---
