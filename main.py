#!/usr/bin/env python3
"""
MorphyDownloader - Spotify to MP3 Downloader
Punto de entrada optimizado con auto-instalación
"""

import sys
import os
import argparse
import subprocess

# Añadir el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def install_requirements():
    """Instalar dependencias automáticamente si no están disponibles"""
    required_packages = [
        'spotipy',
        'yt-dlp', 
        'mutagen',
        'PySide6',
        'typer',
        'rich'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"📦 Instalando dependencias faltantes: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "--user", *missing_packages
            ])
            print("✅ Dependencias instaladas correctamente")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error instalando dependencias: {e}")
            print("Por favor instala manualmente: pip install spotipy yt-dlp mutagen PySide6 typer rich")
            return False
    
    return True

def ensure_ffmpeg():
    """Asegurar que FFmpeg esté disponible"""
    import shutil
    
    if shutil.which('ffmpeg') or shutil.which('ffmpeg.exe'):
        print("✅ FFmpeg disponible")
        return True
    
    print("⚠️  FFmpeg no encontrado. Intentando instalación automática...")
    
    try:
        from morphydownloader.utils_ffmpeg import ensure_ffmpeg as auto_install_ffmpeg
        return auto_install_ffmpeg()
    except Exception as e:
        print(f"❌ Error instalando FFmpeg automáticamente: {e}")
        print("\n📋 Instala FFmpeg manualmente:")
        print("Windows: https://www.gyan.dev/ffmpeg/builds/")
        print("macOS: brew install ffmpeg")
        print("Linux: sudo apt install ffmpeg")
        return False

def check_spotify_credentials():
    """Verificar credenciales de Spotify"""
    return (os.environ.get('SPOTIPY_CLIENT_ID') and 
            os.environ.get('SPOTIPY_CLIENT_SECRET'))

def main():
    """Punto de entrada principal optimizado"""
    print("🎵 MorphyDownloader - Iniciando...")
    
    # Auto-instalar dependencias
    if not install_requirements():
        sys.exit(1)
    
    # Verificar FFmpeg
    if not ensure_ffmpeg():
        print("⚠️  Continuando sin FFmpeg (puede causar errores)")
    
    parser = argparse.ArgumentParser(
        description='MorphyDownloader - Descarga música de Spotify como MP3'
    )
    parser.add_argument('--cli', action='store_true', help='Usar modo línea de comandos')
    parser.add_argument('-u', '--url', type=str, help='URL de Spotify (solo para modo CLI)')
    parser.add_argument('-o', '--output', type=str, default='music', help='Directorio de salida')
    
    args, unknown = parser.parse_known_args()
    
    if args.cli or args.url or unknown:
        # Modo CLI
        if not check_spotify_credentials():
            print("❌ Error: Credenciales de Spotify no configuradas.")
            print("\n🔧 Configura las variables de entorno:")
            print("SPOTIPY_CLIENT_ID=tu_client_id")
            print("SPOTIPY_CLIENT_SECRET=tu_client_secret")
            print("\n📋 Más info: https://developer.spotify.com/dashboard/")
            sys.exit(1)
        
        if args.url:
            # Descarga directa CLI
            try:
                print(f"🎵 Descargando: {args.url}")
                from morphydownloader.cli import download
                download(args.url, args.output)
            except Exception as e:
                print(f"❌ Error: {e}")
                sys.exit(1)
        else:
            # CLI interactivo
            from morphydownloader.cli import app as cli_app
            cli_app()
    else:
        # Modo GUI (por defecto)
        try:
            from PySide6.QtWidgets import QApplication, QMessageBox
            
            app = QApplication(sys.argv)
            app.setApplicationName("MorphyDownloader")
            app.setApplicationVersion("1.0.0")
            
            # Verificar credenciales para GUI
            if not check_spotify_credentials():
                QMessageBox.critical(
                    None, 
                    "Credenciales Requeridas", 
                    "MorphyDownloader necesita credenciales de Spotify.\n\n"
                    "Configura las variables de entorno:\n"
                    "SPOTIPY_CLIENT_ID\n"
                    "SPOTIPY_CLIENT_SECRET\n\n"
                    "Más info: https://developer.spotify.com/dashboard/"
                )
                sys.exit(1)
            
            # Lanzar GUI principal
            from morphydownloader.gui.qt_gui import MorphyDownloaderQt
            window = MorphyDownloaderQt()
            window.show()
            
            print("🖥️  GUI iniciada correctamente")
            sys.exit(app.exec())
            
        except Exception as e:
            print(f"❌ Error fatal: {e}")
            if 'QApplication' in str(e):
                print("📋 Instala PySide6: pip install PySide6")
            sys.exit(1)

if __name__ == '__main__':
    main()