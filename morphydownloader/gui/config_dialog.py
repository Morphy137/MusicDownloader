# morphydownloader/gui/config_dialog.py
import os
import sys
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTextEdit, QCheckBox, QMessageBox, QTabWidget, QWidget, QFileDialog
)
from PySide6.QtGui import QFont, QIcon, QDesktopServices
from PySide6.QtCore import Qt, QUrl, QSettings
from ..config import Config

# Configuración de rutas de iconos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_PATH = os.path.join(BASE_DIR, '..', '..', 'assets')
ICONS_BASE_PATH = os.path.join(ASSETS_PATH, 'icons')
ICON_PATHS = {
    'app_icon': os.path.join(ASSETS_PATH, 'icon.ico'),
    'settings': os.path.join(ICONS_BASE_PATH, 'settings.svg'),
    'folder_browse': os.path.join(ICONS_BASE_PATH, 'folder_browse.svg'),
    'test': os.path.join(ICONS_BASE_PATH, 'test.svg'),
    'save': os.path.join(ICONS_BASE_PATH, 'save.svg'),
    'cancel': os.path.join(ICONS_BASE_PATH, 'cancel.svg'),
    'web': os.path.join(ICONS_BASE_PATH, 'web.svg')
}

class ConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings('MorphyDownloader', 'Config')
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        self.setWindowTitle('Configuración de MorphyDownloader')
        
        self.setMinimumSize(650, 900)
        self.resize(650, 900)
        self.setModal(True)
        
        # Configurar icono de aplicación
        app_icon_path = Config.get_asset_path(ICON_PATHS['app_icon'])
        if os.path.exists(app_icon_path):
            self.setWindowIcon(QIcon(app_icon_path))
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Título principal
        title_label = QLabel('¡Bienvenido a MorphyDownloader!')
        title_label.setFont(QFont('Inter', 18, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        subtitle_label = QLabel('Configuración inicial - Solo necesitas credenciales de Spotify')
        subtitle_label.setFont(QFont('Inter', 12))
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet('color: #888;')
        layout.addWidget(subtitle_label)
        
        # Tabs de configuración
        tabs = QTabWidget()
        
        cred_widget = self.create_credentials_tab()
        tabs.addTab(cred_widget, 'Credenciales')
        
        settings_widget = self.create_settings_tab()
        tabs.addTab(settings_widget, 'Configuración')
        
        layout.addWidget(tabs)
        
        # Botones de acción
        button_layout = QHBoxLayout()
        
        test_btn = QPushButton('Probar Credenciales')
        self._set_icon_or_text(test_btn, 'test', '🧪 Probar Credenciales')
        test_btn.clicked.connect(self.test_credentials_only)
        
        save_btn = QPushButton('Guardar y Continuar')
        self._set_icon_or_text(save_btn, 'save', '💾 Guardar y Continuar')
        save_btn.clicked.connect(self.save_and_close)
        save_btn.setDefault(True)
        
        cancel_btn = QPushButton('Cancelar')
        self._set_icon_or_text(cancel_btn, 'cancel', '❌ Cancelar')
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(test_btn)
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        self.setup_styling()
    
    def _set_icon_or_text(self, button, icon_key, fallback_text):
        """Establece icono o texto de respaldo para botones"""
        icon_path = Config.get_asset_path(ICON_PATHS.get(icon_key, ''))
        if os.path.exists(icon_path):
            button.setIcon(QIcon(icon_path))
            button.setText(fallback_text.split(' ', 1)[-1])  # Texto sin emoji
        else:
            button.setText(fallback_text)
    
    def create_credentials_tab(self):
        """Crear pestaña de configuración de credenciales de Spotify"""
        cred_widget = QWidget()
        cred_layout = QVBoxLayout(cred_widget)
        
        welcome_label = QLabel(
            'MorphyDownloader descarga audio en formato M4A de alta calidad '
            'directamente desde YouTube, sin necesidad de conversión.\n\n'
            'Solo necesitas configurar tus credenciales de Spotify:'
        )
        welcome_label.setFont(QFont('Inter', 11))
        welcome_label.setWordWrap(True)
        welcome_label.setStyleSheet('color: #2ecc71; background: #1a2f1a; padding: 15px; border-radius: 8px;')
        cred_layout.addWidget(welcome_label)
        
        instructions_label = QLabel(
            'Para usar MorphyDownloader necesitas crear una aplicación en Spotify Developer:'
        )
        instructions_label.setFont(QFont('Inter', 11))
        instructions_label.setWordWrap(True)
        cred_layout.addWidget(instructions_label)
        
        # Instrucciones paso a paso
        steps_text = QTextEdit()
        steps_text.setReadOnly(True)
        steps_text.setFixedHeight(200)
        steps_text.setHtml("""
        <ol style="line-height: 1.6;">
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
        open_spotify_btn = QPushButton('Abrir Spotify Developer Dashboard')
        self._set_icon_or_text(open_spotify_btn, 'web', '🌐 Abrir Spotify Developer Dashboard')
        open_spotify_btn.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl('https://developer.spotify.com/dashboard/')
        ))
        cred_layout.addWidget(open_spotify_btn)
        
        # Campos de entrada para credenciales
        cred_layout.addWidget(QLabel('Client ID:'))
        self.client_id_entry = QLineEdit()
        self.client_id_entry.setPlaceholderText('Pega aquí tu Client ID de Spotify...')
        cred_layout.addWidget(self.client_id_entry)
        
        cred_layout.addWidget(QLabel('Client Secret:'))
        self.client_secret_entry = QLineEdit()
        self.client_secret_entry.setPlaceholderText('Pega aquí tu Client Secret de Spotify...')
        self.client_secret_entry.setEchoMode(QLineEdit.EchoMode.Password)
        cred_layout.addWidget(self.client_secret_entry)
        
        # Checkbox para mostrar/ocultar client secret
        self.show_secret_cb = QCheckBox('Mostrar Client Secret')
        self.show_secret_cb.stateChanged.connect(self.toggle_secret_visibility)
        cred_layout.addWidget(self.show_secret_cb)
        
        cred_layout.addStretch()
        return cred_widget
    
    def create_settings_tab(self):
        """Crear pestaña de configuraciones adicionales"""
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        
        format_info = QLabel(
            '🎵 MorphyDownloader descarga audio en formato M4A de alta calidad.\n'
            'Este formato es compatible con todos los dispositivos y reproductores modernos, '
            'incluyendo iPhone, Android, Windows, Mac y Linux.'
        )
        format_info.setFont(QFont('Inter', 11))
        format_info.setWordWrap(True)
        format_info.setStyleSheet('color: #3498db; background: #1a2a3a; padding: 15px; border-radius: 8px;')
        settings_layout.addWidget(format_info)
        
        settings_layout.addWidget(QLabel('Directorio de descarga por defecto:'))
        default_output_layout = QHBoxLayout()
        self.output_dir_entry = QLineEdit(os.path.abspath('music'))
        
        # Botón para seleccionar carpeta
        browse_btn = QPushButton()
        self._set_icon_or_text(browse_btn, 'folder_browse', '📁')
        browse_btn.setFixedWidth(40)
        browse_btn.setToolTip('Seleccionar carpeta')
        browse_btn.clicked.connect(self.browse_output_dir)
        
        default_output_layout.addWidget(self.output_dir_entry)
        default_output_layout.addWidget(browse_btn)
        settings_layout.addLayout(default_output_layout)
        
        # Opción para no mostrar configuración al inicio
        self.dont_show_again_cb = QCheckBox('No mostrar esta configuración al inicio')
        settings_layout.addWidget(self.dont_show_again_cb)
        
        settings_layout.addStretch()
        
        return settings_widget
    
    def toggle_secret_visibility(self, state):
        """Alternar entre mostrar/ocultar el Client Secret"""
        if state == Qt.CheckState.Checked.value:
            self.client_secret_entry.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.client_secret_entry.setEchoMode(QLineEdit.EchoMode.Password)
    
    def browse_output_dir(self):
        """Abrir diálogo para seleccionar directorio de descarga"""
        folder = QFileDialog.getExistingDirectory(self, 'Seleccionar directorio de descarga')
        if folder:
            self.output_dir_entry.setText(folder)
    
    def test_credentials_only(self):
        """Probar únicamente las credenciales de Spotify"""
        if self.test_credentials():
            QMessageBox.information(self, '✅ ¡Éxito!', 
                                  '¡Las credenciales de Spotify están correctas!\n'
                                  'MorphyDownloader está listo para usar.')
        else:
            QMessageBox.warning(self, '❌ Error', 
                              'Las credenciales de Spotify son incorrectas.\n'
                              'Verifica tu Client ID y Client Secret.')
    
    def test_credentials(self):
        """Validar conexión con las credenciales de Spotify"""
        client_id = self.client_id_entry.text().strip()
        client_secret = self.client_secret_entry.text().strip()
        
        if not client_id or not client_secret:
            return False
        
        try:
            # Configurar variables de entorno temporalmente para la prueba
            old_id = os.environ.get('SPOTIPY_CLIENT_ID')
            old_secret = os.environ.get('SPOTIPY_CLIENT_SECRET')
            
            os.environ['SPOTIPY_CLIENT_ID'] = client_id
            os.environ['SPOTIPY_CLIENT_SECRET'] = client_secret
            
            try:
                from ..core.spotify_client import SpotifyClient
                spotify = SpotifyClient()
                
                # Hacer una consulta de prueba
                test_track = 'https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh'
                track_info = spotify.get_track_info(test_track)
                return True
                
            except Exception:
                return False
            finally:
                # Restaurar variables de entorno anteriores
                if old_id:
                    os.environ['SPOTIPY_CLIENT_ID'] = old_id
                else:
                    os.environ.pop('SPOTIPY_CLIENT_ID', None)
                if old_secret:
                    os.environ['SPOTIPY_CLIENT_SECRET'] = old_secret
                else:
                    os.environ.pop('SPOTIPY_CLIENT_SECRET', None)
                    
        except Exception:
            return False
    
    def save_and_close(self):
        """Guardar configuración y cerrar diálogo"""
        client_id = self.client_id_entry.text().strip()
        client_secret = self.client_secret_entry.text().strip()
        
        if not client_id or not client_secret:
            QMessageBox.warning(self, 'Error', 
                              'Por favor completa las credenciales de Spotify')
            return
        
        # Validar credenciales antes de guardar
        if not self.test_credentials():
            reply = QMessageBox.question(
                self, 
                '⚠️ Credenciales incorrectas',
                'Las credenciales de Spotify parecen incorrectas.\n'
                '¿Deseas guardar de todos modos?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                return
        
        # Guardar configuración en QSettings
        self.settings.setValue('spotify_client_id', client_id)
        self.settings.setValue('spotify_client_secret', client_secret)
        self.settings.setValue('default_output_dir', self.output_dir_entry.text())
        self.settings.setValue('dont_show_config', self.dont_show_again_cb.isChecked())
        
        # Configurar variables de entorno
        os.environ['SPOTIPY_CLIENT_ID'] = client_id
        os.environ['SPOTIPY_CLIENT_SECRET'] = client_secret
        
        QMessageBox.information(self, '✅ ¡Configuración Guardada!', 
                              'La configuración se ha guardado correctamente.\n'
                              'Ya puedes usar MorphyDownloader para descargar audio M4A de alta calidad.')
        
        self.accept()
    
    def load_settings(self):
        """Cargar configuración guardada previamente"""
        if self.settings.value('spotify_client_id'):
            self.client_id_entry.setText(self.settings.value('spotify_client_id'))
        if self.settings.value('spotify_client_secret'):
            self.client_secret_entry.setText(self.settings.value('spotify_client_secret'))
        if self.settings.value('default_output_dir'):
            self.output_dir_entry.setText(self.settings.value('default_output_dir'))
        
        if self.settings.value('dont_show_config', False, type=bool):
            self.dont_show_again_cb.setChecked(True)
    
    def setup_styling(self):
        """Aplicar estilos CSS consistentes con la aplicación principal"""
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

# Funciones de utilidad para la configuración
def should_show_config():
    """Determinar si se debe mostrar la ventana de configuración al inicio"""
    settings = QSettings('MorphyDownloader', 'Config')
    
    if settings.value('dont_show_config', False, type=bool):
        client_id = settings.value('spotify_client_id')
        client_secret = settings.value('spotify_client_secret')
        if client_id and client_secret:
            os.environ['SPOTIPY_CLIENT_ID'] = client_id
            os.environ['SPOTIPY_CLIENT_SECRET'] = client_secret
            return False
    
    if not os.environ.get('SPOTIPY_CLIENT_ID') or not os.environ.get('SPOTIPY_CLIENT_SECRET'):
        return True
    
    return False

def load_saved_config():
    """Cargar configuración guardada al iniciar la aplicación"""
    settings = QSettings('MorphyDownloader', 'Config')
    
    if settings.value('spotify_client_id') and settings.value('spotify_client_secret'):
        os.environ['SPOTIPY_CLIENT_ID'] = settings.value('spotify_client_id')
        os.environ['SPOTIPY_CLIENT_SECRET'] = settings.value('spotify_client_secret')