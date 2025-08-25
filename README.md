# MorphyDownloader 🎵

**A modern, open-source tool to download songs, albums, or playlists from Spotify** as MP3 files, obtaining the audio from YouTube and automatically adding full metadata (title, artist, album, cover art, year, etc.). It features both an intuitive graphical interface (GUI) and a powerful command-line interface (CLI).

![MorphyDownloader GUI](https://github.com/Morphy137/MusicDownloader/raw/main/assets/screenshot.png)

---

## 🚀 How does it work?

1. Retrieves song, album, or playlist information from Spotify using the official API (you need your own credentials).
2. Searches for the best YouTube match for each track using yt-dlp.
3. Downloads the audio in the best available quality and converts it to MP3 using ffmpeg.
4. Adds full metadata and cover art from Spotify using mutagen.
5. The process is fully automatic, robust, and logs progress clearly in both CLI and GUI.

**Note:**

- The program does NOT contain any malware, spyware, or trojans. All code is open source and auditable.
- It is recommended to temporarily disable Antivirus if the browser does not allow you to download it.
- You need your own Spotify API credentials (see below). The app will guide you through the setup the first time you run it.

---

## 🛠️ Installation & Requirements

1. **Python 3.12 or higher** 🐍

2. **ffmpeg** installed and in your PATH (download here)

3. Install dependencies:

   ```sh
   pip install -r requirements.txt
   ```

4. Create an app in the Spotify Developer Dashboard and get your `Client ID` and `Client Secret`.

5. Configure your credentials:

   - The program will guide you through the setup the first time you run it (recommended for most users).
   - Alternatively, you can set the following environment variables manually:
     - `SPOTIPY_CLIENT_ID`
     - `SPOTIPY_CLIENT_SECRET`

---

## 📥 Download (Pre-built Executable)

You can download a pre-built `.exe` (and console version) from the GitHub releases section. No installation required—just run the executable and follow the setup instructions.

---

## 🎧 Usage

### Graphical Interface (GUI)

To launch the GUI:

```sh
python main.py
```

Paste your Spotify URL, choose the output folder, and track progress in real time.

### Command Line Interface (CLI)

Example to download a playlist:

```sh
python -m morphydownloader.cli --url "https://open.spotify.com/playlist/PLAYLIST_ID" --output music
```

Main options:

- `--url`: Spotify playlist, album, or track URL
- `--output`: Output folder for MP3 files

---

## 📂 Project Structure

- `main.py`: Entry point. Launches the GUI by default or CLI if specified.
- `morphydownloader/`: Main source code.
  - `cli.py`: CLI logic.
  - `gui/qt_gui.py`: Qt graphical interface.
  - `core/`: Spotify, YouTube, and metadata integration modules.
  - `config.py`, `utils.py`: Utilities and configuration.
- `assets/`: Icons and graphical resources.
- `requirements.txt`: Python dependencies.

---

## 📦 Main Dependencies

- yt-dlp (YouTube download/search)
- spotipy (Spotify API)
- mutagen (MP3 metadata)
- PySide6 (Qt GUI)
- typer (CLI)
- rich (colored output)
- ffmpeg (must be installed manually)

---

## ⚠️ Notes & Recommendations

- The project is modular and easy to maintain or extend.
- If you have issues with YouTube search, ensure you have the latest yt-dlp and ffmpeg.
- Temporary files and tokens are regenerated automatically.
- If you like this project, consider giving it a ⭐ on GitHub and sharing it!

---

## 📜 License

MIT License

---

**Thanks for using MorphyDownloader!** 🎧If you have suggestions, open an issue or pull request.

---

## 🌍 Español

For the Spanish version, see README_ES.md