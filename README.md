# M4A_Downloader 🎵

**A modern, open-source tool to download songs, albums, or playlists from Spotify and videos/playlists from YouTube** as high-quality M4A files. Spotify links obtain audio from YouTube and automatically add full metadata (title, artist, album, cover art, year, etc.); YouTube links download directly with metadata from YouTube. It features both an intuitive graphical interface (GUI) and a powerful command-line interface (CLI). Now with a fully redesigned interface, button icons, and no ffmpeg dependency.

![MorphyDownloader GUI](assets/img/screnshot.png)

---

## 🚀 How does it work?

1. Detects whether the URL is from Spotify or YouTube.
2. For Spotify links, retrieves song, album, or playlist information using the official API (you need your own credentials).
3. Searches for the best YouTube match for each Spotify track using yt-dlp, or reads YouTube videos/playlists directly.
4. Downloads the audio in the best available quality as M4A (no conversion or ffmpeg required).
5. Adds metadata and cover art using Spotify or YouTube information via mutagen.
5. The process is fully automatic, robust, and logs progress clearly in both CLI and GUI.

![MorphyDownloader URL](assets/img/URL_Song.png)

**Note:**

- The program does NOT contain any malware, spyware, or trojans. All code is open source and auditable.
- It is recommended to temporarily disable Antivirus if the browser does not allow you to download it.
- You need your own Spotify API credentials (see below). The app will guide you through the setup the first time you run it.

---

## 🛠️ Installation & Requirements

1. **Python 3.12 or higher** 🐍

2. Install dependencies:

   ```sh
   pip install -r requirements.txt
   ```

3. Create an app in the Spotify Developer Dashboard and get your `Client ID` and `Client Secret`.

4. Configure your credentials:

   - The program will guide you through the setup the first time you run it (recommended for most users).
   - Alternatively, you can set the following environment variables manually:
     - `SPOTIPY_CLIENT_ID`
     - `SPOTIPY_CLIENT_SECRET`

---

## 📥 Download (Pre-built Executable)

You can download a pre-built `.exe` (and console version) from the GitHub releases section. No installation required—just run the executable and follow the setup instructions. The GUI now features icons for all buttons and a modern dark theme.

![M4A_Downloader .EXE](assets/img/ejecutables.png)

---

## 🎧 Usage

### Graphical Interface (GUI)

To launch the GUI:

```sh
python main.py
```

Paste your Spotify or YouTube URL, choose the output folder, and track progress in real time. You can now change settings at any time using the configuration button.

### Command Line Interface (CLI)

Example to download a playlist:

```sh
python -m m4a_downloader.cli --url "https://open.spotify.com/playlist/PLAYLIST_ID" --output music
```

Main options:

- `--url`: Spotify playlist/album/track URL or YouTube video/playlist URL
- `--output`: Output folder for M4A files

---

## 📂 Project Structure

- `main.py`: Entry point. Launches the GUI by default or CLI if specified.
- `morphydownloader/`: Main source code.
  - `cli.py`: CLI logic.
  - `gui/qt_gui.py`: Qt graphical interface (now with dynamic sizing, not fixed size).
  - `core/`: Spotify, YouTube, and metadata integration modules.
  - `config.py`, `utils.py`: Utilities and configuration.
- `assets/`: Icons and graphical resources (now organized in specific folders).
- `requirements.txt`: Python dependencies.

---

## 📦 Main Dependencies

- yt-dlp (YouTube download/search)
- spotipy (Spotify API)
- mutagen (metadata for M4A)
- PySide6 (Qt GUI)
- typer (CLI)
- rich (colored output)

---

## ⚠️ Notes & Recommendations

- The project is modular and easy to maintain or extend.
- If you have issues with YouTube search, ensure you have the latest yt-dlp.
- Temporary files and tokens are regenerated automatically.
- All buttons now use icons for a more modern look.
- The interface color scheme has been updated for a better dark mode experience.
- The window size is now dynamic and adapts to your screen.
- You can change settings at any time from the GUI.
- If you like this project, consider giving it a ⭐ on GitHub and sharing it!

---

## 📜 License

MIT License

---

**Thanks for using MorphyDownloader!** 🎧If you have suggestions, open an issue or pull request.

---

## 🌍 Español

For the Spanish version, see README_ES.md
