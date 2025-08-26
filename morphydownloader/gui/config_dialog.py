# morphydownloader/gui/config_dialog.py - Ventana de configuración mejorada con FFmpeg
import os
import sys
import shutil
import subprocess
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTextEdit, QCheckBox, QMessageBox, QTabWidget, QWidget, QFileDialog,
    QProgressBar, QGroupBox, QFrame
)
from PySide6.QtGui import QFont, QPixmap, QIcon, QDesktopServices, QTextCursor
from PySide6.QtCore import Qt, QUrl, QSettings, QSize, QThread, Signal
from ..config import Config

class FFmpegInstallThread(QThread):
    """Thread para verificar FFmpeg sin bloquear UI"""
    status_updated = Signal(str, str)  # message, color
    finished_check = Signal(bool, str)  # found, path
    
    def run(self):
        self.status_updated.emit("🔍 Verificando FFmpeg...", "#888888")
        
        # Verificar en PATH
        ffmpeg_path = shutil.which('ffmpeg') or shutil.which('ffmpeg.exe')
        if ffmpeg_path:
            self.status_updated.emit(f"✅ FFmpeg encontrado en: {ffmpeg_path}", "#2ecc71")
            self.finished_check.emit(True, ffmpeg_path)
            return
        
        # Verificar en ubicaciones comunes de Windows
        if sys.platform.startswith('win'):
            common_paths = [
                r"C:\ffmpeg\bin\ffmpeg.exe",
                r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
                r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe",
                os.path.expanduser(r"~\ffmpeg\bin\ffmpeg.exe"),
                os.path.join(os.path.dirname(sys.executable), "ffmpeg.exe")
            ]
            
            for path in common_paths:
                if os.path.exists(path):
                    self.status_updated.emit(f"✅ FFmpeg encontrado en: {path}", "#2ecc71")
                    self.finished_check.emit(True, path)
                    return
        
        # No encontrado
        self.status_updated.emit("❌ FFmpeg no encontrado", "#e74c3c")
        self.finished_check.emit(False, "")

class ConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings('MorphyDownloader', 'Config')
        self.ffmpeg_thread = None
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        self.setWindowTitle('Configuración de MorphyDownloader')
        # ❌ PROBLEMA: setFixedSize causa redimensionado al mover
        # self.setFixedSize(700, 600)  # REMOVER ESTA LÍNEA
        
        # ✅ SOLUCIÓN: Usar tamaño mínimo y inicial sin bloquear
        self.setMinimumSize(720, 640)  # Tamaño mínimo más grande
        self.resize(750, 680)          # Tamaño inicial cómodo
        self.setModal(True)
        
        # Icon - Usar icon.png o icon.ico
        try:
            icon_path = Config.get_asset_path('icon.ico')
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
        except Exception:
            pass
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Título principal
        title_label = QLabel('¡Bienvenido a MorphyDownloader!')
        title_label.setFont(QFont('Inter', 18, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        subtitle_label = QLabel('Configuración inicial - Dependencias y credenciales')
        subtitle_label.setFont(QFont('Inter', 12))
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet('color: #888;')
        layout.addWidget(subtitle_label)
        
        # Tabs
        tabs = QTabWidget()
        
        # Tab 1: FFmpeg
        ffmpeg_widget = self.create_ffmpeg_tab()
        tabs.addTab(ffmpeg_widget, '🎬 FFmpeg')
        
        # Tab 2: Credenciales
        cred_widget = self.create_credentials_tab()
        tabs.addTab(cred_widget, '🔑 Credenciales')
        
        # Tab 3: Configuraciones adicionales
        settings_widget = self.create_settings_tab()
        tabs.addTab(settings_widget, '⚙️ Configuración')
        
        layout.addWidget(tabs)
        
        # Botones inferiores
        button_layout = QHBoxLayout()
        
        test_btn = QPushButton('🧪 Probar Todo')
        test_btn.clicked.connect(self.test_all_configuration)
        
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
        
        # Verificar FFmpeg al abrir
        self.check_ffmpeg_status()
        
    def create_ffmpeg_tab(self):
        """Crear tab de configuración de FFmpeg con dimensiones fijas"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Descripción de FFmpeg
        desc_label = QLabel(
            'FFmpeg es necesario para convertir el audio descargado a MP3 con buena calidad.'
        )
        desc_label.setFont(QFont('Inter', 11))
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Estado actual
        status_group = QGroupBox("Estado Actual")
        status_layout = QVBoxLayout(status_group)
        
        self.ffmpeg_status_label = QLabel('🔍 Verificando...')
        self.ffmpeg_status_label.setFont(QFont('JetBrains Mono', 10))
        status_layout.addWidget(self.ffmpeg_status_label)
        
        # Botón verificar
        verify_btn = QPushButton('🔄 Verificar FFmpeg')
        verify_btn.clicked.connect(self.check_ffmpeg_status)
        status_layout.addWidget(verify_btn)
        
        layout.addWidget(status_group)
        
        # ✅ SOLUCIÓN: Instrucciones con altura FIJA para evitar redimensionado
        install_group = QGroupBox("Instalación Manual")
        install_layout = QVBoxLayout(install_group)
        
        instructions_text = QTextEdit()
        instructions_text.setReadOnly(True)
        # ✅ Altura FIJA para evitar redimensionado automático
        instructions_text.setFixedHeight(280)  # Altura fija específica
        instructions_text.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        instructions_text.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        instructions_text.setHtml("""
        <div style="line-height: 1.6; font-family: 'Inter', sans-serif;">
        <h3 style="color: #DC143C; margin-top: 0;">📋 Pasos para instalar FFmpeg:</h3>
        
        <h4>🪟 Windows:</h4>
        <ol>
            <li>Ve a <a href="https://www.gyan.dev/ffmpeg/builds/">gyan.dev/ffmpeg/builds</a></li>
            <li>Descarga <b>"release builds" → "ffmpeg-release-essentials.zip"</b></li>
            <li>Extrae el archivo ZIP en <b>C:\\ffmpeg\\</b></li>
            <li>Agrega <b>C:\\ffmpeg\\bin</b> a las variables de entorno PATH:
                <ul>
                    <li>Busca "Variables de entorno" en el menú inicio</li>
                    <li>Clic en "Variables de entorno..."</li>
                    <li>Selecciona "Path" → "Editar" → "Nuevo"</li>
                    <li>Agrega: <b>C:\\ffmpeg\\bin</b></li>
                    <li>Acepta y reinicia MorphyDownloader</li>
                </ul>
            </li>
        </ol>
        
        <h4>🍎 macOS:</h4>
        <pre style="background: #2a2f36; padding: 10px; border-radius: 6px; color: #e1e1e1;">brew install ffmpeg</pre>
        
        <h4>🐧 Linux:</h4>
        <pre style="background: #2a2f36; padding: 10px; border-radius: 6px; color: #e1e1e1;">sudo apt install ffmpeg  # Ubuntu/Debian
    sudo dnf install ffmpeg  # Fedora
    sudo pacman -S ffmpeg   # Arch</pre>
        </div>
        """)
        install_layout.addWidget(instructions_text)
        
        # Botones de ayuda
        buttons_layout = QHBoxLayout()
        
        download_btn = QPushButton('🌐 Descargar FFmpeg (Windows)')
        download_btn.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl('https://www.gyan.dev/ffmpeg/builds/')
        ))
        
        path_btn = QPushButton('🔧 Configurar PATH (Windows)')
        path_btn.clicked.connect(self.show_path_instructions)
        
        buttons_layout.addWidget(download_btn)
        buttons_layout.addWidget(path_btn)
        install_layout.addLayout(buttons_layout)
        
        layout.addWidget(install_group)
        layout.addStretch()
        
        return widget
    
    def create_credentials_tab(self):
        """Crear tab de credenciales con scroll si es necesario"""
        cred_widget = QWidget()
        cred_layout = QVBoxLayout(cred_widget)
        
        # Instrucciones
        instructions_label = QLabel(
            'Para usar MorphyDownloader necesitas crear una aplicación en Spotify Developer:'
        )
        instructions_label.setFont(QFont('Inter', 11))
        instructions_label.setWordWrap(True)
        cred_layout.addWidget(instructions_label)
        
        # ✅ Pasos con altura fija también
        steps_text = QTextEdit()
        steps_text.setReadOnly(True)
        steps_text.setFixedHeight(180)  # Altura fija
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
        
        cred_layout.addStretch()  # Añadir stretch al final
        return cred_widget
    
    def resizeEvent(self, event):
        """Manejar eventos de redimensionado para prevenir cambios automáticos"""
        # Solo permitir redimensionado si es iniciado por el usuario
        if hasattr(self, '_user_resizing') and not self._user_resizing:
            event.ignore()
            return
        super().resizeEvent(event)

    def moveEvent(self, event):
        """Manejar movimiento de ventana sin redimensionado automático"""
        # Marcar que NO estamos redimensionando durante el movimiento
        self._user_resizing = False
        super().moveEvent(event)

    def mousePressEvent(self, event):
        """Detectar inicio de redimensionado por usuario"""
        self._user_resizing = True
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Detectar fin de redimensionado por usuario"""
        self._user_resizing = False
        super().mouseReleaseEvent(event)
    
    def create_settings_tab(self):
        """Crear tab de configuraciones adicionales"""
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        
        settings_layout.addWidget(QLabel('Calidad de audio:'))
        self.quality_entry = QLineEdit('192')
        self.quality_entry.setPlaceholderText('128, 192, 256, 320')
        settings_layout.addWidget(self.quality_entry)
        
        settings_layout.addWidget(QLabel('Directorio de descarga por defecto:'))
        default_output_layout = QHBoxLayout()
        self.output_dir_entry = QLineEdit(os.path.abspath('music'))
        
        # Botón browse con icono
        browse_btn = QPushButton('📁')
        browse_btn.setFixedWidth(40)
        browse_btn.setToolTip('Seleccionar carpeta')
        browse_btn.clicked.connect(self.browse_output_dir)
        
        default_output_layout.addWidget(self.output_dir_entry)
        default_output_layout.addWidget(browse_btn)
        settings_layout.addLayout(default_output_layout)
        
        # Checkbox para no mostrar esta ventana de nuevo
        self.dont_show_again_cb = QCheckBox('No mostrar esta configuración al inicio')
        settings_layout.addWidget(self.dont_show_again_cb)
        
        settings_layout.addStretch()
        
        return settings_widget
    
    def check_ffmpeg_status(self):
        """Verificar estado de FFmpeg"""
        if self.ffmpeg_thread and self.ffmpeg_thread.isRunning():
            return
            
        self.ffmpeg_thread = FFmpegInstallThread()
        self.ffmpeg_thread.status_updated.connect(self.update_ffmpeg_status)
        self.ffmpeg_thread.finished_check.connect(self.handle_ffmpeg_result)
        self.ffmpeg_thread.start()
    
    def update_ffmpeg_status(self, message, color):
        """Actualizar status de FFmpeg"""
        self.ffmpeg_status_label.setText(f'<span style="color: {color};">{message}</span>')
    
    def handle_ffmpeg_result(self, found, path):
        """Manejar resultado de verificación de FFmpeg"""
        if found:
            self.settings.setValue('ffmpeg_path', path)
            self.settings.setValue('ffmpeg_available', True)
        else:
            self.settings.setValue('ffmpeg_available', False)
    
    def show_path_instructions(self):
        """Mostrar instrucciones detalladas para configurar PATH"""
        QMessageBox.information(
            self, 
            'Configurar PATH en Windows',
            '🔧 Pasos detallados para agregar FFmpeg al PATH:\n\n'
            '1. Presiona Win + R, escribe "sysdm.cpl" y presiona Enter\n'
            '2. Ve a la pestaña "Opciones avanzadas"\n'
            '3. Clic en "Variables de entorno..."\n'
            '4. En "Variables del sistema", busca y selecciona "Path"\n'
            '5. Clic en "Editar..."\n'
            '6. Clic en "Nuevo"\n'
            '7. Escribe: C:\\ffmpeg\\bin\n'
            '8. Clic "Aceptar" en todas las ventanas\n'
            '9. Reinicia MorphyDownloader\n\n'
            '💡 Tip: También puedes buscar "Variables de entorno" en el menú inicio.'
        )
    
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
    
    def test_all_configuration(self):
        """Probar toda la configuración"""
        # Test FFmpeg
        ffmpeg_ok = self.test_ffmpeg()
        
        # Test Spotify
        spotify_ok = self.test_credentials()
        
        if ffmpeg_ok and spotify_ok:
            QMessageBox.information(self, '✅ ¡Éxito!', 
                                  '¡Toda la configuración está correcta!\n'
                                  'MorphyDownloader está listo para usar.')
        else:
            issues = []
            if not ffmpeg_ok:
                issues.append('• FFmpeg no está disponible')
            if not spotify_ok:
                issues.append('• Credenciales de Spotify incorrectas')
            
            QMessageBox.warning(self, '⚠️ Problemas encontrados', 
                              f'Se encontraron los siguientes problemas:\n\n' + 
                              '\n'.join(issues) + 
                              '\n\nPor favor, corrige estos problemas antes de continuar.')
    
    def test_ffmpeg(self):
        """Probar FFmpeg"""
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def test_credentials(self):
        """Probar las credenciales de Spotify"""
        client_id = self.client_id_entry.text().strip()
        client_secret = self.client_secret_entry.text().strip()
        
        if not client_id or not client_secret:
            return False
        
        try:
            # Configurar variables de entorno temporalmente
            old_id = os.environ.get('SPOTIPY_CLIENT_ID')
            old_secret = os.environ.get('SPOTIPY_CLIENT_SECRET')
            
            os.environ['SPOTIPY_CLIENT_ID'] = client_id
            os.environ['SPOTIPY_CLIENT_SECRET'] = client_secret
            
            # Probar conexión
            try:
                from ..core.spotify_client import SpotifyClient
                spotify = SpotifyClient()
                
                # Hacer una consulta simple para verificar
                test_track = 'https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh'
                track_info = spotify.get_track_info(test_track)
                return True
                
            except Exception:
                return False
            finally:
                # Restaurar variables anteriores
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
        """Guardar configuración y cerrar"""
        client_id = self.client_id_entry.text().strip()
        client_secret = self.client_secret_entry.text().strip()
        
        # Verificar configuración mínima
        if not client_id or not client_secret:
            QMessageBox.warning(self, 'Error', 
                              'Por favor completa las credenciales de Spotify')
            return
        
        # Verificar FFmpeg
        if not self.test_ffmpeg():
            reply = QMessageBox.question(
                self, 
                '⚠️ FFmpeg no encontrado',
                'FFmpeg no está instalado o no se encuentra en el PATH.\n'
                'Sin FFmpeg, es posible que las descargas no funcionen correctamente.\n\n'
                '¿Deseas continuar de todos modos?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
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
        
        QMessageBox.information(self, '✅ ¡Configuración Guardada!', 
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
        
        if self.settings.value('dont_show_config', False, type=bool):
            self.dont_show_again_cb.setChecked(True)
    
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
            QGroupBox {{
                font-weight: 600;
                border: 2px solid #2a2f36;
                border-radius: 8px;
                margin: 10px 0px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
        """)

# Funciones de utilidad (sin cambios)
def should_show_config():
    """Verificar si se debe mostrar la ventana de configuración"""
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
    """Cargar configuración guardada al inicio"""
    settings = QSettings('MorphyDownloader', 'Config')
    
    if settings.value('spotify_client_id') and settings.value('spotify_client_secret'):
        os.environ['SPOTIPY_CLIENT_ID'] = settings.value('spotify_client_id')
        os.environ['SPOTIPY_CLIENT_SECRET'] = settings.value('spotify_client_secret')