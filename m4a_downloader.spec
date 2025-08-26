# -*- mode: python ; coding: utf-8 -*-

# m4a_downloader.spec - Configuración optimizada para PyInstaller (SIN FFmpeg incluido)

import os
import sys

# Obtener ruta de certificados de certifi
def get_certifi_path():
    try:
        import certifi
        return certifi.where()
    except ImportError:
        return None

block_cipher = None

# Datos adicionales para incluir
datas = [
    ('assets', 'assets'),  # Incluir carpeta de assets
]

# Incluir certificados SSL si certifi está disponible
certifi_path = get_certifi_path()
if certifi_path and os.path.exists(certifi_path):
    datas.append((certifi_path, 'certifi'))
    print(f"Including certifi certificates: {certifi_path}")

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        # Spotify
        'spotipy',
        'spotipy.oauth2',
        'spotipy.client',
        'spotipy.util',
        # YouTube
        'yt_dlp',
        'yt_dlp.extractor',
        'yt_dlp.postprocessor',
        'yt_dlp.utils',
        # Audio processing (solo mutagen para M4A)
        'mutagen',
        'mutagen.easyid3',
        'mutagen.id3',
        'mutagen.mp3',
        'mutagen.mp4',
        'mutagen._file',
        'mutagen._tags',
        # GUI
        'PySide6.QtCore',
        'PySide6.QtWidgets',
        'PySide6.QtGui',
        # CLI
        'typer',
        'rich',
        'rich.console',
        'rich.progress',
        'rich.text',
        # SSL and certificates
        'ssl',
        'certifi',
        'urllib3',
        'urllib3.util',
        'urllib3.util.ssl_',
        'urllib3.contrib.pyopenssl',
        # HTTP requests
        'urllib.request',
        'urllib.error',
        'urllib.parse',
        'http.client',
        'http.server',
        # System
        'tempfile',
        'shutil',
        'subprocess',
        'threading',
        'concurrent.futures',
        # JSON and data
        'json',
        'csv',
        'configparser',
        # Regex and text
        're',
        'difflib',
        'string',
        # Math and time
        'time',
        'datetime',
        'math',
        'random',
        # File handling
        'os',
        'os.path',
        'pathlib',
        'zipfile',
        # Logging
        'logging',
        'logging.handlers',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Excluir módulos innecesarios para reducir tamaño
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'tkinter',
        'PIL',
        'Pillow',
        'IPython',
        'jupyter',
        'notebook',
        'torch',
        'tensorflow',
        'opencv',
        'sklearn',
        'sympy',
        'pytest',
        'setuptools',
        'wheel',
        'pip',
        # NO incluir FFmpeg - debe ser instalado por el usuario
        'ffmpeg',
        'ffmpeg-python',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Filtrar archivos innecesarios para reducir tamaño
def filter_binaries(binaries):
    """Filtrar binaries innecesarios"""
    filtered = []
    skip_patterns = [
        'Qt6Quick',
        'Qt6Qml', 
        'Qt6Network',
        'Qt6OpenGL',
        'Qt6Pdf',
        'Qt6WebEngine',
        'Qt6Designer',
        'Qt6Test',
        'Qt6Sql',
        'Qt6PrintSupport',
        'api-ms-win',  # Windows API files
        'ucrtbase',    # Universal C Runtime
        'ffmpeg',      # No incluir FFmpeg
        'ffprobe',     # No incluir FFprobe
    ]
    
    keep_patterns = [
        'Qt6Core',
        'Qt6Gui', 
        'Qt6Widgets',
        'python',
        'ssl',
        'crypto',
    ]
    
    for name, path, kind in binaries:
        # Always keep essential libraries
        should_keep = any(pattern in name for pattern in keep_patterns)
        if should_keep:
            filtered.append((name, path, kind))
            continue
            
        # Skip unwanted libraries
        should_skip = any(pattern in name for pattern in skip_patterns)
        if not should_skip:
            filtered.append((name, path, kind))
    
    return filtered

a.binaries = filter_binaries(a.binaries)

# Filtrar archivos de datos innecesarios
def filter_datas(datas):
    """Filtrar archivos de datos innecesarios"""
    filtered = []
    skip_patterns = [
        'tcl',
        'tk',
        'test',
        '__pycache__',
        '.pyc',
        '.pyo',
        'examples',
        'docs',
        'locale',  # Algunos locales innecesarios
        'ffmpeg',  # No incluir archivos de FFmpeg
    ]
    
    keep_patterns = [
        'assets',
        'certifi',
        'cacert.pem',
        'cert.pem',
    ]
    
    for dest, source, kind in datas:
        # Always keep essential data
        should_keep = any(pattern in dest for pattern in keep_patterns)
        if should_keep:
            filtered.append((dest, source, kind))
            continue
            
        # Skip unwanted data
        should_skip = any(pattern in dest for pattern in skip_patterns)
        if not should_skip:
            filtered.append((dest, source, kind))
    
    return filtered

a.datas = filter_datas(a.datas)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MorphyDownloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Comprimir ejecutable
    upx_exclude=[
        'Qt6Core.dll',
        'Qt6Gui.dll', 
        'Qt6Widgets.dll',
        'python*.dll',
    ],
    runtime_tmpdir=None,
    console=False,  # Sin ventana de consola para la versión principal
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico'  # Icono del ejecutable
)

exe_console = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MorphyDownloader-Console',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[
        'Qt6Core.dll',
        'Qt6Gui.dll', 
        'Qt6Widgets.dll',
        'python*.dll',
    ],
    runtime_tmpdir=None,
    console=True,  # CON ventana de consola para debug
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon_console.ico'
)

# Comentarios importantes sobre FFmpeg:
# - FFmpeg NO está incluido en el ejecutable intencionalmente
# - Los usuarios deben instalarlo manualmente en su sistema
# - Esto mantiene el ejecutable ligero y evita problemas de licencias
# - La aplicación detecta automáticamente si FFmpeg está disponible
# - Si no está disponible, usa M4A como fallback (que no requiere conversión)