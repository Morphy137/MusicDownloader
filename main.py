#!/usr/bin/env python3
"""
MorphyDownloader - Spotify to MP3 Downloader
Punto de entrada principal de la aplicación
"""


import sys
import os
import argparse
# Integrar ffmpeg auto-descarga
try:
    from morphydownloader.utils_ffmpeg import ensure_ffmpeg
    ensure_ffmpeg()
except Exception as e:
    print(f"[WARN] No se pudo verificar/instalar ffmpeg automáticamente: {e}")

# Añadir el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Punto de entrada principal"""
    parser = argparse.ArgumentParser(
        description='MorphyDownloader - Descarga música de Spotify como MP3'
    )
    parser.add_argument(
        '--cli', 
        action='store_true', 
        help='Usar modo línea de comandos'
    )
    parser.add_argument(
        '-u', '--url', 
        type=str, 
        help='URL de Spotify (solo para modo CLI)'
    )
    parser.add_argument(
        '-o', '--output', 
        type=str, 
        default='music',
        help='Directorio de salida (solo para modo CLI)'
    )
    
    args, unknown = parser.parse_known_args()
    
    if args.cli or args.url or unknown:
        # Modo CLI
        from morphydownloader.cli import app as cli_app
        if args.url:
            # Ejecutar descarga directa
            from morphydownloader.cli import download
            download(args.url, args.output)
        else:
            # Usar CLI interactivo de typer
            cli_app()
    else:
        # Modo GUI (por defecto)
        from morphydownloader.gui.qt_gui import main as qt_main
        qt_main()

if __name__ == '__main__':
    main()