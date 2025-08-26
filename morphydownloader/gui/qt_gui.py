# qt_gui.py - Versión optimizada sin timeouts
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTextEdit, QFileDialog, QProgressBar, QSizePolicy, QMessageBox
)
from PySide6.QtGui import QIcon, QFont, QCursor
from PySide6.QtCore import Qt, QThread, Signal, QSize
from ..config import Config

import sys
import os
import time
import logging

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
    """Worker thread optimizado sin timeouts"""
    progress_updated = Signal(int, int)
    log_message = Signal(str, str)  # message, level
    download_finished = Signal(bool, str)  # success, message
    
    def __init__(self, url, output_dir):
        super().__init__()
        self.url = url
        self.output_dir = output_dir
        self.cancel_requested = False
        
    def cancel(self):
        self.cancel_requested = True
        
    def run(self):
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
                if self.cancel_requested:
                    raise Exception("Descarga cancelada por el usuario")
                self.progress_updated.emit(current, total)
                
            def log_callback(msg, level="info"):
                if self.cancel_requested:
                    raise Exception("Descarga cancelada por el usuario")
                
                # Añadir timing solo a logs importantes
                elapsed = time.time() - start_time
                
                if "Descargando" in msg or "Descargado" in msg:
                    timed_msg = f"[{elapsed:.1f}s] {msg}"
                    self.log_message.emit(timed_msg, level)
                else:
                    self.log_message.emit(msg, level)
            
            # Ejecutar descarga SIN timeout
            self.log_message.emit("🔗 Conectando con Spotify...", "info")
            
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
            self.log_message.emit(str(e), "error")
            success = False
            
        finally:
            self.download_finished.emit(success, message)

class MorphyDownloaderQt(QWidget):
    def __init__(self):
        super().__init__()
        self.worker_thread = None
        self.init_ui()
        self.setup_styling()
        
    def init_ui(self):
        self.setWindowTitle('MorphyDownloader')
        
        # ✅ CAMBIO 1: Permitir redimensionado con tamaño mínimo más grande
        self.setMinimumSize(800, 580)  # Aumentado para evitar solapamientos
        self.resize(850, 620)  # Tamaño inicial más cómodo
        # self.setFixedSize(750, 520)  # ❌ REMOVER esta línea
        
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        self.setWindowFlag(Qt.WindowCloseButtonHint, True)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)  # ✅ Agregar maximizar
        
        # App icon
        icon_path = Config.get_asset_path('icon.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            
        layout = QVBoxLayout()
        layout.setContentsMargins(36, 24, 36, 24)
        layout.setSpacing(18)

        # ✅ CAMBIO 2: Agregar header con título y botón config
        header_layout = QHBoxLayout()
        
        title_label = QLabel('MorphyDownloader')
        title_label.setFont(QFont('Inter', 18, QFont.Bold))
        title_label.setStyleSheet(f"color: {PRIMARY_COLOR};")
        
        # Botón de configuración
        config_btn = QPushButton()
        config_btn.setCursor(QCursor(Qt.PointingHandCursor))
        config_btn.setToolTip('Abrir configuración')
        config_btn.setText('⚙️')  # O usar icono SVG si tienes
        config_btn.setFixedSize(40, 40)
        config_btn.setProperty("type", "secondary")
        config_btn.clicked.connect(self.open_config)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(config_btn)
        
        layout.addLayout(header_layout)

        # URL de Spotify
        url_label = QLabel('URL de Spotify (track, álbum o playlist):')
        url_label.setFont(QFont('Inter', 12, QFont.Medium))
        self.url_entry = QLineEdit()
        self.url_entry.setFont(QFont('Inter', 12))
        self.url_entry.setPlaceholderText('Pega aquí la URL de Spotify...')
        # ✅ CAMBIO 3: Política de expansión horizontal
        self.url_entry.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(url_label)
        layout.addWidget(self.url_entry)

        # Carpeta de destino
        # ✅ CAMBIO CORREGIDO: Layout vertical para evitar solapamientos
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
        # ✅ Expansión correcta con tamaño mínimo
        self.output_entry.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.output_entry.setMinimumWidth(200)  # Ancho mínimo para evitar solapamiento
        
        browse_btn = QPushButton()
        browse_btn.setCursor(QCursor(Qt.PointingHandCursor))
        browse_btn.setToolTip('Elegir carpeta')
        folder_select_icon = Config.get_asset_path('folder_select.svg')
        if os.path.exists(folder_select_icon):
            browse_btn.setIcon(QIcon(folder_select_icon))
            browse_btn.setIconSize(QSize(22, 22))
        else:
            browse_btn.setText('📁')
        browse_btn.setFixedSize(44, 44)  # Tamaño fijo para evitar deformación
        browse_btn.setProperty("type", "secondary")
        browse_btn.clicked.connect(self.choose_folder)
        
        folder_input_layout.addWidget(self.output_entry)
        folder_input_layout.addWidget(browse_btn)
        folder_section.addLayout(folder_input_layout)
        
        layout.addLayout(folder_section)

        # Botón descargar - sin cambios necesarios
        self.download_btn = QPushButton()
        self.download_btn.setCursor(QCursor(Qt.PointingHandCursor))
        folder_download_icon = Config.get_asset_path('folder_download.svg')
        if os.path.exists(folder_download_icon):
            self.download_btn.setIcon(QIcon(folder_download_icon))
            self.download_btn.setIconSize(QSize(26, 26))
            self.download_btn.setText('  Descargar')
        else:
            self.download_btn.setText('⬇️ Descargar')
        self.download_btn.setFont(QFont('Inter', 14, QFont.Bold))
        self.download_btn.clicked.connect(self.start_download)
        layout.addWidget(self.download_btn)

        # Barra de progreso - sin cambios
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setFixedHeight(26)
        self.progress.setTextVisible(True)
        layout.addWidget(self.progress)

        # ✅ CAMBIO 6: Área de log con mejor política de tamaño
        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)
        self.output_box.setFont(QFont('JetBrains Mono', 10))
        # Permitir expansión vertical
        self.output_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.output_box.setMinimumHeight(140)
        # self.output_box.setMaximumHeight(180)  # ❌ REMOVER límite máximo
        layout.addWidget(self.output_box)

        # Estado y botones - MEJORADO para evitar solapamiento
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(8)  # Espacio reducido entre elementos
        
        self.status_label = QLabel('')
        self.status_label.setFont(QFont('Inter', 12, QFont.Medium))
        # Status label con tamaño mínimo para prevenir solapamiento
        self.status_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.status_label.setMinimumWidth(200)  # Ancho mínimo
        self.status_label.setWordWrap(True)     # Permitir wrap si es necesario
        
        # Contenedor para botones con ancho fijo
        buttons_container = QHBoxLayout()
        buttons_container.setSpacing(4)
        
        self.cancel_btn = QPushButton()
        self.cancel_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.cancel_btn.setToolTip('Cancelar descarga')
        folder_cancel_icon = Config.get_asset_path('folder_cancel.svg')
        if os.path.exists(folder_cancel_icon):
            self.cancel_btn.setIcon(QIcon(folder_cancel_icon))
            self.cancel_btn.setIconSize(QSize(22, 22))
        else:
            self.cancel_btn.setText('❌')
        self.cancel_btn.setFixedSize(44, 44)  # Tamaño fijo
        self.cancel_btn.clicked.connect(self.cancel_download)
        self.cancel_btn.setProperty("type", "secondary")
        self.cancel_btn.setEnabled(False)
        
        open_btn = QPushButton()
        open_btn.setCursor(QCursor(Qt.PointingHandCursor))
        open_btn.setToolTip('Abrir carpeta de destino')
        folder_open_icon = Config.get_asset_path('folder_open.svg')
        if os.path.exists(folder_open_icon):
            open_btn.setIcon(QIcon(folder_open_icon))
            open_btn.setIconSize(QSize(22, 22))
        else:
            open_btn.setText('🗂️')
        open_btn.setFixedSize(44, 44)  # Tamaño fijo
        open_btn.setProperty("type", "secondary")
        open_btn.clicked.connect(self.open_folder)
        
        buttons_container.addWidget(self.cancel_btn)
        buttons_container.addWidget(open_btn)
        
        bottom_layout.addWidget(self.status_label, 1)  # Factor de stretch para expandir
        bottom_layout.addLayout(buttons_container, 0)   # Sin stretch para mantener tamaño
        layout.addLayout(bottom_layout)

        self.setLayout(layout)


    def open_config(self):
        """Abrir ventana de configuración"""
        try:
            from .config_dialog import ConfigDialog
            config_dialog = ConfigDialog(self)
            
            # Centrar en la ventana principal
            parent_geometry = self.geometry()
            dialog_size = config_dialog.size()
            x = parent_geometry.x() + (parent_geometry.width() - dialog_size.width()) // 2
            y = parent_geometry.y() + (parent_geometry.height() - dialog_size.height()) // 2
            config_dialog.move(x, y)
            
            config_dialog.exec()
        except ImportError as e:
            QMessageBox.warning(self, "Error", f"No se pudo abrir la configuración: {e}")

    # ✅ CAMBIO 9: Método para manejar redimensionado
    def resizeEvent(self, event):
        """Manejar redimensionado de ventana"""
        super().resizeEvent(event)
        # Asegurar que los elementos se ajusten correctamente
        self.update()
        
    def setup_styling(self):
        """Configurar estilos CSS mejorados"""
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
                min-height: 20px;  /* ✅ Altura mínima */
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
                min-height: 100px;  /* ✅ Altura mínima flexible */
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
                min-width: 80px;  /* ✅ Ancho mínimo */
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
                padding: 8px 8px;  /* ✅ Padding más pequeño para botones secundarios */
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
                min-height: 24px;  /* ✅ Altura mínima consistente */
            }}
            QProgressBar::chunk {{ 
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 {PRIMARY_COLOR}, stop: 1 #e91e63); 
                border-radius: 11px;
                margin: 1px;
            }}
            QLabel {{
                color: {FG_COLOR};
                font-weight: 500;
                min-height: 16px;  /* ✅ Altura mínima para labels */
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
        """Iniciar descarga sin validaciones complejas"""
        url = self.url_entry.text().strip()
        output = self.output_entry.text().strip()
        
        if not url:
            QMessageBox.warning(self, "Error", "Por favor, ingresa una URL de Spotify.")
            return
        
        # Validación simple de URL
        if 'spotify.com' not in url and 'spoti.fi' not in url:
            QMessageBox.warning(self, "URL No Válida", "Debe ser una URL de Spotify válida.")
            return
        
        # Limpiar interfaz
        self.output_box.clear()
        
        # Determinar tipo de contenido
        if 'track' in url:
            msg = '🎵 Preparando descarga de canción...'
        elif 'playlist' in url:
            msg = '📋 Preparando descarga de playlist...'
        elif 'album' in url:
            msg = '💿 Preparando descarga de álbum...'
        else:
            msg = '🎶 Preparando descarga...'
        
        self.append_log(msg, SUCCESS_COLOR)
        self.show_status_message("Iniciando...", PRIMARY_COLOR)
        
        # UI feedback
        self.download_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.progress.setValue(0)
        
        # Worker thread sin timeout
        self.worker_thread = DownloadWorker(url, output)
        self.worker_thread.progress_updated.connect(self.update_progress)
        self.worker_thread.log_message.connect(self.handle_log_message)
        self.worker_thread.download_finished.connect(self.handle_download_finished)
        
        start_msg = f"⏱️ Inicio: {time.strftime('%H:%M:%S')}"
        self.append_log(start_msg, "#888888")
        
        self.worker_thread.start()

    def cancel_download(self):
        """Cancelar descarga en progreso"""
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.cancel()
            self.append_log("Cancelando descarga...", "#f1c40f")
            self.show_status_message("Cancelando...", ERROR_COLOR)

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
                self.worker_thread.wait(3000)
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