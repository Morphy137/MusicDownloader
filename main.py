# main.py optimizado - Solo verificar variables de entorno

#!/usr/bin/env python3
"""
MorphyDownloader - Spotify to MP3 Downloader
Punto de entrada principal de la aplicación
"""

import sys
import os
import argparse

# Añadir el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_spotify_credentials():
    """Verificar SOLO si las credenciales de Spotify están en variables de entorno"""
    return (os.environ.get('SPOTIPY_CLIENT_ID') and 
            os.environ.get('SPOTIPY_CLIENT_SECRET'))

def check_ffmpeg_availability():
    """Verificación rápida de FFmpeg sin descargar"""
    import shutil
    return shutil.which('ffmpeg') is not None or shutil.which('ffmpeg.exe') is not None

def main():
    """Punto de entrada principal optimizado"""
    parser = argparse.ArgumentParser(
        description='MorphyDownloader - Descarga música de Spotify como MP3'
    )
    parser.add_argument('--cli', action='store_true', help='Usar modo línea de comandos')
    parser.add_argument('-u', '--url', type=str, help='URL de Spotify (solo para modo CLI)')
    parser.add_argument('-o', '--output', type=str, default='music', help='Directorio de salida (solo para modo CLI)')
    parser.add_argument('--config', action='store_true', help='Mostrar ventana de configuración')
    parser.add_argument('--install-ffmpeg', action='store_true', help='Instalar FFmpeg automáticamente')
    
    args, unknown = parser.parse_known_args()
    
    # Instalación manual de FFmpeg si se solicita
    if args.install_ffmpeg:
        try:
            from morphydownloader.utils_ffmpeg import ensure_ffmpeg
            ensure_ffmpeg()
            print("✅ FFmpeg instalado correctamente")
            return
        except Exception as e:
            print(f"❌ Error instalando FFmpeg: {e}")
            return
    
    # Verificación rápida de FFmpeg (opcional warning)
    if not check_ffmpeg_availability():
        print("⚠️  Warning: FFmpeg no encontrado en PATH")
        print("   Ejecuta: python main.py --install-ffmpeg")
        print("   O instala manualmente desde: https://ffmpeg.org/")
    
    if args.cli or args.url or unknown:
        # Modo CLI
        
        # Cargar configuración guardada SOLO para CLI
        try:
            from morphydownloader.gui.config_dialog import load_saved_config
            load_saved_config()
        except Exception:
            pass
        
        # Verificar credenciales
        if not check_spotify_credentials():
            print("❌ Error: Credenciales de Spotify no configuradas.")
            print("\nOpciones:")
            print("1. Configurar variables de entorno:")
            print("   SPOTIPY_CLIENT_ID=tu_client_id")
            print("   SPOTIPY_CLIENT_SECRET=tu_client_secret")
            print("2. Usar GUI para configurar: python main.py --config")
            print("3. Más info: https://developer.spotify.com/dashboard/")
            sys.exit(1)
        
        if args.url:
            # Descarga directa CLI
            try:
                print(f"🎵 Iniciando descarga de: {args.url}")
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
        from PySide6.QtWidgets import QApplication, QMessageBox
        
        app = QApplication(sys.argv)
        app.setApplicationName("MorphyDownloader")
        app.setApplicationVersion("1.0.0")
        
        # Cargar configuración guardada RÁPIDAMENTE
        try:
            from morphydownloader.gui.config_dialog import load_saved_config, should_show_config
            load_saved_config()
        except ImportError:
            pass
        
        # Mostrar configuración SOLO si es necesario
        show_config = args.config or not check_spotify_credentials()
        
        # Si debe mostrar configuración opcional (primera vez)
        if not show_config:
            try:
                show_config = should_show_config()
            except:
                show_config = False
        
        if show_config:
            try:
                from morphydownloader.gui.config_dialog import ConfigDialog
                
                config_dialog = ConfigDialog()
                if config_dialog.exec() != config_dialog.Accepted:
                    if not check_spotify_credentials():
                        QMessageBox.critical(
                            None, 
                            "Configuración Requerida", 
                            "MorphyDownloader necesita credenciales de Spotify.\n"
                            "Configure SPOTIPY_CLIENT_ID y SPOTIPY_CLIENT_SECRET."
                        )
                        sys.exit(1)
            except ImportError:
                QMessageBox.critical(
                    None, 
                    "Error", 
                    "Configure las variables de entorno:\n"
                    "SPOTIPY_CLIENT_ID y SPOTIPY_CLIENT_SECRET"
                )
                sys.exit(1)
        
        # Verificación final
        if not check_spotify_credentials():
            QMessageBox.critical(
                None, 
                "Credenciales Faltantes", 
                "Variables de entorno requeridas:\n"
                "SPOTIFY_CLIENT_ID\nSPOTIFY_CLIENT_SECRET"
            )
            sys.exit(1)
        
        # Lanzar GUI principal
        try:
            from morphydownloader.gui.qt_gui import MorphyDownloaderQt
            window = MorphyDownloaderQt()
            window.show()
            sys.exit(app.exec())
        except Exception as e:
            QMessageBox.critical(None, "Error Fatal", f"Error: {e}")
            sys.exit(1)

if __name__ == '__main__':
    main()