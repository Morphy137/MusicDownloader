import os
import sys
import shutil
import zipfile
import urllib.request
import platform

FFMPEG_URLS = {
    'Windows': 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip',
    # Puedes agregar URLs para otros sistemas si lo deseas
}

FFMPEG_BIN = 'ffmpeg.exe' if platform.system() == 'Windows' else 'ffmpeg'


def is_ffmpeg_available():
    """Verifica si ffmpeg está en el PATH o en la carpeta local."""
    if shutil.which(FFMPEG_BIN):
        return True
    # Buscar en carpeta local
    local_path = os.path.join(os.path.dirname(__file__), FFMPEG_BIN)
    return os.path.exists(local_path)


def download_and_extract_ffmpeg(dest_folder='ffmpeg_bin'):
    """Descarga y extrae ffmpeg en una carpeta local si no está disponible."""
    system = platform.system()
    url = FFMPEG_URLS.get(system)
    if not url:
        raise RuntimeError(f'No hay descarga automática de ffmpeg para {system}. Descárgalo manualmente.')
    os.makedirs(dest_folder, exist_ok=True)
    zip_path = os.path.join(dest_folder, 'ffmpeg.zip')
    print('Descargando ffmpeg...')
    urllib.request.urlretrieve(url, zip_path)
    print('Extrayendo ffmpeg...')
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(dest_folder)
    # Buscar el ejecutable dentro de la estructura extraída
    for root, dirs, files in os.walk(dest_folder):
        if FFMPEG_BIN in files:
            ffmpeg_path = os.path.join(root, FFMPEG_BIN)
            shutil.copy(ffmpeg_path, os.path.join(os.path.dirname(__file__), FFMPEG_BIN))
            break
    os.remove(zip_path)
    print('ffmpeg listo para usar.')


def ensure_ffmpeg():
    """Asegura que ffmpeg esté disponible, si no lo descarga automáticamente."""
    if not is_ffmpeg_available():
        download_and_extract_ffmpeg()
        # Agregar carpeta local al PATH temporalmente
        os.environ['PATH'] = os.path.dirname(__file__) + os.pathsep + os.environ['PATH']

# Puedes llamar a ensure_ffmpeg() al inicio de tu app principal o justo antes de usar ffmpeg.
