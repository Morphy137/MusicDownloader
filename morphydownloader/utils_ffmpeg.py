import os
import sys
import shutil
import zipfile
import urllib.request
import platform
import subprocess
import tempfile
from pathlib import Path

FFMPEG_URLS = {
    'Windows': 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip',
    'Darwin': 'https://evermeet.cx/ffmpeg/ffmpeg-5.1.2.zip',  # macOS
    # Para Linux, recomendamos instalación via package manager
}

FFMPEG_BIN = 'ffmpeg.exe' if platform.system() == 'Windows' else 'ffmpeg'

def is_ffmpeg_available():
    """Verifica si ffmpeg está en el PATH o en la carpeta local."""
    # Verificar en PATH
    if shutil.which(FFMPEG_BIN):
        return True
    
    # Verificar en carpeta local del script
    local_path = os.path.join(os.path.dirname(__file__), FFMPEG_BIN)
    if os.path.exists(local_path):
        return True
    
    # Verificar en directorio de trabajo
    if os.path.exists(FFMPEG_BIN):
        return True
    
    # Verificar si está en el PATH con el comando
    try:
        subprocess.run([FFMPEG_BIN, '-version'], 
                      capture_output=True, check=True, timeout=10)
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return False

def get_ffmpeg_local_path():
    """Obtiene la ruta local donde debería estar ffmpeg."""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller executable
        return os.path.join(sys._MEIPASS, FFMPEG_BIN)
    else:
        # Development
        return os.path.join(os.path.dirname(__file__), FFMPEG_BIN)

def download_and_extract_ffmpeg(dest_folder=None):
    """Descarga y extrae ffmpeg en una carpeta local si no está disponible."""
    system = platform.system()
    
    if system == 'Linux':
        raise RuntimeError(
            'En Linux, instala ffmpeg usando tu package manager:\n'
            'Ubuntu/Debian: sudo apt install ffmpeg\n'
            'Fedora: sudo dnf install ffmpeg\n'
            'Arch: sudo pacman -S ffmpeg'
        )
    
    url = FFMPEG_URLS.get(system)
    if not url:
        raise RuntimeError(f'No hay descarga automática de ffmpeg para {system}. Descárgalo manualmente.')
    
    if dest_folder is None:
        dest_folder = os.path.dirname(__file__)
    
    os.makedirs(dest_folder, exist_ok=True)
    
    print('Descargando ffmpeg... Esto puede tomar unos minutos.')
    
    try:
        # Usar directorio temporal para la descarga
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = os.path.join(temp_dir, 'ffmpeg.zip')
            
            # Descargar con progreso
            def progress_hook(block_num, block_size, total_size):
                if total_size > 0:
                    percent = min(100, (block_num * block_size) / total_size * 100)
                    print(f'\rDescargando... {percent:.1f}%', end='', flush=True)
            
            urllib.request.urlretrieve(url, zip_path, progress_hook)
            print('\nExtrayendo ffmpeg...')
            
            # Extraer archivo
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Buscar el ejecutable en la estructura extraída
                for file_info in zip_ref.filelist:
                    if file_info.filename.endswith(FFMPEG_BIN):
                        # Extraer solo el ejecutable
                        file_info.filename = FFMPEG_BIN
                        zip_ref.extract(file_info, dest_folder)
                        break
                else:
                    # Si no se encuentra, extraer todo y buscar
                    extract_path = os.path.join(temp_dir, 'extracted')
                    zip_ref.extractall(extract_path)
                    
                    # Buscar recursivamente el ejecutable
                    for root, dirs, files in os.walk(extract_path):
                        if FFMPEG_BIN in files:
                            source_path = os.path.join(root, FFMPEG_BIN)
                            dest_path = os.path.join(dest_folder, FFMPEG_BIN)
                            shutil.copy2(source_path, dest_path)
                            break
                    else:
                        raise RuntimeError(f'No se encontró {FFMPEG_BIN} en el archivo descargado')
            
            # Verificar que se copió correctamente
            final_path = os.path.join(dest_folder, FFMPEG_BIN)
            if os.path.exists(final_path):
                # Hacer ejecutable en sistemas Unix
                if platform.system() != 'Windows':
                    os.chmod(final_path, 0o755)
                print(f'ffmpeg instalado correctamente en: {final_path}')
            else:
                raise RuntimeError('Error al copiar ffmpeg')
                
    except Exception as e:
        raise RuntimeError(f'Error al descargar/instalar ffmpeg: {e}')

def ensure_ffmpeg():
    """Asegura que ffmpeg esté disponible, si no lo descarga automáticamente."""
    if is_ffmpeg_available():
        print("ffmpeg ya está disponible")
        return True
    
    try:
        print("ffmpeg no encontrado. Intentando descarga automática...")
        
        # Determinar dónde instalarlo
        if hasattr(sys, '_MEIPASS'):
            # En ejecutable, instalar en directorio temporal
            install_dir = tempfile.gettempdir()
        else:
            # En desarrollo, instalar localmente
            install_dir = os.path.dirname(__file__)
        
        download_and_extract_ffmpeg(install_dir)
        
        # Agregar al PATH si es necesario
        ffmpeg_path = os.path.join(install_dir, FFMPEG_BIN)
        if os.path.exists(ffmpeg_path):
            dir_path = os.path.dirname(ffmpeg_path)
            if dir_path not in os.environ['PATH']:
                os.environ['PATH'] = dir_path + os.pathsep + os.environ['PATH']
        
        # Verificar instalación
        if is_ffmpeg_available():
            print("ffmpeg instalado y configurado correctamente")
            return True
        else:
            print("Warning: ffmpeg se instaló pero no está disponible")
            return False
            
    except Exception as e:
        print(f"Error al instalar ffmpeg automáticamente: {e}")
        print("Por favor, instala ffmpeg manualmente:")
        print("Windows: https://www.gyan.dev/ffmpeg/builds/")
        print("macOS: brew install ffmpeg")
        print("Linux: sudo apt install ffmpeg (Ubuntu/Debian)")
        return False

# Verificar al importar el módulo
if __name__ == "__main__":
    ensure_ffmpeg()