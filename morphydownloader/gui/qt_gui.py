# gui_qt.py - Versión corregida
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTextEdit, QFileDialog, QProgressBar, QSizePolicy, QMessageBox
)
from PySide6.QtGui import QIcon, QFont, QCursor
from PySide6.QtCore import Qt, QThread, Signal, QSize
from ..config import Config
from contextlib import contextmanager

import signal
import threading
import sys
import os
import time
import traceback
import logging

# --- Customizable palette ---
PRIMARY_COLOR = Config.PRIMARY_COLOR
PRIMARY_DARK = Config.PRIMARY_DARK
BG_COLOR = Config.BG_COLOR
FG_COLOR = Config.FG_COLOR
ENTRY_BG = Config.ENTRY_BG
SUCCESS_COLOR = Config.SUCCESS_COLOR
ERROR_COLOR = Config.ERROR_COLOR

# Configurar logging para debug
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TimeoutError(Exception):
    pass

@contextmanager
def timeout_context(seconds):
    """Context manager para timeout de operaciones - CORREGIDO"""
    if hasattr(signal, 'SIGALRM') and hasattr(signal, 'alarm'):
        # Unix systems
        def timeout_handler(signum, frame):
            raise TimeoutError(f"Operation timed out after {seconds} seconds")
        
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(seconds)
        try:
            yield
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)
    else:
        # Windows y otros sistemas - usar threading
        class TimeoutThread(threading.Thread):
            def __init__(self):
                super().__init__()
                self.daemon = True
                self.exception = None
                self.result = None
                self.finished = False
                
            def run(self):
                try:
                    # El código principal se ejecutará en el hilo principal
                    pass
                except Exception as e:
                    self.exception = e
                finally:
                    self.finished = True
        
        # Para Windows, simplemente hacer yield y confiar en otros mecanismos
        try:
            yield
        except Exception as e:
            raise

class DownloadWorker(QThread):
    """Worker thread optimizado con mejor logging de timing"""
    progress_updated = Signal(int, int)
    log_message = Signal(str, str)  # message, level
    download_finished = Signal(bool, str)  # success, message
    
    def __init__(self, url, output_dir):
        super().__init__()
        self.url = url
        self.output_dir = output_dir
        self.cancel_requested = False
        self._timeout = 600  # 10 minutos
        
    def cancel(self):
        self.cancel_requested = True
        
    def run(self):
        start_time = time.time()
        success = False
        message = ""
        
        try:
            # Timing de importaciones
            import_start = time.time()
            try:
                from ..cli import download
            except ImportError:
                import sys
                import os
                sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                from cli import download
            
            import_time = time.time() - import_start
            logger.debug(f"⏱️  Import time: {import_time:.2f}s")
            
            def progress_callback(current, total):
                if self.cancel_requested:
                    raise Exception("Descarga cancelada por el usuario")
                
                # Verificar timeout
                if time.time() - start_time > self._timeout:
                    raise Exception(f"Timeout después de {self._timeout}s")
                
                self.progress_updated.emit(current, total)
                
            def log_callback(msg, level="info"):
                # Añadir timing a los logs importantes
                elapsed = time.time() - start_time
                
                if self.cancel_requested:
                    raise Exception("Descarga cancelada por el usuario")
                
                if time.time() - start_time > self._timeout:
                    raise Exception(f"Timeout después de {self._timeout}s")
                
                # Log con timing para debug
                if "Conectando" in msg or "Descargando" in msg or "Descargado" in msg:
                    timed_msg = f"[{elapsed:.1f}s] {msg}"
                    logger.debug(timed_msg)
                    self.log_message.emit(timed_msg, level)
                else:
                    self.log_message.emit(msg, level)
            
            # Inicio de descarga con timing
            self.log_message.emit("🔗 Conectando con Spotify API...", "info")
            spotify_start = time.time()
            
            # Ejecutar descarga
            download(
                url=self.url, 
                output=self.output_dir, 
                progress_callback=progress_callback, 
                log_callback=log_callback
            )
            
            if not self.cancel_requested:
                total_time = time.time() - start_time
                success = True
                message = f"✅ Descarga completada en {total_time:.1f}s"
                
        except Exception as e:
            total_time = time.time() - start_time
            message = f"❌ Error después de {total_time:.1f}s: {str(e)}"
            
            # Log detallado solo para debug
            logger.error(f"Error completo: {traceback.format_exc()}")
            self.log_message.emit(str(e), "error")
            success = False
            
        finally:
            # Siempre emitir señal de finalización
            try:
                self.download_finished.emit(success, message)
            except Exception as e:
                logger.error(f"Error en finalización: {e}")


class MorphyDownloaderQt(QWidget):
    def __init__(self):
        super().__init__()
        self.worker_thread = None
        self.init_ui()
        self.setup_styling()
        
    def init_ui(self):
        self.setWindowTitle('MorphyDownloader')
        self.setFixedSize(750, 520)
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        self.setWindowFlag(Qt.WindowCloseButtonHint, True)
        
        # App icon
        icon_path = Config.get_asset_path('icon.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            
        layout = QVBoxLayout()
        layout.setContentsMargins(36, 24, 36, 24)
        layout.setSpacing(18)

        # --- URL de Spotify ---
        url_label = QLabel('URL de Spotify (track, álbum o playlist):')
        url_label.setFont(QFont('Inter', 12, QFont.Medium))
        self.url_entry = QLineEdit()
        self.url_entry.setFont(QFont('Inter', 12))
        self.url_entry.setPlaceholderText('Pega aquí la URL de Spotify...')
        layout.addWidget(url_label)
        layout.addWidget(self.url_entry)

        # --- Carpeta de destino ---
        folder_layout = QHBoxLayout()
        folder_label = QLabel('Carpeta de destino:')
        folder_label.setFont(QFont('Inter', 12, QFont.Medium))
        
        # Crear directorio music si no existe
        default_music_path = os.path.abspath('music')
        os.makedirs(default_music_path, exist_ok=True)
        
        self.output_entry = QLineEdit(default_music_path)
        self.output_entry.setFont(QFont('JetBrains Mono', 11))
        self.output_entry.setReadOnly(True)
        self.output_entry.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        browse_btn = QPushButton()
        browse_btn.setCursor(QCursor(Qt.PointingHandCursor))
        browse_btn.setToolTip('Elegir carpeta')
        # Usar folder-select.svg para seleccionar ubicación de descarga
        browse_icon_path = Config.get_asset_path('folder-select.svg')
        if not os.path.exists(browse_icon_path):
            browse_icon_path = os.path.join(os.path.dirname(__file__), 'textures/folder-select.svg')
        if os.path.exists(browse_icon_path):
            browse_btn.setIcon(QIcon(browse_icon_path))
            browse_btn.setIconSize(QSize(22, 22))
        else:
            browse_btn.setText('📁')
        browse_btn.setFixedWidth(44)
        browse_btn.setProperty("type", "secondary")
        browse_btn.clicked.connect(self.choose_folder)
        
        folder_layout.addWidget(folder_label)
        folder_layout.addWidget(self.output_entry)
        folder_layout.addWidget(browse_btn)
        layout.addLayout(folder_layout)

        # --- Botón descargar ---
        self.download_btn = QPushButton()
        self.download_btn.setCursor(QCursor(Qt.PointingHandCursor))
        # Usar folder-download.svg para el botón de descarga
        download_icon_path = Config.get_asset_path('folder-download.svg')
        if os.path.exists(download_icon_path):
            self.download_btn.setIcon(QIcon(download_icon_path))
            self.download_btn.setIconSize(QSize(26, 26))
            self.download_btn.setText('  Descargar')
        else:
            self.download_btn.setText('⬇️ Descargar')
        self.download_btn.setFont(QFont('Inter', 14, QFont.Bold))
        self.download_btn.clicked.connect(self.start_download)
        layout.addWidget(self.download_btn)

        # --- Barra de progreso ---
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setFixedHeight(26)
        self.progress.setTextVisible(True)
        layout.addWidget(self.progress)

        # --- Área de log ---
        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)
        self.output_box.setFont(QFont('JetBrains Mono', 10))
        self.output_box.setMinimumHeight(140)
        self.output_box.setMaximumHeight(180)
        layout.addWidget(self.output_box)

        # --- Estado, botón abrir carpeta y cancelar ---
        bottom_layout = QHBoxLayout()
        self.status_label = QLabel('')
        self.status_label.setFont(QFont('Inter', 12, QFont.Medium))
        
        open_btn = QPushButton()
        open_btn.setCursor(QCursor(Qt.PointingHandCursor))
        open_btn.setToolTip('Abrir carpeta de destino')
        # Usar folder-open.svg para abrir carpeta
        open_icon_path = Config.get_asset_path('folder-open.svg')
        if os.path.exists(open_icon_path):
            open_btn.setIcon(QIcon(open_icon_path))
            open_btn.setIconSize(QSize(22, 22))
        else:
            open_btn.setText('🗂️')
        open_btn.setFixedWidth(44)
        open_btn.setProperty("type", "secondary")
        open_btn.clicked.connect(self.open_folder)
        
        self.cancel_btn = QPushButton()
        self.cancel_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.cancel_btn.setToolTip('Cancelar descarga')
        # Usar folder-cancel.svg para cancelar
        cancel_icon_path = Config.get_asset_path('folder-cancel.svg')
        if os.path.exists(cancel_icon_path):
            self.cancel_btn.setIcon(QIcon(cancel_icon_path))
            self.cancel_btn.setIconSize(QSize(22, 22))
        else:
            self.cancel_btn.setText('❌')
        self.cancel_btn.setFixedWidth(44)
        self.cancel_btn.clicked.connect(self.cancel_download)
        self.cancel_btn.setProperty("type", "secondary")
        self.cancel_btn.setEnabled(False)
        
        bottom_layout.addWidget(self.status_label)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.cancel_btn)
        bottom_layout.addWidget(open_btn)
        layout.addLayout(bottom_layout)

        self.setLayout(layout)
        
    def setup_styling(self):
        """Configurar estilos CSS"""
        self.setStyleSheet(f"""
            QWidget {{ 
                background: {BG_COLOR}; 
                color: {FG_COLOR};
                font-family: 'Inter', 'Segoe UI', sans-serif;
            }}
            QLineEdit {{ 
                background: {ENTRY_BG}; 
                color: {FG_COLOR}; 
                border-radius: 12px; 
                padding: 12px 16px; 
                border: 2px solid transparent;
                font-size: 14px;
                font-weight: 400;
            }}
            QLineEdit:focus {{
                border: 2px solid {PRIMARY_COLOR};
                background: #2a2f36;
            }}
            QTextEdit {{ 
                background: {BG_COLOR}; 
                color: {FG_COLOR}; 
                border-radius: 12px; 
                border: 1px solid #2a2f36; 
                font-size: 12px;
                padding: 8px;
            }}
            QPushButton {{ 
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 {PRIMARY_COLOR}, stop: 1 {PRIMARY_DARK}); 
                color: white; 
                border-radius: 12px; 
                padding: 12px 20px; 
                font-weight: 600; 
                font-size: 14px;
                border: none;
                min-height: 20px;
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
                padding: 12px 12px;
                font-size: 12px;
                min-width: 20px;
                min-height: 20px;
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
            }}
            QProgressBar::chunk {{ 
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 {PRIMARY_COLOR}, stop: 1 #e91e63); 
                border-radius: 11px;
                margin: 1px;
            }}
            QLabel {{
                color: {FG_COLOR};
                font-weight: 500;
            }}
        """)

    def choose_folder(self):
        """Abrir diálogo para seleccionar carpeta"""
        folder = QFileDialog.getExistingDirectory(self, 'Seleccionar carpeta de destino')
        if folder:
            self.output_entry.setText(folder)

    def open_folder(self):
        """Abrir carpeta de destino en el explorador"""
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
        """Mostrar mensaje en el status label"""
        if color:
            self.status_label.setText(f'<span style="color: {color}; font-family: Inter; font-size: 14px; font-weight: 500;">{message}</span>')
        else:
            self.status_label.setText(message)

    def start_download(self):
        """Método start_download optimizado con mejor feedback"""
        url = self.url_entry.text().strip()
        output = self.output_entry.text().strip()
        
        if not url:
            QMessageBox.warning(self, "Error", "Por favor, ingresa una URL de Spotify.")
            return
        
        if not self.validate_spotify_url(url):
            QMessageBox.warning(
                self, 
                "URL No Válida", 
                "La URL no es válida de Spotify.\n\n"
                "Formatos compatibles:\n"
                "• https://open.spotify.com/track/...\n"
                "• https://open.spotify.com/playlist/...\n"
                "• https://open.spotify.com/album/...\n"
                "• https://spoti.fi/..."
            )
            return
        
        # Limpiar interfaz
        self.output_box.clear()
        
        # Mensaje inicial optimista
        content_type = self.extract_spotify_type(url)
        type_messages = {
            'track': '🎵 Preparando descarga de canción...',
            'playlist': '📋 Preparando descarga de playlist...',
            'album': '💿 Preparando descarga de álbum...',
            'unknown': '🎶 Preparando descarga...'
        }
        
        self.append_log(type_messages.get(content_type, "🚀 Iniciando descarga..."), "#00ff88")
        self.show_status_message("Iniciando...", PRIMARY_COLOR)
        
        # UI feedback
        self.download_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.progress.setValue(0)
        
        # Worker thread
        self.worker_thread = DownloadWorker(url, output)
        self.worker_thread.progress_updated.connect(self.update_progress)
        self.worker_thread.log_message.connect(self.handle_log_message)
        self.worker_thread.download_finished.connect(self.handle_download_finished)
        
        # Log de inicio para timing
        import time
        start_msg = f"⏱️  Inicio: {time.strftime('%H:%M:%S')}"
        self.append_log(start_msg, "#888888")
        
        self.worker_thread.start()

    def validate_spotify_url(self, url):
        """Validar que la URL sea de Spotify"""
        if not url or not isinstance(url, str):
            return False
        
        url = url.strip()
        
        # Patrones para diferentes tipos de enlaces de Spotify
        spotify_patterns = [
            # URLs estándar de open.spotify.com
            r'https?://open\.spotify\.com/track/[a-zA-Z0-9]+(\?.*)?',
            r'https?://open\.spotify\.com/playlist/[a-zA-Z0-9]+(\?.*)?',
            r'https?://open\.spotify\.com/album/[a-zA-Z0-9]+(\?.*)?',
            r'https?://open\.spotify\.com/artist/[a-zA-Z0-9]+(\?.*)?',
            
            # URLs cortas de spotify:
            r'spotify:track:[a-zA-Z0-9]+',
            r'spotify:playlist:[a-zA-Z0-9]+',
            r'spotify:album:[a-zA-Z0-9]+',
            r'spotify:artist:[a-zA-Z0-9]+',
            
            # URLs compartidas (spoti.fi)
            r'https?://spoti\.fi/[a-zA-Z0-9]+',
        ]
        
        # Verificar si coincide con algún patrón
        import re
        for pattern in spotify_patterns:
            if re.match(pattern, url):
                return True
        
        # Intentar extraer ID de Spotify si la URL tiene formato inusual
        spotify_id_pattern = r'[a-zA-Z0-9]{22}'
        if re.search(spotify_id_pattern, url) and 'spotify' in url.lower():
            return True
        
        return False

    def cancel_download(self):
        """Cancelar descarga en progreso"""
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.cancel()
            self.append_log("Cancelando descarga...", "#f1c40f")
            self.show_status_message("Cancelando...", ERROR_COLOR)

    def extract_spotify_type(self, url):
        """Extraer el tipo de contenido de Spotify"""
        url = url.strip().lower()
        
        if 'track' in url:
            return 'track'
        elif 'playlist' in url:
            return 'playlist'
        elif 'album' in url:
            return 'album'
        elif 'artist' in url:
            return 'artist'
        else:
            return 'unknown'
    def update_progress(self, current, total):
        """Actualizar barra de progreso"""
        if total > 0:
            percent = int((current / total) * 100)
            self.progress.setValue(percent)

    def handle_log_message(self, message, level):
        """Manejar mensajes de log del worker thread"""
        color_map = {
            "error": ERROR_COLOR,
            "success": SUCCESS_COLOR,
            "warning": "#f1c40f",
            "info": None
        }
        self.append_log(message, color_map.get(level))

    def handle_download_finished(self, success, message):
        """Manejar finalización de descarga"""
        color = SUCCESS_COLOR if success else ERROR_COLOR
        self.append_log(message, color)
        self.show_status_message(message, color)
        
        # Rehabilitar botones
        self.download_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        
        # Actualizar progreso
        if success:
            self.progress.setValue(100)
        else:
            self.progress.setValue(0)
            
        # Limpiar worker thread
        if self.worker_thread:
            self.worker_thread.deleteLater()
            self.worker_thread = None

    def append_log(self, text, color=None):
        """Agregar mensaje al área de log"""
        font_family = "JetBrains Mono, Fira Code, Monaco, 'Courier New', monospace"
        if color:
            self.output_box.append(f'<span style="color:{color}; font-family:{font_family}; font-size:11px; line-height: 1.4;">{text}</span>')
        else:
            self.output_box.append(f'<span style="font-family:{font_family}; font-size:11px; line-height: 1.4;">{text}</span>')
        
        # Auto-scroll
        scrollbar = self.output_box.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def closeEvent(self, event):
        """Manejar cierre de ventana"""
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
                self.worker_thread.wait(3000)  # Esperar hasta 3 segundos
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

def main():
    app = QApplication(sys.argv)
    window = MorphyDownloaderQt()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()