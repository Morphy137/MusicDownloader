# M4A_Downloader 🎵

**Una herramienta moderna y de código abierto para descargar canciones, álbumes o playlists de Spotify y videos/playlists de YouTube** en archivos M4A de alta calidad. Los enlaces de Spotify obtienen el audio desde YouTube y añaden metadatos completos (título, artista, álbum, carátula, año, etc.); los enlaces de YouTube se descargan directamente con metadatos de YouTube. Incluye tanto una interfaz gráfica intuitiva (GUI) como una potente línea de comandos (CLI). Ahora con interfaz rediseñada, iconos en todos los botones y sin dependencia de ffmpeg.

![MorphyDownloader GUI](assets/img/screnshot.png)

---

---

## 🚀 ¿Cómo funciona?

1. Detecta si la URL es de Spotify o YouTube.
2. Para enlaces de Spotify, obtiene la información de la canción, álbum o playlist usando la API oficial (necesitas tus propias credenciales).
3. Busca la mejor coincidencia en YouTube para cada pista de Spotify usando yt-dlp, o lee videos/playlists de YouTube directamente.
4. Descarga el audio en la mejor calidad disponible como M4A (sin conversión ni ffmpeg).
5. Añade metadatos y carátula usando información de Spotify o YouTube mediante mutagen.
6. El proceso es totalmente automático, robusto y muestra el progreso claramente tanto en CLI como en GUI.

![MorphyDownloader URL](assets/img/URL_Song.png)

**Nota:**

- El programa NO contiene malware, spyware ni troyanos. Todo el código es abierto y auditable.
- Se recomienda desactivar temporalmente el Antivirus si el navegador no permite descargarlo.
- Necesitas tus propias credenciales de la API de Spotify (ver abajo). La app te guiará en la configuración la primera vez que la ejecutes.

---

---

## 🛠️ Instalación y requisitos

1. **Python 3.12 o superior** 🐍

2. Instala las dependencias:

   ```sh
   pip install -r requirements.txt
   ```

3. Crea una app en el [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/) y obtén tu `Client ID` y `Client Secret`.

4. Configura tus credenciales:

   - El programa te guiará en la configuración la primera vez que lo ejecutes (recomendado para la mayoría de usuarios).
   - Alternativamente, puedes establecer las siguientes variables de entorno manualmente:
     - `SPOTIPY_CLIENT_ID`
     - `SPOTIPY_CLIENT_SECRET`

---

## 📥 Descargar (Ejecutable precompilado)

Puedes descargar un `.exe` precompilado (y versión consola) desde la sección de releases de GitHub. No requiere instalación: solo ejecuta el archivo y sigue las instrucciones de configuración. La GUI ahora tiene iconos en todos los botones y un tema oscuro moderno.

![MorphyDownloader .EXE](assets/img/ejecutables.png)

---

---

## 🎧 Uso

### Interfaz gráfica (GUI)

Para lanzar la GUI:

```sh
python main.py
```

Pega tu URL de Spotify o YouTube, elige la carpeta de destino y sigue el progreso en tiempo real. Ahora puedes cambiar la configuración en cualquier momento desde el botón de configuración.

### Línea de comandos (CLI)

Ejemplo para descargar una playlist:

```sh
python -m morphydownloader.cli --url "https://open.spotify.com/playlist/ID_DE_LA_PLAYLIST" --output music
```

Opciones principales:

- `--url`: URL de playlist, álbum o canción de Spotify, o video/playlist de YouTube
- `--output`: Carpeta de destino para los archivos M4A

---

---

## 📂 Estructura del proyecto

- `main.py`: Punto de entrada. Lanza la GUI por defecto o la CLI si se indica.
- `morphydownloader/`: Código fuente principal.
  - `cli.py`: Lógica de la CLI.
  - `gui/qt_gui.py`: Interfaz gráfica Qt (ahora con tamaño dinámico, no fixed size).
  - `core/`: Módulos de integración con Spotify, YouTube y metadatos.
  - `config.py`, `utils.py`: Utilidades y configuración.
- `assets/`: Iconos y recursos gráficos (ahora organizados en carpetas específicas).
- `requirements.txt`: Dependencias Python.

---

---

## 📦 Dependencias principales

- yt-dlp (descarga y búsqueda en YouTube)
- spotipy (API de Spotify)
- mutagen (metadatos para M4A)
- PySide6 (GUI Qt)
- typer (CLI)
- rich (salida colorida)

---

---

## ⚠️ Notas y recomendaciones

- El proyecto es modular y fácil de mantener o extender.
- Si tienes problemas con la búsqueda en YouTube, asegúrate de tener la última versión de yt-dlp.
- Los archivos temporales y tokens se regeneran automáticamente.
- Todos los botones ahora usan iconos para una apariencia más moderna.
- El esquema de colores de la interfaz se ha actualizado para un mejor modo oscuro.
- El tamaño de la ventana ahora es dinámico y se adapta a tu pantalla.
- Puedes cambiar la configuración en cualquier momento desde la GUI.
- ¡Si te gusta este proyecto, considera darle una ⭐ en GitHub y compartirlo!

---

---

## 📜 Licencia

MIT License

---

**¡Gracias por usar M4A_Downloader!** 🎧 Si tienes sugerencias, abre un issue o pull request.

---

# English

For the English version, see [README.md](README.md)
