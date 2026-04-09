# Historial de Actualizaciones (Changelog)

Este documento sirve como registro oficial de las características, funciones y correcciones implementadas en MorphyDownloader, para facilitar el seguimiento a futuro.

## [Próxima Versión / En Desarrollo]

### [1.1.2] - Actualización Temas y Lyrics!:
- **Base y Organización**: 
  - Creación de este documento (`docs/CHANGELOG.md`) para el seguimiento del historial del proyecto.
  - Preparación de la arquitectura base para soporte Multi-idioma (Inglés y Español).
- **Temas (Theming)**:
  - Implementación de un nuevo gestor de temas con soporte de Modo Claro/Oscuro y varias opciones de color de acento.
- **Configuración Amigable**:
  - Remodelación de los ajustes de UI utilizando Scroll Areas para prevenir "bugs de overflow" al mostrar muchas opciones.
- **Personalización de la Nomenclatura y Organización de Carpetas**:
  - Implementación de un selector de la sintaxis del nombre de salida de los audios.
  - Inclusión de un ajuste (activable) para colocar listas de reproducción/álbumes en sus respectivas carpetas por defecto.
- **Metadatos Premium**:
  - Descarga y añadido de letras (Lyrics) a los archivos MP3/M4A.

---

## [1.0.0] - Versión Inicial
- **Interfaz (GUI)**:
  - Nueva GUI moderna en PySide6 con tamaño dinámico y optimizado.
  - Implementación de Iconos gráficos en todos los botones para mejor interacción.
- **Funcionalidad Principal (Core)**:
  - Descarga de alta calidad en M4A nativo y soporte MP3 usando `yt-dlp` y FFmpeg, desde links de Spotify.
  - Inclusión de carátulas HQ y metadatos detallados (Artista, álbum, track_number) utilizando `spotipy` y `mutagen`.
- **Accesibilidad**:
  - Versión ejecutable lista para usarse, sin dependencias.
  - Asistente de configuración inicial (Client ID y Client Secret de Spotify).
