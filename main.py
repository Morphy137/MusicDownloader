#!/usr/bin/env python3
"""
MorphyDownloader - Spotify to MP3 Downloader
Punto de entrada optimizado con auto-instalación y gestión de iconos
"""
from PySide6.QtWidgets import QApplication, QMessageBox, QDialog
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
        'rich',
        'certifi'  # Añadido para certificados SSL
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
            print("Por favor instala manualmente: pip install spotipy yt-dlp mutagen PySide6 typer rich certifi")
            return False
    
    return True

def setup_ssl_certificates():
    """Configurar certificados SSL para descargas de portadas"""
    try:
        import certifi
        
        # Configurar contexto SSL con certificados de certifi
        # ssl_context = ssl.create_default_context(cafile=certifi.where())
        
        # Configurar variables de entorno para requests/urllib
        os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
        os.environ['SSL_CERT_FILE'] = certifi.where()
        
        print("✅ Certificados SSL configurados")
        return True
        
    except ImportError:
        print("⚠️ Módulo certifi no encontrado - portadas podrían fallar")
        return False
    except Exception as e:
        print(f"⚠️ Error configurando certificados SSL: {e}")
        return False

def check_spotify_credentials():
    """Verificar credenciales de Spotify"""
    return (os.environ.get('SPOTIPY_CLIENT_ID') and 
            os.environ.get('SPOTIPY_CLIENT_SECRET'))

def check_assets():
    """Verificar que los assets/iconos estén disponibles según la GUI"""
    from morphydownloader.gui.config_dialog import ICON_PATHS

    icon_paths = list(ICON_PATHS.values())
    missing_assets = []
    for path in icon_paths:
        abs_path = os.path.abspath(path)
        if not os.path.exists(abs_path):
            missing_assets.append(abs_path)

    if missing_assets:
        print(f"⚠️ Assets faltantes: {', '.join(missing_assets)}")
        print("La aplicación funcionará pero sin algunos iconos")
    else:
        print("✅ Todos los assets encontrados")

def show_dependencies_status():
    """Mostrar estado de todas las dependencias"""
    print("\n🔍 Verificando dependencias...")
    print("=" * 50)
    
    # SSL/Certificados
    ssl_ok = setup_ssl_certificates()
    
    # Spotify credentials
    spotify_ok = check_spotify_credentials()
    if spotify_ok:
        print("✅ Credenciales de Spotify configuradas")
    else:
        print("⚠️ Credenciales de Spotify no configuradas")
    
    # Assets
    check_assets()
    
    print("=" * 50)
    
    # Resumen
    issues = []
    if not ssl_ok:
        issues.append("Certificados SSL no configurados")
    if not spotify_ok:
        issues.append("Credenciales de Spotify faltantes")
    
    if issues:
        print(f"⚠️ Problemas encontrados: {len(issues)}")
        for issue in issues:
            print(f"  • {issue}")
        print("\n💡 Usa la configuración inicial para solucionar estos problemas")
    else:
        print("✅ Todas las dependencias están correctas")
    
    print()

def main():
    """Punto de entrada principal optimizado"""
    print("🎵 MorphyDownloader - Iniciando...")
    
    # Auto-instalar dependencias básicas
    if not install_requirements():
        sys.exit(1)
    
    # Verificar todas las dependencias
    show_dependencies_status()
    
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
            app = QApplication(sys.argv)
            app.setApplicationName("MorphyDownloader")
            app.setApplicationVersion("1.0.0")
            
            # Cargar configuración guardada si existe
            from morphydownloader.gui.config_dialog import load_saved_config, should_show_config
            load_saved_config()
            
            # Mostrar diálogo de configuración si es necesario
            if should_show_config():
                from morphydownloader.gui.config_dialog import ConfigDialog
                config_dialog = ConfigDialog()
                if config_dialog.exec() != QDialog.Accepted:
                    print("❌ Configuración cancelada")
                    sys.exit(1)
            
            # Verificar dependencias críticas después de la configuración
            critical_issues = []
            
            if not check_spotify_credentials():
                critical_issues.append("Credenciales de Spotify no configuradas")
            
            if critical_issues:
                QMessageBox.critical(
                    None, 
                    "Dependencias Críticas Faltantes", 
                    "MorphyDownloader necesita las siguientes configuraciones:\n\n" +
                    "\n".join([f"• {issue}" for issue in critical_issues]) +
                    "\n\nPor favor, completa la configuración inicial."
                )
                sys.exit(1)
            
            # Lanzar GUI principal
            from morphydownloader.gui.qt_gui import MorphyDownloaderQt
            window = MorphyDownloaderQt()
            window.show()
            
            print("🖥️ GUI iniciada correctamente")
            print("💡 Si tienes problemas con las portadas, verifica los certificados SSL")
            sys.exit(app.exec())
            
        except Exception as e:
            print(f"❌ Error fatal: {e}")
            if 'QApplication' in str(e):
                print("📋 Instala PySide6: pip install PySide6")
            elif 'certifi' in str(e):
                print("📋 Instala certifi: pip install certifi")
            sys.exit(1)

if __name__ == '__main__':
    main()