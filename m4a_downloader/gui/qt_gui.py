# qt_gui.py
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTextEdit, QFileDialog, QProgressBar, QSizePolicy, QMessageBox,
    QComboBox, QGroupBox, QDialog
)
from PySide6.QtGui import QIcon, QFont, QCursor
from PySide6.QtCore import Qt, QThread, Signal, QSize, QSettings
from ..config import Config
from ..gui.config_dialog import get_saved_audio_format, get_saved_audio_quality

import sys
import os
import time
import logging

# Configuración de rutas de iconos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_PATH = os.path.join(BASE_DIR, '..', '..', 'assets')
ICONS_BASE_PATH = os.path.join(ASSETS_PATH, 'icons')
ICON_PATHS = {
    'app_icon': os.path.join(ASSETS_PATH, 'icon.ico'),
    'settings': os.path.join(ICONS_BASE_PATH, 'settings.svg'),
    'folder_select': os.path.join(ICONS_BASE_PATH, 'folder-select.svg'),
    'folder_download': os.path.join(ICONS_BASE_PATH, 'folder-download.svg'),
    'folder_cancel': os.path.join(ICONS_BASE_PATH, 'cancel.svg'),
    'folder_open': os.path.join(ICONS_BASE_PATH, 'folder-open.svg')
}

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Paleta de colores
PRIMARY_COLOR = Config.PRIMARY_COLOR
PRIMARY_DARK = Config.PRIMARY_DARK
BG_COLOR = Config.BG_COLOR
FG_COLOR = Config.FG_COLOR
ENTRY_BG = Config.ENTRY_BG
SUCCESS_COLOR = Config.SUCCESS_COLOR
ERROR_COLOR = Config.ERROR_COLOR

class DownloadWorker(QThread):
    """Worker thread para manejar descargas en segundo plano"""
    progress_updated = Signal(int, int)
    log_message = Signal(str, str)  # message, level
    download_finished = Signal(bool, str)  # success, message
    
    def __init__(self, url, output_dir, audio_format='m4a', quality='192'):
        super().__init__()
        self.url = url
        self.output_dir = output_dir
        self.audio_format = audio_format
        self.quality = quality
        self.cancel_requested = False
        
    def cancel(self):
        """Solicitar cancelación de la descarga"""
        self.cancel_requested = True
        
    def run(self):
        """Ejecutar proceso de descarga"""
        start_time = time.time()
        success = False
        message = ""
        
        try:
            # Importar función de descarga
            try:
                from ..cli import download
            except ImportError:
                import sys
                import os
                sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                from cli import download
            
            def progress_callback(current, total):
                """Callback para actualizar progreso"""
                if self.cancel_requested:
                    raise Exception("Descarga cancelada por el usuario")
                self.progress_updated.emit(current, total)
                
            def log_callback(msg, level="info"):
                """Callback para mensajes de log"""
                if self.cancel_requested:
                    raise Exception("Descarga cancelada por el usuario")
                
                # Añadir timing solo a logs importantes
                elapsed = time.time() - start_time
                
                if "Descargando" in msg or "Descargado" in msg:
                    timed_msg = f"[{elapsed:.1f}s] {msg}"
                    self.log_message.emit(timed_msg, level)
                else:
                    self.log_message.emit(msg, level)
            
            # Ejecutar descarga con formato y calidad especificados
            self.log_message.emit("Conectando con Spotify...", "info")
            
            download(
                url=self.url, 
                output=self.output_dir,
                audio_format=self.audio_format,
                quality=self.quality,
                progress_callback=progress_callback, 
                log_callback=log_callback
            )
            
            if not self.cancel_requested:
                total_time = time.time() - start_time
                success = True
                message = f"Descarga completada en {total_time:.1f}s - Formato: {self.audio_format.upper()}"
                
        except Exception as e:
            total_time = time.time() - start_time
            message = f"Error después de {total_time:.1f}s: {str(e)}"
            self.log_message.emit(str(e), "error")
            success = False
            
        finally:
            self.download_finished.emit(success, message)

class MorphyDownloaderQt(QWidget):
    def __init__(self):
        super().__init__()
        self.worker_thread = None
        self.settings = QSettings('MorphyDownloader', 'Config')
        self.init_ui()
        self.setup_styling()
        self.load_settings()
        
    def init_ui(self):
        """Inicializar interfaz de usuario"""
        self.setWindowTitle('MorphyDownloader')
        
        self.setMinimumSize(650, 750)
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        self.setWindowFlag(Qt.WindowCloseButtonHint, True)
        
        # Configurar icono de aplicación
        app_icon_path = Config.get_asset_path(ICON_PATHS['app_icon'])
        if os.path.exists(app_icon_path):
            self.setWindowIcon(QIcon(app_icon_path))
            
        layout = QVBoxLayout()
        layout.setContentsMargins(36, 24, 36, 24)
        layout.setSpacing(18)

        # Header con título y botón de configuración
        header_layout = QHBoxLayout()
        
        title_label = QLabel('M4A/MP3 Downloader')
        title_label.setFont(QFont('Segoe UI', 24, QFont.Bold))
        title_label.setStyleSheet(f"color: {PRIMARY_COLOR}; font-weight: 900;")
        
        config_btn = QPushButton()
        self._set_icon_or_text(config_btn, 'settings', 'Config')
        config_btn.setCursor(QCursor(Qt.PointingHandCursor))
        config_btn.setToolTip('Abrir configuración')
        config_btn.setFixedSize(40, 40)
        config_btn.setProperty("type", "secondary")
        config_btn.clicked.connect(self.open_config)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(config_btn)
        
        layout.addLayout(header_layout)

        # Campo de entrada para URL de Spotify
        url_label = QLabel('URL de Spotify (track, álbum o playlist):')
        url_label.setFont(QFont('Inter', 12, QFont.Medium))
        self.url_entry = QLineEdit()
        self.url_entry.setFont(QFont('Inter', 12))
        self.url_entry.setPlaceholderText('Pega aquí la URL de Spotify...')
        self.url_entry.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(url_label)
        layout.addWidget(self.url_entry)

        # Configuración de formato y calidad
        format_group = QGroupBox("Configuración de Audio")
        format_layout = QHBoxLayout(format_group)
        
        # Selector de formato
        format_layout.addWidget(QLabel('Formato:'))
        self.format_combo = QComboBox()
        self.format_combo.addItems(['m4a', 'mp3'])
        self.format_combo.currentTextChanged.connect(self.on_format_changed)
        format_layout.addWidget(self.format_combo)
        
        # Selector de calidad
        format_layout.addWidget(QLabel('Calidad:'))
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(Config.SUPPORTED_QUALITY)
        format_layout.addWidget(self.quality_combo)
        
        # Estado de FFmpeg
        self.ffmpeg_status = QLabel()
        self.ffmpeg_status.setWordWrap(True)
        format_layout.addWidget(self.ffmpeg_status)
        format_layout.addStretch()
        
        layout.addWidget(format_group)

        # Selección de carpeta de destino
        folder_section = QVBoxLayout()
        folder_label = QLabel('Carpeta de destino:')
        folder_label.setFont(QFont('Inter', 12, QFont.Medium))
        folder_section.addWidget(folder_label)
        
        # Layout horizontal para el input y botón
        folder_input_layout = QHBoxLayout()
        
        default_music_path = os.path.abspath('music')
        os.makedirs(default_music_path, exist_ok=True)
        
        self.output_entry = QLineEdit(default_music_path)
        self.output_entry.setFont(QFont('JetBrains Mono', 11))
        self.output_entry.setReadOnly(True)
        self.output_entry.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.output_entry.setMinimumWidth(200)
        
        browse_btn = QPushButton()
        self._set_icon_or_text(browse_btn, 'folder_select', 'Buscar')
        browse_btn.setCursor(QCursor(Qt.PointingHandCursor))
        browse_btn.setToolTip('Elegir carpeta')
        browse_btn.setFixedSize(44, 44)
        browse_btn.setProperty("type", "secondary")
        browse_btn.clicked.connect(self.choose_folder)
        
        folder_input_layout.addWidget(self.output_entry)
        folder_input_layout.addWidget(browse_btn)
        folder_section.addLayout(folder_input_layout)
        
        layout.addLayout(folder_section)

        # Botón principal de descarga
        self.download_btn = QPushButton()
        self._set_icon_or_text(self.download_btn, 'folder_download', 'Descargar')
        self.download_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.download_btn.setFont(QFont('Inter', 14, QFont.Bold))
        self.download_btn.clicked.connect(self.start_download)
        layout.addWidget(self.download_btn)

        # Barra de progreso
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setFixedHeight(26)
        self.progress.setTextVisible(True)
        layout.addWidget(self.progress)

        # Área de log de salida
        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)
        self.output_box.setFont(QFont('JetBrains Mono', 10))
        self.output_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.output_box.setMinimumHeight(140)
        layout.addWidget(self.output_box)

        # Parte inferior con estado y botones de acción
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(8)
        
        self.status_label = QLabel('')
        self.status_label.setFont(QFont('Inter', 12, QFont.Medium))
        self.status_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.status_label.setMinimumWidth(200)
        self.status_label.setWordWrap(True)
        
        # Contenedor para botones de acción
        buttons_container = QHBoxLayout()
        buttons_container.setSpacing(4)
        
        self.cancel_btn = QPushButton()
        self._set_icon_or_text(self.cancel_btn, 'folder_cancel', 'Cancelar')
        self.cancel_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.cancel_btn.setToolTip('Cancelar descarga')
        self.cancel_btn.setFixedSize(44, 44)
        self.cancel_btn.clicked.connect(self.cancel_download)
        self.cancel_btn.setProperty("type", "secondary")
        self.cancel_btn.setEnabled(False)
        
        open_btn = QPushButton()
        self._set_icon_or_text(open_btn, 'folder_open', 'Abrir')
        open_btn.setCursor(QCursor(Qt.PointingHandCursor))
        open_btn.setToolTip('Abrir carpeta de destino')
        open_btn.setFixedSize(44, 44)
        open_btn.setProperty("type", "secondary")
        open_btn.clicked.connect(self.open_folder)
        
        buttons_container.addWidget(self.cancel_btn)
        buttons_container.addWidget(open_btn)
        
        bottom_layout.addWidget(self.status_label, 1)
        bottom_layout.addLayout(buttons_container, 0)
        layout.addLayout(bottom_layout)

        self.setLayout(layout)

    def _set_icon_or_text(self, button, icon_key, fallback_text):
        """Establece icono o texto de respaldo para botones"""
        icon_path = Config.get_asset_path(ICON_PATHS.get(icon_key, ''))
        if os.path.exists(icon_path):
            button.setIcon(QIcon(icon_path))
            if ' ' in fallback_text:
                button.setText(fallback_text.split(' ', 1)[-1])  # Texto sin emoji
            button.setIconSize(QSize(22, 22))
        else:
            button.setText(fallback_text)

    def load_settings(self):
        """Cargar configuración guardada"""
        # Cargar formato de audio
        saved_format = get_saved_audio_format()
        if saved_format in Config.SUPPORTED_FORMATS:
            self.format_combo.setCurrentText(saved_format)
        
        # Cargar calidad de audio
        saved_quality = get_saved_audio_quality()
        if saved_quality in Config.SUPPORTED_QUALITY:
            self.quality_combo.setCurrentText(saved_quality)
            
        # Cargar directorio de salida
        saved_output = self.settings.value('default_output_dir')
        if saved_output and os.path.exists(saved_output):
            self.output_entry.setText(saved_output)
            
        # Actualizar estado inicial
        self.on_format_changed(self.format_combo.currentText())

    def on_format_changed(self, format_type):
        """Actualizar interfaz cuando se cambie el formato"""
        format_info = Config.get_format_info(format_type)
        
        # Actualizar título de la ventana
        self.setWindowTitle(f'MorphyDownloader - {format_type.upper()}')
        
        # Actualizar estado de FFmpeg
        if format_info['requires_ffmpeg']:
            if Config.check_ffmpeg():
                self.ffmpeg_status.setText("FFmpeg: Disponible")
                self.ffmpeg_status.setStyleSheet('color: #2ecc71; font-weight: bold;')
                self.quality_combo.setEnabled(True)
            else:
                self.ffmpeg_status.setText("FFmpeg: No disponible")
                self.ffmpeg_status.setStyleSheet('color: #e74c3c; font-weight: bold;')
                self.quality_combo.setEnabled(False)
        else:
            self.ffmpeg_status.setText("Sin conversión")
            self.ffmpeg_status.setStyleSheet('color: #3498db; font-weight: bold;')
            self.quality_combo.setEnabled(False)
            
        # Actualizar texto del botón de descarga
        self.download_btn.setText(f"Descargar {format_type.upper()}")

    def open_config(self):
        """Abrir ventana de configuración"""
        try:
            from .config_dialog import ConfigDialog
            config_dialog = ConfigDialog(self)
            
            # Centrar diálogo en la ventana principal
            parent_geometry = self.geometry()
            dialog_size = config_dialog.size()
            x = parent_geometry.x() + (parent_geometry.width() - dialog_size.width()) // 2
            y = parent_geometry.y() + (parent_geometry.height() - dialog_size.height()) // 2
            config_dialog.move(x, y)
            
            if config_dialog.exec() == QDialog.Accepted:
                # Recargar configuración después de guardar
                self.load_settings()
                
        except ImportError as e:
            QMessageBox.warning(self, "Error", f"No se pudo abrir la configuración: {e}")

    def setup_styling(self):
        """Aplicar estilos CSS a la interfaz"""
        self.setStyleSheet(f"""
            QWidget {{ 
                background: {BG_COLOR}; 
                color: {FG_COLOR};
                font-family: 'Segoe UI', 'Inter', sans-serif;
            }}
            QLineEdit {{ 
                background: {ENTRY_BG}; 
                color: {FG_COLOR}; 
                border-radius: 12px; 
                padding: 12px 16px; 
                border: 2px solid transparent;
                font-size: 14px;
                font-weight: 400;
                min-height: 24px;
            }}
            QLineEdit:focus {{
                border: 2px solid {PRIMARY_COLOR};
                background: #2a2f36;
            }}
            QComboBox {{
                background: {ENTRY_BG};
                color: {FG_COLOR};
                border-radius: 8px;
                padding: 8px 12px;
                border: 2px solid transparent;
                font-size: 13px;
                min-width: 80px;
            }}
            QComboBox:focus {{
                border: 2px solid {PRIMARY_COLOR};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                width: 12px;
                height: 12px;
            }}
            QComboBox QAbstractItemView {{
                background: {ENTRY_BG};
                color: {FG_COLOR};
                selection-background-color: {PRIMARY_COLOR};
                border: 1px solid #2a2f36;
            }}
            QTextEdit {{ 
                background: {BG_COLOR}; 
                color: {FG_COLOR}; 
                border-radius: 12px; 
                border: 1px solid #2a2f36; 
                font-size: 12px;
                padding: 8px;
                min-height: 110px;
            }}
            QPushButton {{ 
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 {PRIMARY_COLOR}, stop: 1 {PRIMARY_DARK}); 
                color: white; 
                border-radius: 12px; 
                padding: 12px 20px; 
                font-weight: 600; 
                font-size: 14px;
                border: none;
                min-height: 24px;
                min-width: 80px;
            }}
            QPushButton:hover {{ 
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #e91e63, stop: 1 #c2185b);
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 {PRIMARY_DARK}, stop: 1 #8e0a1e);
            }}
            QPushButton:disabled {{
                background: #404040;
                color: #888;
            }}
            QPushButton[type="secondary"] {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #4a4a4a, stop: 1 #3a3a3a);
                color: white;
                border-radius: 12px;
                padding: 8px 8px;
                font-size: 12px;
                min-width: 32px;
                min-height: 32px;
                border: none;
            }}
            QPushButton[type="secondary"]:hover {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #5a5a5a, stop: 1 #4a4a4a);
            }}
            QPushButton[type="secondary"]:pressed {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #3a3a3a, stop: 1 #2a2a2a);
            }}
            QPushButton[type="secondary"]:disabled {{
                background: #333;
                color: #666;
            }}
            QProgressBar {{ 
                background: #23272e; 
                border-radius: 12px; 
                text-align: center; 
                color: {FG_COLOR}; 
                font-size: 12px; 
                font-weight: 500;
                height: 24px;
                border: 1px solid #2a2f36;
                min-height: 24px;
            }}
            QProgressBar::chunk {{ 
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 {PRIMARY_COLOR}, stop: 1 #e91e63); 
                border-radius: 11px;
                margin: 1px;
            }}
            QLabel {{
                color: {FG_COLOR};
                font-weight: 500;
                min-height: 22px;
            }}
            QGroupBox {{
                font-weight: bold;
                border: 2px solid #2a2f36;
                border-radius: 12px;
                margin-top: 1ex;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
        """)

    def choose_folder(self):
        """Abrir diálogo para seleccionar carpeta de destino"""
        folder = QFileDialog.getExistingDirectory(self, 'Seleccionar carpeta de destino')
        if folder:
            self.output_entry.setText(folder)

    def open_folder(self):
        """Abrir carpeta de destino en el explorador del sistema"""
        folder = self.output_entry.text()
        if os.path.isdir(folder):
            if sys.platform.startswith('win'):
                os.startfile(folder)
            elif sys.platform.startswith('darwin'):
                os.system(f'open "{folder}"')
            else:
                os.system(f'xdg-open "{folder}"')
        else:
            self.show_status_message('Carpeta no encontrada', ERROR_COLOR)

    def show_status_message(self, message, color=None):
        """Mostrar mensaje de estado con color opcional"""
        if color:
            self.status_label.setText(f'<span style="color: {color}; font-family: Inter; font-size: 14px; font-weight: 500;">{message}</span>')
        else:
            self.status_label.setText(message)

    def start_download(self):
        """Iniciar proceso de descarga"""
        url = self.url_entry.text().strip()
        output = self.output_entry.text().strip()
        audio_format = self.format_combo.currentText()
        quality = self.quality_combo.currentText()
        
        if not url:
            QMessageBox.warning(self, "Error", "Por favor, ingresa una URL de Spotify.")
            return
        
        # Validación simple de URL
        if 'spotify.com' not in url and 'spoti.fi' not in url:
            QMessageBox.warning(self, "URL No Válida", "Debe ser una URL de Spotify válida.")
            return
            
        # Verificar FFmpeg si se necesita MP3
        if audio_format == 'mp3' and not Config.check_ffmpeg():
            reply = QMessageBox.question(
                self,
                "FFmpeg No Disponible",
                f"Has seleccionado formato MP3 pero FFmpeg no está instalado.\n"
                f"¿Deseas continuar con M4A en su lugar?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                audio_format = 'm4a'
                self.format_combo.setCurrentText('m4a')
            else:
                return
        
        # Limpiar interfaz para nueva descarga
        self.output_box.clear()
        
        # Determinar tipo de contenido
        if 'track' in url:
            msg = f'Preparando descarga de canción en {audio_format.upper()}...'
        elif 'playlist' in url:
            msg = f'Preparando descarga de playlist en {audio_format.upper()}...'
        elif 'album' in url:
            msg = f'Preparando descarga de álbum en {audio_format.upper()}...'
        else:
            msg = f'Preparando descarga en {audio_format.upper()}...'
        
        self.append_log(msg, SUCCESS_COLOR)
        self.show_status_message(f"Iniciando descarga {audio_format.upper()}...", PRIMARY_COLOR)
        
        # Actualizar estado de la interfaz
        self.download_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.progress.setValue(0)
        
        # Inicializar worker thread
        self.worker_thread = DownloadWorker(url, output, audio_format, quality)
        self.worker_thread.progress_updated.connect(self.update_progress)
        self.worker_thread.log_message.connect(self.handle_log_message)
        self.worker_thread.download_finished.connect(self.handle_download_finished)
        
        start_msg = f"Inicio: {time.strftime('%H:%M:%S')} - {audio_format.upper()} {quality}kbps"
        self.append_log(start_msg, "#888888")
        
        self.worker_thread.start()

    def cancel_download(self):
        """Solicitar cancelación de la descarga actual"""
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.cancel()
            self.append_log("Cancelando descarga...", "#f1c40f")
            self.show_status_message("Cancelando...", ERROR_COLOR)

    def update_progress(self, current, total):
        """Actualizar barra de progreso con valores actuales"""
        if total > 0:
            percent = int((current / total) * 100)
            self.progress.setValue(percent)

    def handle_log_message(self, message, level):
        """Procesar mensajes de log del worker thread"""
        color_map = {
            "error": ERROR_COLOR,
            "success": SUCCESS_COLOR,
            "warning": "#f1c40f",
            "info": None
        }
        self.append_log(message, color_map.get(level))

    def handle_download_finished(self, success, message):
        """Manejar finalización del proceso de descarga"""
        color = SUCCESS_COLOR if success else ERROR_COLOR
        self.append_log(message, color)
        self.show_status_message(message, color)
        
        # Restaurar estado de botones
        self.download_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        
        # Actualizar barra de progreso
        if success:
            self.progress.setValue(100)
        else:
            self.progress.setValue(0)
            
        # Limpiar referencia al worker thread
        if self.worker_thread:
            self.worker_thread.deleteLater()
            self.worker_thread = None

    def append_log(self, text, color=None):
        """Agregar mensaje al área de log con formato"""
        font_family = "JetBrains Mono, Fira Code, Monaco, 'Courier New', monospace"
        if color:
            self.output_box.append(f'<span style="color:{color}; font-family:{font_family}; font-size:11px; line-height: 1.7;">{text}</span>')
        else:
            self.output_box.append(f'<span style="font-family:{font_family}; font-size:11px; line-height: 1.7;">{text}</span>')
        
        # Auto-scroll hacia el final
        scrollbar = self.output_box.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def closeEvent(self, event):
        """Manejar evento de cierre de ventana"""
        if self.worker_thread and self.worker_thread.isRunning():
            reply = QMessageBox.question(
                self, 
                'Confirmación',
                '¿Estás seguro de que quieres cerrar? La descarga se cancelará.',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.worker_thread.cancel()
                self.worker_thread.wait(3000)
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

def main():
    """Función principal para ejecutar la aplicación"""
    app = QApplication(sys.argv)
    window = MorphyDownloaderQt()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()