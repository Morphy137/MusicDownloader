"""
Configuración centralizada de la aplicación
"""

import os
import sys
import subprocess
import shutil

class Config:
    # Directorios
    DEFAULT_OUTPUT_DIR = 'music'
    TEMP_DIR_NAME = '.tmp'
    
    # Formatos de audio soportados
    SUPPORTED_FORMATS = ['m4a', 'mp3']
    DEFAULT_FORMAT = 'm4a'
    
    # Calidad de audio
    SUPPORTED_QUALITY = ['128', '192', '256', '320']
    DEFAULT_QUALITY = '192'
    
    # Colores de la interfaz
    PRIMARY_COLOR = "#E94560"
    PRIMARY_DARK = "#B8233A"
    BG_COLOR = "#181A20"
    FG_COLOR = "#F5F6FA"
    ENTRY_BG = "#23243A"
    SUCCESS_COLOR = "#22C55E"
    ERROR_COLOR = "#F43F5E"
    
    @staticmethod
    def get_asset_path(filename):
        """Obtiene la ruta correcta del asset independiente del empaquetado"""
        if hasattr(sys, '_MEIPASS'):
            # Ejecutable empaquetado con PyInstaller
            return os.path.join(sys._MEIPASS, 'assets', filename)
        else:
            # Desarrollo
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            return os.path.join(base_path, 'assets', filename)
    
    @staticmethod
    def check_ffmpeg():
        """Verificar si FFmpeg está disponible en el sistema"""
        try:
            # Intentar ejecutar ffmpeg para ver si está instalado
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            return False
    
    @staticmethod
    def get_ffmpeg_path():
        """Obtener la ruta de FFmpeg si está disponible"""
        if Config.check_ffmpeg():
            return shutil.which('ffmpeg')
        return None
    
    @staticmethod
    def get_format_info(format_type):
        """Obtener información sobre el formato seleccionado"""
        if format_type == 'mp3':
            return {
                'requires_ffmpeg': True,
                'description': 'MP3 - Formato universal compatible con todos los dispositivos',
                'extension': 'mp3',
                'quality_note': 'Requiere FFmpeg para conversión desde M4A'
            }
        else:  # m4a
            return {
                'requires_ffmpeg': False,
                'description': 'M4A - Formato de alta calidad nativo de YouTube',
                'extension': 'm4a',
                'quality_note': 'Descarga directa sin conversión'
            }