# qt_gui.py
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTextEdit, QFileDialog, QProgressBar, QSizePolicy, QMessageBox,
    QComboBox, QGroupBox, QDialog
)
from PySide6.QtGui import QIcon, QFont, QCursor, QShortcut, QKeySequence
from PySide6.QtCore import Qt, QThread, Signal, QSize, QSettings
from ..config import Config
from ..gui.config_dialog import get_saved_audio_format, get_saved_audio_quality
from .theme_manager import ThemeManager
from ..locales import _
from ..utils import detect_url_source

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

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class DownloadWorker(QThread):
    progress_updated = Signal(int, int)
    log_message = Signal(str, str) 
    download_finished = Signal(bool, str) 
    
    def __init__(self, url, output_dir, audio_format='m4a', quality='192'):
        super().__init__()
        self.url = url
        self.output_dir = output_dir
        self.audio_format = audio_format
        self.quality = quality
        self.cancel_requested = False
        
    def cancel(self):
        self.cancel_requested = True
        
    def run(self):
        start_time = time.time()
        success = False
        message = ""
        
        try:
            try:
                from ..cli import download
            except ImportError:
                sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                from cli import download
            
            def progress_callback(current, total):
                if self.cancel_requested:
                    raise Exception("Descarga cancelada por el usuario" if _('cancel') == "Cancelar" else "Download canceled by user")
                self.progress_updated.emit(current, total)
                
            def log_callback(msg, level="info"):
                if self.cancel_requested:
                    raise Exception("Canceled")
                elapsed = time.time() - start_time
                if "Descarg" in msg or "Download" in msg:
                    timed_msg = f"[{elapsed:.1f}s] {msg}"
                    self.log_message.emit(timed_msg, level)
                else:
                    self.log_message.emit(msg, level)
            
            self.log_message.emit("Connecting to API...", "info")
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
                message = f"Done in {total_time:.1f}s - FORMAT: {self.audio_format.upper()}"
                
        except Exception as e:
            total_time = time.time() - start_time
            message = f"Error after {total_time:.1f}s: {str(e)}"
            self.log_message.emit(str(e), "error")
            success = False
            
        finally:
            self.download_finished.emit(success, message)

class MorphyDownloaderQt(QWidget):
    def __init__(self):
        super().__init__()
        self.worker_thread = None
        self.settings = QSettings('MorphyDownloader', 'Config')
        self.current_theme = self.settings.value('theme', ThemeManager.get_default_theme())
        
        self.init_ui()
        self.setup_styling()
        self.load_settings()
        self.setup_shortcuts()
        
    def init_ui(self):
        self.setWindowTitle(_('title'))
        # Tamaño base seguro para resoluciones menores (ej. 720p)
        self.setMinimumSize(500, 550)
        self.resize(650, 700)
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        self.setWindowFlag(Qt.WindowCloseButtonHint, True)
        
        app_icon_path = Config.get_asset_path(ICON_PATHS['app_icon'])
        if os.path.exists(app_icon_path):
            self.setWindowIcon(QIcon(app_icon_path))
            
        layout = QVBoxLayout()
        layout.setContentsMargins(36, 24, 36, 24)
        layout.setSpacing(18)

        header_layout = QHBoxLayout()
        self.title_label = QLabel(_('app_subtitle'))
        self.title_label.setFont(QFont('Segoe UI', 24, QFont.Bold))
        # The color will be handled by the Theme Manager but Title gets special attention
        
        self.config_btn = QPushButton()
        self._set_icon_or_text(self.config_btn, 'settings', _('settings'))
        self.config_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.config_btn.setToolTip(_('settings'))
        self.config_btn.setFixedSize(40, 40)
        self.config_btn.setProperty("type", "secondary")
        self.config_btn.clicked.connect(self.open_config)
        
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.config_btn)
        layout.addLayout(header_layout)

        self.url_label = QLabel(_('spotify_url'))
        self.url_label.setFont(QFont('Inter', 12, QFont.Medium))
        self.url_entry = QLineEdit()
        self.url_entry.setFont(QFont('Inter', 12))
        self.url_entry.setPlaceholderText(_('paste_url_placeholder'))
        self.url_entry.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self.url_label)
        layout.addWidget(self.url_entry)

        self.format_group = QGroupBox(_('audio_config'))
        format_layout = QHBoxLayout(self.format_group)
        
        self.lbl_format = QLabel(_('format'))
        format_layout.addWidget(self.lbl_format)
        self.format_combo = QComboBox()
        self.format_combo.addItems(['m4a', 'mp3'])
        self.format_combo.currentTextChanged.connect(self.on_format_changed)
        format_layout.addWidget(self.format_combo)
        
        self.lbl_quality = QLabel(_('quality'))
        format_layout.addWidget(self.lbl_quality)
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(Config.SUPPORTED_QUALITY)
        format_layout.addWidget(self.quality_combo)
        
        self.ffmpeg_status = QLabel()
        self.ffmpeg_status.setWordWrap(True)
        format_layout.addWidget(self.ffmpeg_status)
        format_layout.addStretch()
        layout.addWidget(self.format_group)

        folder_section = QVBoxLayout()
        self.folder_label = QLabel(_('output_folder'))
        self.folder_label.setFont(QFont('Inter', 12, QFont.Medium))
        folder_section.addWidget(self.folder_label)
        
        folder_input_layout = QHBoxLayout()
        default_music_path = os.path.abspath('music')
        os.makedirs(default_music_path, exist_ok=True)
        
        self.output_entry = QLineEdit(default_music_path)
        self.output_entry.setFont(QFont('JetBrains Mono', 11))
        self.output_entry.setReadOnly(True)
        self.output_entry.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.output_entry.setMinimumWidth(200)
        
        self.browse_btn = QPushButton()
        self._set_icon_or_text(self.browse_btn, 'folder_select', _('browse'))
        self.browse_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.browse_btn.setToolTip(_('browse'))
        self.browse_btn.setFixedSize(44, 44)
        self.browse_btn.setProperty("type", "secondary")
        self.browse_btn.clicked.connect(self.choose_folder)
        
        folder_input_layout.addWidget(self.output_entry)
        folder_input_layout.addWidget(self.browse_btn)
        folder_section.addLayout(folder_input_layout)
        layout.addLayout(folder_section)

        self.download_btn = QPushButton()
        self._set_icon_or_text(self.download_btn, 'folder_download', _('download'))
        self.download_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.download_btn.setFont(QFont('Inter', 14, QFont.Bold))
        self.download_btn.clicked.connect(self.start_download)
        # Adding accessible properties for screen reader
        self.download_btn.setAccessibleName("Boton de Descarga")
        layout.addWidget(self.download_btn)

        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setFixedHeight(26)
        self.progress.setTextVisible(True)
        layout.addWidget(self.progress)

        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)
        self.output_box.setFont(QFont('JetBrains Mono', 10))
        self.output_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.output_box.setMinimumHeight(140)
        layout.addWidget(self.output_box)

        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(8)
        
        self.status_label = QLabel('')
        self.status_label.setFont(QFont('Inter', 12, QFont.Medium))
        self.status_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.status_label.setMinimumWidth(200)
        self.status_label.setWordWrap(True)
        
        buttons_container = QHBoxLayout()
        buttons_container.setSpacing(4)
        
        self.cancel_btn = QPushButton()
        self._set_icon_or_text(self.cancel_btn, 'folder_cancel', _('cancel'))
        self.cancel_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.cancel_btn.setToolTip(_('cancel'))
        self.cancel_btn.setFixedSize(44, 44)
        self.cancel_btn.clicked.connect(self.cancel_download)
        self.cancel_btn.setProperty("type", "secondary")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.setAccessibleName("Boton Cancelar")
        
        self.open_btn = QPushButton()
        self._set_icon_or_text(self.open_btn, 'folder_open', _('open'))
        self.open_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.open_btn.setToolTip(_('open'))
        self.open_btn.setFixedSize(44, 44)
        self.open_btn.setProperty("type", "secondary")
        self.open_btn.clicked.connect(self.open_folder)
        
        buttons_container.addWidget(self.cancel_btn)
        buttons_container.addWidget(self.open_btn)
        
        bottom_layout.addWidget(self.status_label, 1)
        bottom_layout.addLayout(buttons_container, 0)
        layout.addLayout(bottom_layout)

        self.setLayout(layout)

    def setup_shortcuts(self):
        # ATAJOS DE TECLADO
        # 1. Enter en la caja de URL -> Inicia la descarga
        self.shortcut_enter = QShortcut(QKeySequence("Return"), self.url_entry)
        self.shortcut_enter.activated.connect(self.start_download)
        
        # 2. Ctrl+, -> Abre la configuración
        self.shortcut_settings = QShortcut(QKeySequence("Ctrl+,"), self)
        self.shortcut_settings.activated.connect(self.open_config)

        # 3. Esc -> Cancela descarga si está activa
        self.shortcut_esc = QShortcut(QKeySequence("Esc"), self)
        self.shortcut_esc.activated.connect(lambda: self.cancel_download() if self.cancel_btn.isEnabled() else None)

    def _set_icon_or_text(self, button, icon_key, fallback_text):
        icon_path = Config.get_asset_path(ICON_PATHS.get(icon_key, ''))
        if os.path.exists(icon_path):
            button.setIcon(QIcon(icon_path))
            if ' ' in fallback_text:
                button.setText(fallback_text.split(' ', 1)[-1])
            button.setIconSize(QSize(22, 22))
        else:
            button.setText(fallback_text)

    def load_settings(self):
        saved_format = get_saved_audio_format()
        if saved_format in Config.SUPPORTED_FORMATS:
            self.format_combo.setCurrentText(saved_format)
        
        saved_quality = get_saved_audio_quality()
        if saved_quality in Config.SUPPORTED_QUALITY:
            self.quality_combo.setCurrentText(saved_quality)
            
        saved_output = self.settings.value('default_output_dir')
        if saved_output and os.path.exists(saved_output):
            self.output_entry.setText(saved_output)
            
        self.on_format_changed(self.format_combo.currentText())

    def on_format_changed(self, format_type):
        self.setWindowTitle(f"{_('title')} - {format_type.upper()}")
        
        format_info = Config.get_format_info(format_type)
        if format_info['requires_ffmpeg']:
            if Config.check_ffmpeg():
                self.ffmpeg_status.setText(_('ffmpeg_available'))
                self.ffmpeg_status.setStyleSheet(f"color: {ThemeManager.get_theme(self.current_theme)['SUCCESS_COLOR']}; font-weight: bold;")
                self.quality_combo.setEnabled(True)
            else:
                self.ffmpeg_status.setText(_('ffmpeg_unavailable'))
                self.ffmpeg_status.setStyleSheet(f"color: {ThemeManager.get_theme(self.current_theme)['ERROR_COLOR']}; font-weight: bold;")
                self.quality_combo.setEnabled(False)
        else:
            self.ffmpeg_status.setText(_('no_conversion'))
            self.ffmpeg_status.setStyleSheet(f"color: {ThemeManager.get_theme(self.current_theme)['PRIMARY_COLOR']}; font-weight: bold;")
            self.quality_combo.setEnabled(False)
            
        # Update download button text cleanly
        self.download_btn.setText(_('download'))

    def open_config(self):
        try:
            from .config_dialog import ConfigDialog
            config_dialog = ConfigDialog(self)
            
            # Connect signals
            config_dialog.theme_changed.connect(self.on_theme_changed)
            config_dialog.language_changed.connect(self.on_language_changed)
            
            config_dialog.exec()
            self.load_settings() # Recargar settings extra
        except ImportError as e:
            QMessageBox.warning(self, "Error", f"Error opening config: {e}")

    def on_theme_changed(self, theme_id):
        self.current_theme = theme_id
        self.setup_styling()
        # force UI labels refresh
        self.on_format_changed(self.format_combo.currentText())

    def on_language_changed(self, lang_id):
        # Refresh hardcoded labels dynamically 
        self.title_label.setText(_('app_subtitle'))
        self.url_label.setText(_('spotify_url'))
        self.url_entry.setPlaceholderText(_('paste_url_placeholder'))
        self.format_group.setTitle(_('audio_config'))
        self.lbl_format.setText(_('format'))
        self.lbl_quality.setText(_('quality'))
        self.folder_label.setText(_('output_folder'))
        self.download_btn.setText(_('download'))
        self.on_format_changed(self.format_combo.currentText())

    def setup_styling(self):
        ThemeManager.apply_theme(self, self.current_theme)
        theme = ThemeManager.get_theme(self.current_theme)
        self.title_label.setStyleSheet(f"color: {theme['PRIMARY_COLOR']}; font-weight: 900;")

    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, _('output_folder'))
        if folder:
            self.output_entry.setText(folder)

    def open_folder(self):
        folder = self.output_entry.text()
        if os.path.isdir(folder):
            if sys.platform.startswith('win'):
                os.startfile(folder)
            elif sys.platform.startswith('darwin'):
                os.system(f'open "{folder}"')
            else:
                os.system(f'xdg-open "{folder}"')
        else:
            self.show_status_message(_('folder_not_found'), ThemeManager.get_theme(self.current_theme)['ERROR_COLOR'])

    def show_status_message(self, message, color=None):
        if color:
            self.status_label.setText(f'<span style="color: {color}; font-family: Inter; font-size: 14px; font-weight: 500;">{message}</span>')
        else:
            self.status_label.setText(message)

    def start_download(self):
        url = self.url_entry.text().strip()
        output = self.output_entry.text().strip()
        audio_format = self.format_combo.currentText()
        quality = self.quality_combo.currentText()
        theme = ThemeManager.get_theme(self.current_theme)
        
        if not url:
            QMessageBox.warning(self, _('error'), _('enter_url'))
            return
        
        source_type = detect_url_source(url)
        if source_type == "unknown":
            QMessageBox.warning(self, _('error'), _('invalid_url'))
            return
            
        if audio_format == 'mp3' and not Config.check_ffmpeg():
            reply = QMessageBox.question(self, "FFmpeg", _('ffmpeg_missing_warn'),
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if reply == QMessageBox.Yes:
                audio_format = 'm4a'
                self.format_combo.setCurrentText('m4a')
            else:
                return
        
        self.output_box.clear()
        
        if source_type == 'spotify_track':
            msg = _('preparing_song', format=audio_format.upper())
        elif source_type in ('spotify_playlist', 'youtube_playlist'):
             msg = _('preparing_playlist', format=audio_format.upper())
        elif source_type == 'spotify_album':
             msg = _('preparing_album', format=audio_format.upper())
        elif source_type == 'youtube_video':
             msg = _('preparing_song', format=audio_format.upper())
        else:
             msg = _('preparing', format=audio_format.upper())
        
        self.append_log(msg, theme['SUCCESS_COLOR'])
        self.show_status_message(_('preparing', format=audio_format.upper()), theme['PRIMARY_COLOR'])
        
        self.download_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.progress.setValue(0)
        
        self.worker_thread = DownloadWorker(url, output, audio_format, quality)
        self.worker_thread.progress_updated.connect(self.update_progress)
        self.worker_thread.log_message.connect(self.handle_log_message)
        self.worker_thread.download_finished.connect(self.handle_download_finished)
        
        start_msg = f"Start: {time.strftime('%H:%M:%S')} - {audio_format.upper()} {quality}kbps"
        self.append_log(start_msg, "#888888")
        
        self.worker_thread.start()

    def cancel_download(self):
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.cancel()
            self.append_log("Canceling...", "#f1c40f")
            self.show_status_message(_('cancel') + "...", ThemeManager.get_theme(self.current_theme)['ERROR_COLOR'])

    def update_progress(self, current, total):
        if total > 0:
            percent = int((current / total) * 100)
            self.progress.setValue(percent)

    def handle_log_message(self, message, level):
        theme = ThemeManager.get_theme(self.current_theme)
        color_map = {
            "error": theme['ERROR_COLOR'],
            "success": theme['SUCCESS_COLOR'],
            "warning": "#f1c40f",
            "info": None
        }
        self.append_log(message, color_map.get(level))

    def handle_download_finished(self, success, message):
        theme = ThemeManager.get_theme(self.current_theme)
        color = theme['SUCCESS_COLOR'] if success else theme['ERROR_COLOR']
        self.append_log(message, color)
        self.show_status_message(message, color)
        
        self.download_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        
        if success: self.progress.setValue(100)
        else: self.progress.setValue(0)
            
        if self.worker_thread:
            self.worker_thread.deleteLater()
            self.worker_thread = None

    def append_log(self, text, color=None):
        font_family = "JetBrains Mono, Fira Code, Monaco, 'Courier New', monospace"
        if color:
            self.output_box.append(f'<span style="color:{color}; font-family:{font_family}; font-size:11px; line-height: 1.7;">{text}</span>')
        else:
            self.output_box.append(f'<span style="font-family:{font_family}; font-size:11px; line-height: 1.7;">{text}</span>')
        
        scrollbar = self.output_box.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def closeEvent(self, event):
        if self.worker_thread and self.worker_thread.isRunning():
            reply = QMessageBox.question(self, 'Close', _('cancel_confirm'),
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
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
