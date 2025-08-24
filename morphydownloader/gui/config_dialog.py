# morphydownloader/gui/config_dialog.py - Ventana de configuración completa

import os
import sys
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTextEdit, QCheckBox, QMessageBox, QTabWidget, QWidget, QFileDialog
)
from PySide6.QtGui import QFont, QPixmap, QIcon, QDesktopServices
from PySide6.QtCore import Qt, QUrl, QSettings
from ..config import Config

class ConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings('MorphyDownloader', 'Config')
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        self.setWindowTitle('Configuración de MorphyDownloader')
        self.setFixedSize(600, 500)
        self.setModal(True)
        
        # Icon
        try:
            icon_path = Config.get_asset_path('icon.png')
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
        except:
            pass  # Si no encuentra el icono, continúa sin él
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Título principal
        title_label = QLabel('¡Bienvenido a MorphyDownloader!')
        title_label.setFont(QFont('Inter', 18, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        subtitle_label = QLabel('Configuración inicial - Credenciales de Spotify')
        subtitle_label.setFont(QFont('Inter', 12))
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet('color: #888;')
        layout.addWidget(subtitle_label)
        
        # Tabs
        tabs = QTabWidget()
        
        # Tab 1: Credenciales
        cred_widget = QWidget()
        cred_layout = QVBoxLayout(cred_widget)
        
        # Instrucciones
        instructions_label = QLabel(
            'Para usar MorphyDownloader necesitas crear una aplicación en Spotify Developer:'
        )
        instructions_label.setFont(QFont('Inter', 11))
        instructions_label.setWordWrap(True)
        cred_layout.addWidget(instructions_label)
        
        # Pasos
        steps_text = QTextEdit()
        steps_text.setReadOnly(True)
        steps_text.setMaximumHeight(150)
        steps_text.setHtml("""
        <ol style="line-height: 1.5;">
            <li>Ve a <a href="https://developer.spotify.com/dashboard/">Spotify Developer Dashboard</a></li>
            <li>Inicia sesión con tu cuenta de Spotify</li>
            <li>Haz clic en "Create App"</li>
            <li>Llena los campos:
                <ul>
                    <li><b>App name:</b> MorphyDownloader (o cualquier nombre)</li>
                    <li><b>App description:</b> Music downloader</li>
                    <li><b>Redirect URI:</b> http://localhost:8080/callback</li>
                </ul>
            </li>
            <li>Acepta los términos y crea la app</li>
            <li>Copia el <b>Client ID</b> y <b>Client Secret</b> de tu nueva app</li>
        </ol>
        """)
        cred_layout.addWidget(steps_text)
        
        # Botón para abrir Spotify Developer
        open_spotify_btn = QPushButton('🌐 Abrir Spotify Developer Dashboard')
        open_spotify_btn.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl('https://developer.spotify.com/dashboard/')
        ))
        cred_layout.addWidget(open_spotify_btn)
        
        # Campos de entrada
        cred_layout.addWidget(QLabel('Client ID:'))
        self.client_id_entry = QLineEdit()
        self.client_id_entry.setPlaceholderText('Pega aquí tu Client ID de Spotify...')
        cred_layout.addWidget(self.client_id_entry)
        
        cred_layout.addWidget(QLabel('Client Secret:'))
        self.client_secret_entry = QLineEdit()
        self.client_secret_entry.setPlaceholderText('Pega aquí tu Client Secret de Spotify...')
        self.client_secret_entry.setEchoMode(QLineEdit.EchoMode.Password)
        cred_layout.addWidget(self.client_secret_entry)
        
        # Checkbox para mostrar/ocultar secret
        self.show_secret_cb = QCheckBox('Mostrar Client Secret')
        self.show_secret_cb.stateChanged.connect(self.toggle_secret_visibility)
        cred_layout.addWidget(self.show_secret_cb)
        
        tabs.addTab(cred_widget, '🔑 Credenciales')
        
        # Tab 2: Configuraciones adicionales
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        
        settings_layout.addWidget(QLabel('Calidad de audio:'))
        self.quality_entry = QLineEdit('192')
        self.quality_entry.setPlaceholderText('128, 192, 256, 320')
        settings_layout.addWidget(self.quality_entry)
        
        settings_layout.addWidget(QLabel('Directorio de descarga por defecto:'))
        default_output_layout = QHBoxLayout()
        self.output_dir_entry = QLineEdit(os.path.abspath('music'))
        browse_btn = QPushButton('📁')
        browse_btn.setFixedWidth(40)
        browse_btn.clicked.connect(self.browse_output_dir)
        default_output_layout.addWidget(self.output_dir_entry)
        default_output_layout.addWidget(browse_btn)
        settings_layout.addLayout(default_output_layout)
        
        # Checkbox para no mostrar esta ventana de nuevo
        self.dont_show_again_cb = QCheckBox('No mostrar esta configuración al inicio')
        settings_layout.addWidget(self.dont_show_again_cb)
        
        settings_layout.addStretch()
        tabs.addTab(settings_widget, '⚙️ Configuración')
        
        layout.addWidget(tabs)
        
        # Botones inferiores
        button_layout = QHBoxLayout()
        
        test_btn = QPushButton('🧪 Probar Conexión')
        test_btn.clicked.connect(self.test_credentials)
        
        save_btn = QPushButton('💾 Guardar y Continuar')
        save_btn.clicked.connect(self.save_and_close)
        save_btn.setDefault(True)
        
        cancel_btn = QPushButton('❌ Cancelar')
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(test_btn)
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        self.setup_styling()
        
    def setup_styling(self):
        """Aplicar estilos consistentes con la aplicación principal"""
        self.setStyleSheet(f"""
            QDialog {{
                background: {Config.BG_COLOR};
                color: {Config.FG_COLOR};
                font-family: 'Inter', sans-serif;
            }}
            QLabel {{
                color: {Config.FG_COLOR};
                font-weight: 500;
            }}
            QLineEdit {{
                background: {Config.ENTRY_BG};
                color: {Config.FG_COLOR};
                border-radius: 8px;
                padding: 10px 12px;
                border: 2px solid transparent;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 2px solid {Config.PRIMARY_COLOR};
            }}
            QTextEdit {{
                background: {Config.BG_COLOR};
                color: {Config.FG_COLOR};
                border: 1px solid #2a2f36;
                border-radius: 8px;
                padding: 10px;
            }}
            QPushButton {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                           stop: 0 {Config.PRIMARY_COLOR}, stop: 1 {Config.PRIMARY_DARK});
                color: white;
                border-radius: 8px;
                padding: 10px 16px;
                font-weight: 600;
                border: none;
                min-height: 16px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                           stop: 0 #e91e63, stop: 1 #c2185b);
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                           stop: 0 {Config.PRIMARY_DARK}, stop: 1 #8e0a1e);
            }}
            QCheckBox {{
                color: {Config.FG_COLOR};
                font-size: 13px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
            }}
            QCheckBox::indicator:unchecked {{
                background: {Config.ENTRY_BG};
                border: 2px solid #444;
                border-radius: 3px;
            }}
            QCheckBox::indicator:checked {{
                background: {Config.PRIMARY_COLOR};
                border: 2px solid {Config.PRIMARY_COLOR};
                border-radius: 3px;
            }}
            QTabWidget::pane {{
                border: 1px solid #2a2f36;
                border-radius: 8px;
                background: {Config.BG_COLOR};
            }}
            QTabBar::tab {{
                background: #2a2f36;
                color: {Config.FG_COLOR};
                padding: 10px 16px;
                margin: 2px;
                border-radius: 6px;
            }}
            QTabBar::tab:selected {{
                background: {Config.PRIMARY_COLOR};
                color: white;
            }}
        """)
    
    def toggle_secret_visibility(self, state):
        """Alternar visibilidad del Client Secret"""
        if state == Qt.CheckState.Checked.value:
            self.client_secret_entry.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.client_secret_entry.setEchoMode(QLineEdit.EchoMode.Password)
    
    def browse_output_dir(self):
        """Seleccionar directorio de salida"""
        folder = QFileDialog.getExistingDirectory(self, 'Seleccionar directorio de descarga')
        if folder:
            self.output_dir_entry.setText(folder)
    
    def test_credentials(self):
        """Probar las credenciales de Spotify"""
        client_id = self.client_id_entry.text().strip()
        client_secret = self.client_secret_entry.text().strip()
        
        if not client_id or not client_secret:
            QMessageBox.warning(self, 'Error', 
                              'Por favor ingresa tanto el Client ID como el Client Secret')
            return
        
        try:
            # Configurar variables de entorno temporalmente
            old_id = os.environ.get('SPOTIPY_CLIENT_ID')
            old_secret = os.environ.get('SPOTIPY_CLIENT_SECRET')
            
            os.environ['SPOTIFY_CLIENT_ID'] = client_id
            os.environ['SPOTIPY_CLIENT_SECRET'] = client_secret
            
            # Probar conexión
            try:
                from ..core.spotify_client import SpotifyClient
                spotify = SpotifyClient()
                
                # Hacer una consulta simple para verificar
                test_track = 'https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh'  # Never Gonna Give You Up
                track_info = spotify.get_track_info(test_track)
                
                QMessageBox.information(self, '¡Éxito!', 
                                      f'Conexión exitosa con Spotify.\n'
                                      f'Track de prueba: {track_info["track_title"]} - {track_info["artist_name"]}')
            except Exception as e:
                QMessageBox.critical(self, 'Error de Conexión', 
                                   f'No se pudo conectar con Spotify:\n{str(e)}\n\n'
                                   'Verifica que las credenciales sean correctas.')
                return
            
            # Restaurar variables anteriores
            if old_id:
                os.environ['SPOTIPY_CLIENT_ID'] = old_id
            else:
                os.environ.pop('SPOTIPY_CLIENT_ID', None)
            if old_secret:
                os.environ['SPOTIPY_CLIENT_SECRET'] = old_secret
            else:
                os.environ.pop('SPOTIPY_CLIENT_SECRET', None)
                
        except Exception as e:
            QMessageBox.critical(self, 'Error de Conexión', 
                               f'Error inesperado al probar conexión:\n{str(e)}')
    
    def save_and_close(self):
        """Guardar configuración y cerrar"""
        client_id = self.client_id_entry.text().strip()
        client_secret = self.client_secret_entry.text().strip()
        
        if not client_id or not client_secret:
            QMessageBox.warning(self, 'Error', 
                              'Por favor completa las credenciales de Spotify')
            return
        
        # Guardar en QSettings
        self.settings.setValue('spotify_client_id', client_id)
        self.settings.setValue('spotify_client_secret', client_secret)
        self.settings.setValue('audio_quality', self.quality_entry.text())
        self.settings.setValue('default_output_dir', self.output_dir_entry.text())
        self.settings.setValue('dont_show_config', self.dont_show_again_cb.isChecked())
        
        # Configurar variables de entorno
        os.environ['SPOTIPY_CLIENT_ID'] = client_id
        os.environ['SPOTIPY_CLIENT_SECRET'] = client_secret
        
        QMessageBox.information(self, '¡Configuración Guardada!', 
                              'La configuración se ha guardado correctamente.\n'
                              'Ya puedes usar MorphyDownloader.')
        
        self.accept()
    
    def load_settings(self):
        """Cargar configuración guardada"""
        if self.settings.value('spotify_client_id'):
            self.client_id_entry.setText(self.settings.value('spotify_client_id'))
        if self.settings.value('spotify_client_secret'):
            self.client_secret_entry.setText(self.settings.value('spotify_client_secret'))
        if self.settings.value('audio_quality'):
            self.quality_entry.setText(self.settings.value('audio_quality'))
        if self.settings.value('default_output_dir'):
            self.output_dir_entry.setText(self.settings.value('default_output_dir'))
        
        # Si ya está configurado, marcar el checkbox
        if self.settings.value('dont_show_config', False, type=bool):
            self.dont_show_again_cb.setChecked(True)

def should_show_config():
    """Verificar si se debe mostrar la ventana de configuración"""
    settings = QSettings('MorphyDownloader', 'Config')
    
    # Si el usuario marcó "no mostrar de nuevo" y ya tiene credenciales
    if settings.value('dont_show_config', False, type=bool):
        client_id = settings.value('spotify_client_id')
        client_secret = settings.value('spotify_client_secret')
        if client_id and client_secret:
            # Configurar variables de entorno
            os.environ['SPOTIPY_CLIENT_ID'] = client_id
            os.environ['SPOTIPY_CLIENT_SECRET'] = client_secret
            return False
    
    # Si no hay credenciales en variables de entorno
    if not os.environ.get('SPOTIPY_CLIENT_ID') or not os.environ.get('SPOTIPY_CLIENT_SECRET'):
        return True
    
    return False

def load_saved_config():
    """Cargar configuración guardada al inicio"""
    settings = QSettings('MorphyDownloader', 'Config')
    
    if settings.value('spotify_client_id') and settings.value('spotify_client_secret'):
        os.environ['SPOTIPY_CLIENT_ID'] = settings.value('spotify_client_id')
        os.environ['SPOTIPY_CLIENT_SECRET'] = settings.value('spotify_client_secret')