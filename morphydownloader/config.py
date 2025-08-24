"""
Configuración centralizada de la aplicación
"""

import os
import sys

class Config:
    # Directorios
    DEFAULT_OUTPUT_DIR = 'music'
    TEMP_DIR_NAME = 'tmp'
    
    # Calidad de audio
    SUPPORTED_QUALITY = ['128', '192', '256', '320']
    DEFAULT_QUALITY = '192'
    
    # Colores de la interfaz
    PRIMARY_COLOR = '#DC143C'
    PRIMARY_DARK = '#a10e2a'
    BG_COLOR = '#181a1b'
    FG_COLOR = '#e1e1e1'
    ENTRY_BG = '#23272e'
    SUCCESS_COLOR = '#2ecc71'
    ERROR_COLOR = '#e74c3c'
    
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