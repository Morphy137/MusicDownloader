# morphydownloader/gui/config_dialog.py
import os
import sys
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTextEdit, QCheckBox, QMessageBox, QTabWidget, QWidget, 
    QFileDialog, QComboBox, QGroupBox
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
    'folder_browse': os.path.join(ICONS_BASE_PATH, 'folder-browse.svg'),
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
        self.check_ffmpeg_status()
        
    def init_ui(self):
        self.setWindowTitle('Configuración de MorphyDownloader')
        
        self.setMinimumSize(700, 950)
        self.resize(700, 950)
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
        
        subtitle_label = QLabel('Configuración inicial - Credenciales de Spotify y formato de audio')
        subtitle_label.setFont(QFont('Inter', 12))
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet('color: #888;')
        layout.addWidget(subtitle_label)
        
        # Tabs de configuración
        tabs = QTabWidget()
        
        cred_widget = self.create_credentials_tab()
        tabs.addTab(cred_widget, 'Credenciales')
        
        format_widget = self.create_format_tab()
        tabs.addTab(format_widget, 'Formato de Audio')
        
        settings_widget = self.create_settings_tab()
        tabs.addTab(settings_widget, 'Configuración')
        
        layout.addWidget(tabs)
        
        # Botones de acción
        button_layout = QHBoxLayout()
        
        test_btn = QPushButton('Probar Credenciales')
        self._set_icon_or_text(test_btn, 'test', 'Test Credenciales')
        test_btn.clicked.connect(self.test_credentials_only)
        
        save_btn = QPushButton('Guardar y Continuar')
        self._set_icon_or_text(save_btn, 'save', 'Guardar y Continuar')
        save_btn.clicked.connect(self.save_and_close)
        save_btn.setDefault(True)
        
        cancel_btn = QPushButton('Cancelar')
        self._set_icon_or_text(cancel_btn, 'cancel', 'Cancelar')
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(test_btn)
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        self.setup_styling()
    
    def _set_icon_or_text(self, button, icon_key, fallback_text):
        icon_path = Config.get_asset_path(ICON_PATHS.get(icon_key, ''))
        if os.path.exists(icon_path):
            button.setIcon(QIcon(icon_path))
            button.setText('')  # Solo icono, sin texto ni emoji
        else:
            button.setText(fallback_text)
    
    def create_credentials_tab(self):
        """Crear pestaña de configuración de credenciales de Spotify"""
        cred_widget = QWidget()
        cred_layout = QVBoxLayout(cred_widget)
        
        welcome_label = QLabel(
            'MorphyDownloader descarga audio de alta calidad desde YouTube '
            'con metadatos completos de Spotify.\n\n'
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
        self._set_icon_or_text(open_spotify_btn, 'web', 'Abrir Spotify Developer Dashboard')
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
    
    def create_format_tab(self):
        """Crear pestaña de configuración de formato de audio"""
        format_widget = QWidget()
        format_layout = QVBoxLayout(format_widget)
        
        # Grupo de selección de formato
        format_group = QGroupBox("Formato de Audio")
        format_group_layout = QVBoxLayout(format_group)
        
        # Selector de formato
        format_layout_inner = QHBoxLayout()
        format_layout_inner.addWidget(QLabel('Formato de descarga:'))
        self.format_combo = QComboBox()
        self.format_combo.addItems(['m4a', 'mp3'])
        self.format_combo.currentTextChanged.connect(self.on_format_changed)
        format_layout_inner.addWidget(self.format_combo)
        format_layout_inner.addStretch()
        format_group_layout.addLayout(format_layout_inner)
        
        # Información del formato seleccionado
        self.format_info_label = QLabel()
        self.format_info_label.setWordWrap(True)
        self.format_info_label.setStyleSheet('color: #3498db; background: #1a2a3a; padding: 15px; border-radius: 8px;')
        format_group_layout.addWidget(self.format_info_label)
        
        format_layout.addWidget(format_group)
        
        # Sección FFmpeg
        ffmpeg_group = QGroupBox("FFmpeg (Requerido para MP3)")
        ffmpeg_layout = QVBoxLayout(ffmpeg_group)
        
        # Estado de FFmpeg
        self.ffmpeg_status_label = QLabel()
        self.ffmpeg_status_label.setWordWrap(True)
        ffmpeg_layout.addWidget(self.ffmpeg_status_label)
        
        # Instrucciones de instalación de FFmpeg
        ffmpeg_instructions = QTextEdit()
        ffmpeg_instructions.setReadOnly(True)
        ffmpeg_instructions.setFixedHeight(250)
        ffmpeg_instructions.setHtml("""
        <h3>Instalación de FFmpeg:</h3>
        <h4>Windows:</h4>
        <ol>
            <li>Descarga FFmpeg desde <a href="https://ffmpeg.org/download.html#build-windows">ffmpeg.org</a></li>
            <li>Extrae el archivo zip a una carpeta (ej: C:\\ffmpeg)</li>
            <li>Agrega la carpeta bin al PATH del sistema:
                <ul>
                    <li>Busca "Variables de entorno" en el menú inicio</li>
                    <li>Edita las variables de entorno del sistema</li>
                    <li>Edita la variable PATH</li>
                    <li>Agrega: C:\\ffmpeg\\bin</li>
                </ul>
            </li>
            <li>Reinicia el programa</li>
        </ol>
        
        <h4>macOS:</h4>
        <ol>
            <li>Instala Homebrew si no lo tienes: <code>/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"</code></li>
            <li>Ejecuta en Terminal: <code>brew install ffmpeg</code></li>
        </ol>
        
        <h4>Linux (Ubuntu/Debian):</h4>
        <ol>
            <li>Ejecuta en Terminal: <code>sudo apt update && sudo apt install ffmpeg</code></li>
        </ol>
        """)
        ffmpeg_layout.addWidget(ffmpeg_instructions)
        
        # Botón para verificar FFmpeg
        check_ffmpeg_btn = QPushButton('Verificar FFmpeg')
        check_ffmpeg_btn.clicked.connect(self.check_ffmpeg_status)
        ffmpeg_layout.addWidget(check_ffmpeg_btn)
        
        format_layout.addWidget(ffmpeg_group)
        format_layout.addStretch()
        
        return format_widget
    
    def create_settings_tab(self):
        """Crear pestaña de configuraciones adicionales"""
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        
        # Selector de calidad
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel('Calidad de audio:'))
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(Config.SUPPORTED_QUALITY)
        self.quality_combo.setCurrentText(Config.DEFAULT_QUALITY)
        quality_layout.addWidget(self.quality_combo)
        quality_layout.addStretch()
        settings_layout.addLayout(quality_layout)
        
        quality_info = QLabel(
            'La calidad se aplica solo a MP3. M4A siempre usa la mejor calidad disponible.'
        )
        quality_info.setFont(QFont('Inter', 10))
        quality_info.setStyleSheet('color: #888; font-style: italic;')
        settings_layout.addWidget(quality_info)
        
        settings_layout.addWidget(QLabel('Directorio de descarga por defecto:'))
        default_output_layout = QHBoxLayout()
        self.output_dir_entry = QLineEdit(os.path.abspath('music'))
        
        # Botón para seleccionar carpeta
        browse_btn = QPushButton()
        self._set_icon_or_text(browse_btn, 'folder_browse', 'Seleccionar')
        browse_btn.setFixedWidth(80)
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
    
    def on_format_changed(self, format_type):
        """Actualizar información cuando se cambie el formato"""
        format_info = Config.get_format_info(format_type)
        self.format_info_label.setText(
            f"{format_info['description']}\n{format_info['quality_note']}"
        )
        
        # Actualizar color según si requiere FFmpeg
        if format_info['requires_ffmpeg']:
            if Config.check_ffmpeg():
                self.format_info_label.setStyleSheet('color: #2ecc71; background: #1a2f1a; padding: 15px; border-radius: 8px;')
            else:
                self.format_info_label.setStyleSheet('color: #e74c3c; background: #2f1a1a; padding: 15px; border-radius: 8px;')
        else:
            self.format_info_label.setStyleSheet('color: #3498db; background: #1a2a3a; padding: 15px; border-radius: 8px;')
    
    def check_ffmpeg_status(self):
        """Verificar y mostrar el estado de FFmpeg"""
        if Config.check_ffmpeg():
            ffmpeg_path = Config.get_ffmpeg_path()
            self.ffmpeg_status_label.setText(
                f"✅ FFmpeg encontrado: {ffmpeg_path}\nPuedes usar formato MP3 sin problemas."
            )
            self.ffmpeg_status_label.setStyleSheet('color: #2ecc71; background: #1a2f1a; padding: 10px; border-radius: 8px;')
        else:
            self.ffmpeg_status_label.setText(
                "⚠️ FFmpeg no encontrado\nInstala FFmpeg para usar formato MP3. M4A funcionará sin FFmpeg."
            )
            self.ffmpeg_status_label.setStyleSheet('color: #e74c3c; background: #2f1a1a; padding: 10px; border-radius: 8px;')
        
        # Actualizar información del formato actual
        current_format = self.format_combo.currentText()
        self.on_format_changed(current_format)
    
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
        
        # Validar que si se selecciona MP3, FFmpeg esté disponible
        selected_format = self.format_combo.currentText()
        if selected_format == 'mp3' and not Config.check_ffmpeg():
            reply = QMessageBox.question(
                self, 
                '⚠️ FFmpeg no encontrado',
                'Has seleccionado formato MP3 pero FFmpeg no está instalado.\n'
                '¿Deseas continuar con M4A en su lugar?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                self.format_combo.setCurrentText('m4a')
                selected_format = 'm4a'
            else:
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
        self.settings.setValue('audio_format', selected_format)
        self.settings.setValue('audio_quality', self.quality_combo.currentText())
        self.settings.setValue('default_output_dir', self.output_dir_entry.text())
        self.settings.setValue('dont_show_config', self.dont_show_again_cb.isChecked())
        
        # Configurar variables de entorno
        os.environ['SPOTIPY_CLIENT_ID'] = client_id
        os.environ['SPOTIPY_CLIENT_SECRET'] = client_secret
        
        format_info = Config.get_format_info(selected_format)
        QMessageBox.information(self, '✅ ¡Configuración Guardada!', 
                              f'Configuración guardada correctamente:\n'
                              f'• Formato: {selected_format.upper()}\n'
                              f'• Calidad: {self.quality_combo.currentText()} kbps\n'
                              f'• FFmpeg: {"✅ Disponible" if Config.check_ffmpeg() else "❌ No disponible"}\n\n'
                              f'{format_info["description"]}')
        
        self.accept()
    
    def load_settings(self):
        """Cargar configuración guardada previamente"""
        if self.settings.value('spotify_client_id'):
            self.client_id_entry.setText(self.settings.value('spotify_client_id'))
        if self.settings.value('spotify_client_secret'):
            self.client_secret_entry.setText(self.settings.value('spotify_client_secret'))
        if self.settings.value('default_output_dir'):
            self.output_dir_entry.setText(self.settings.value('default_output_dir'))
        
        # Cargar formato de audio
        saved_format = self.settings.value('audio_format', Config.DEFAULT_FORMAT)
        if saved_format in Config.SUPPORTED_FORMATS:
            self.format_combo.setCurrentText(saved_format)
        
        # Cargar calidad de audio
        saved_quality = self.settings.value('audio_quality', Config.DEFAULT_QUALITY)
        if saved_quality in Config.SUPPORTED_QUALITY:
            self.quality_combo.setCurrentText(saved_quality)
        
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
            QLineEdit, QComboBox {{
                background: {Config.ENTRY_BG};
                color: {Config.FG_COLOR};
                border-radius: 8px;
                padding: 10px 12px;
                border: 2px solid transparent;
                font-size: 13px;
            }}
            QLineEdit:focus, QComboBox:focus {{
                border: 2px solid {Config.PRIMARY_COLOR};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                width: 12px;
                height: 12px;
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
            QGroupBox {{
                font-weight: bold;
                border: 2px solid #2a2f36;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
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

def get_saved_audio_format():
    """Obtener el formato de audio guardado"""
    settings = QSettings('MorphyDownloader', 'Config')
    return settings.value('audio_format', Config.DEFAULT_FORMAT)

def get_saved_audio_quality():
    """Obtener la calidad de audio guardada"""
    settings = QSettings('MorphyDownloader', 'Config')
    return settings.value('audio_quality', Config.DEFAULT_QUALITY)