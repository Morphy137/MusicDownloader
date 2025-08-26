"""
Configuración centralizada de la aplicación
"""

import os
import sys

class Config:
    # Directorios
    DEFAULT_OUTPUT_DIR = 'music'
    TEMP_DIR_NAME = '.tmp'
    
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