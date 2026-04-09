# morphydownloader/gui/config_dialog.py
import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTextEdit, QCheckBox, QMessageBox, QTabWidget, QWidget, 
    QFileDialog, QComboBox, QGroupBox, QSpinBox, QScrollArea
)
from PySide6.QtGui import QFont, QIcon, QDesktopServices
from PySide6.QtCore import Qt, QUrl, QSettings, Signal
from ..config import Config
from .theme_manager import ThemeManager
from ..locales import _, translator

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
    theme_changed = Signal(str)
    language_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings('MorphyDownloader', 'Config')
        self.current_theme = self.settings.value('theme', ThemeManager.get_default_theme())
        self.init_ui()
        self.load_settings()
        self.check_ffmpeg_status()
        self.apply_theme()
        
    def init_ui(self):
        self.setWindowTitle(_('settings'))
        
        # Tamaño mínimo seguro para pantallas pequeñas (ej. 1366x768) y scroll para que no se corte
        self.setMinimumSize(500, 500)
        self.resize(650, 650)
        self.setModal(True)
        
        # Configurar icono de aplicación
        app_icon_path = Config.get_asset_path(ICON_PATHS['app_icon'])
        if os.path.exists(app_icon_path):
            self.setWindowIcon(QIcon(app_icon_path))
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Título principal
        title_label = QLabel(_('welcome'))
        title_label.setFont(QFont('Inter', 18, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        subtitle_label = QLabel(_('initial_setup_subtitle'))
        subtitle_label.setFont(QFont('Inter', 11))
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(subtitle_label)
        
        # Tabs de configuración envueltos en ScrollArea
        self.tabs = QTabWidget()
        
        # Wrapper con Scroll Areas
        cred_sa = QScrollArea(); cred_sa.setWidgetResizable(True)
        cred_sa.setWidget(self.create_credentials_tab())
        self.tabs.addTab(cred_sa, _('tab_credentials'))
        
        format_sa = QScrollArea(); format_sa.setWidgetResizable(True)
        format_sa.setWidget(self.create_format_tab())
        self.tabs.addTab(format_sa, _('tab_format'))
        
        settings_sa = QScrollArea(); settings_sa.setWidgetResizable(True)
        settings_sa.setWidget(self.create_settings_tab())
        self.tabs.addTab(settings_sa, _('tab_settings'))
        
        main_layout.addWidget(self.tabs)
        
        # Botones de acción
        button_layout = QHBoxLayout()
        
        test_btn = QPushButton(_('test_credentials'))
        self._set_icon_or_text(test_btn, 'test', _('test_credentials'))
        test_btn.clicked.connect(self.test_credentials_only)
        test_btn.setProperty("type", "secondary")
        
        save_btn = QPushButton(_('save_continue'))
        self._set_icon_or_text(save_btn, 'save', _('save_continue'))
        save_btn.clicked.connect(self.save_and_close)
        save_btn.setDefault(True)
        save_btn.setMinimumWidth(150)
        
        cancel_btn = QPushButton(_('cancel'))
        self._set_icon_or_text(cancel_btn, 'cancel', _('cancel'))
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setProperty("type", "secondary")
        
        button_layout.addWidget(test_btn)
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
    
    def apply_theme(self):
        ThemeManager.apply_theme(self, self.current_theme)

    def _set_icon_or_text(self, button, icon_key, fallback_text):
        icon_path = Config.get_asset_path(ICON_PATHS.get(icon_key, ''))
        if os.path.exists(icon_path):
            button.setIcon(QIcon(icon_path))
            button.setText(' ' + fallback_text) 
        else:
            button.setText(fallback_text)
    
    def create_credentials_tab(self):
        cred_widget = QWidget()
        cred_layout = QVBoxLayout(cred_widget)
        cred_layout.setSpacing(15)
        
        welcome_label = QLabel(_('spotify_welcome'))
        welcome_label.setFont(QFont('Inter', 11))
        welcome_label.setWordWrap(True)
        cred_layout.addWidget(welcome_label)
        
        instructions_label = QLabel(_('spotify_instructions'))
        instructions_label.setFont(QFont('Inter', 11))
        instructions_label.setWordWrap(True)
        cred_layout.addWidget(instructions_label)
        
        steps_text = QTextEdit()
        steps_text.setReadOnly(True)
        steps_text.setFixedHeight(180)
        steps_text.setHtml(f"""
        <ol style="line-height: 1.6; font-size: 13px;">
            <li>{_('open_dashboard')}</li>
            <li>Create App &rarr; App Name: MorphyDownloader</li>
            <li>Redirect URI: http://localhost:8080/callback</li>
            <li>Copy Client ID & Client Secret</li>
        </ol>
        """)
        cred_layout.addWidget(steps_text)
        
        open_spotify_btn = QPushButton(_('open_dashboard'))
        self._set_icon_or_text(open_spotify_btn, 'web', _('open_dashboard'))
        open_spotify_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl('https://developer.spotify.com/dashboard/')))
        cred_layout.addWidget(open_spotify_btn)
        
        cred_layout.addWidget(QLabel(_('client_id')))
        self.client_id_entry = QLineEdit()
        cred_layout.addWidget(self.client_id_entry)
        
        cred_layout.addWidget(QLabel(_('client_secret')))
        self.client_secret_entry = QLineEdit()
        self.client_secret_entry.setEchoMode(QLineEdit.EchoMode.Password)
        cred_layout.addWidget(self.client_secret_entry)
        
        self.show_secret_cb = QCheckBox(_('show_secret'))
        self.show_secret_cb.stateChanged.connect(self.toggle_secret_visibility)
        cred_layout.addWidget(self.show_secret_cb)
        
        cred_layout.addStretch()
        return cred_widget
    
    def create_format_tab(self):
        format_widget = QWidget()
        format_layout = QVBoxLayout(format_widget)
        
        format_group = QGroupBox(_('tab_format'))
        format_group_layout = QVBoxLayout(format_group)
        
        format_layout_inner = QHBoxLayout()
        format_layout_inner.addWidget(QLabel(_('format')))
        self.format_combo = QComboBox()
        self.format_combo.addItems(['m4a', 'mp3'])
        self.format_combo.currentTextChanged.connect(self.on_format_changed)
        format_layout_inner.addWidget(self.format_combo)
        format_layout_inner.addStretch()
        format_group_layout.addLayout(format_layout_inner)
        
        self.format_info_label = QLabel()
        self.format_info_label.setWordWrap(True)
        format_group_layout.addWidget(self.format_info_label)
        format_layout.addWidget(format_group)
        
        ffmpeg_group = QGroupBox("FFmpeg")
        ffmpeg_layout = QVBoxLayout(ffmpeg_group)
        self.ffmpeg_status_label = QLabel()
        self.ffmpeg_status_label.setWordWrap(True)
        ffmpeg_layout.addWidget(self.ffmpeg_status_label)
        
        check_ffmpeg_btn = QPushButton(_('check_ffmpeg'))
        check_ffmpeg_btn.clicked.connect(self.check_ffmpeg_status)
        ffmpeg_layout.addWidget(check_ffmpeg_btn)
        
        format_layout.addWidget(ffmpeg_group)
        format_layout.addStretch()
        
        return format_widget
    
    def create_settings_tab(self):
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        
        # --- Grupo Apariencia y UI ---
        ui_group = QGroupBox(_('appearance_group'))
        ui_layout = QVBoxLayout(ui_group)
        
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel(_('language')))
        self.lang_combo = QComboBox()
        # Mapeo de códigos
        self.lang_combo.addItem("English", "en")
        self.lang_combo.addItem("Español", "es")
        self.lang_combo.currentIndexChanged.connect(self.on_language_combobox_changed)
        lang_layout.addWidget(self.lang_combo)
        lang_layout.addStretch()
        ui_layout.addLayout(lang_layout)
        
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel(_('theme')))
        self.theme_combo = QComboBox()
        for theme_id, theme_name in ThemeManager.get_theme_names():
            translated_name = _(f'theme_{theme_id}')
            if translated_name == f'theme_{theme_id}':
                translated_name = theme_name
            self.theme_combo.addItem(translated_name, theme_id)
        self.theme_combo.currentIndexChanged.connect(self.on_theme_changed)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        ui_layout.addLayout(theme_layout)
        
        settings_layout.addWidget(ui_group)
        
        # --- Grupo Archivos y Carpetas ---
        file_group = QGroupBox(_('files_group'))
        file_layout = QVBoxLayout(file_group)
        
        file_layout.addWidget(QLabel(_('output_folder')))
        default_output_layout = QHBoxLayout()
        self.output_dir_entry = QLineEdit(os.path.abspath('music'))
        
        browse_btn = QPushButton()
        self._set_icon_or_text(browse_btn, 'folder_browse', _('browse'))
        browse_btn.clicked.connect(self.browse_output_dir)
        default_output_layout.addWidget(self.output_dir_entry)
        default_output_layout.addWidget(browse_btn)
        file_layout.addLayout(default_output_layout)
        
        file_layout.addWidget(QLabel(_('file_naming')))
        self.naming_combo = QComboBox()
        self.naming_combo.addItem(_('naming_default'), "{title}.{ext}")
        self.naming_combo.addItem(_('naming_artist_title'), "{artist} - {title}.{ext}")
        self.naming_combo.addItem(_('naming_track_title'), "{track_number}. {title}.{ext}")
        file_layout.addWidget(self.naming_combo)
        
        self.subfolders_cb = QCheckBox(_('create_subfolders'))
        file_layout.addWidget(self.subfolders_cb)

        self.lyrics_cb = QCheckBox(_('download_lyrics'))
        file_layout.addWidget(self.lyrics_cb)
        
        settings_layout.addWidget(file_group)
        
        # --- Grupo Avanzado ---
        adv_group = QGroupBox(_('advanced_group'))
        adv_layout = QVBoxLayout(adv_group)
        
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel(_('quality')))
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(Config.SUPPORTED_QUALITY)
        self.quality_combo.setCurrentText(Config.DEFAULT_QUALITY)
        quality_layout.addWidget(self.quality_combo)
        quality_layout.addStretch()
        adv_layout.addLayout(quality_layout)
        
        parallel_layout = QHBoxLayout()
        parallel_layout.addWidget(QLabel(_('parallel_downloads')))
        self.parallel_spinbox = QSpinBox()
        self.parallel_spinbox.setRange(1, 8)
        self.parallel_spinbox.setValue(2)
        parallel_layout.addWidget(self.parallel_spinbox)
        parallel_layout.addStretch()
        adv_layout.addLayout(parallel_layout)
        
        self.dont_show_again_cb = QCheckBox(_('dont_show_startup'))
        adv_layout.addWidget(self.dont_show_again_cb)
        
        settings_layout.addWidget(adv_group)
        settings_layout.addStretch()
        
        return settings_widget

    def on_language_combobox_changed(self):
        selected_lang_code = self.lang_combo.currentData()
        translator.set_language(selected_lang_code)
        # We don't reconstruct the full UI automatically here to avoid losing state,
        # usually users must restart for all strings to apply, or we emit signal.
        # But we do keep the config saved.

    def on_theme_changed(self):
        theme_id = self.theme_combo.currentData()
        self.current_theme = theme_id
        self.apply_theme()

    def on_format_changed(self, format_type):
        format_info = Config.get_format_info(format_type)
        self.format_info_label.setText(f"{format_info['description']}")
    
    def check_ffmpeg_status(self):
        if Config.check_ffmpeg():
            ffmpeg_path = Config.get_ffmpeg_path()
            self.ffmpeg_status_label.setText("✅ FFmpeg " + _('ffmpeg_available') + f"\n({ffmpeg_path})")
        else:
            self.ffmpeg_status_label.setText("⚠️ " + _('ffmpeg_unavailable'))
        self.on_format_changed(self.format_combo.currentText())
    
    def toggle_secret_visibility(self, state):
        if state == Qt.CheckState.Checked.value:
            self.client_secret_entry.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.client_secret_entry.setEchoMode(QLineEdit.EchoMode.Password)
    
    def browse_output_dir(self):
        folder = QFileDialog.getExistingDirectory(self, _('output_folder'))
        if folder:
            self.output_dir_entry.setText(folder)
    
    def test_credentials_only(self):
        if self.test_credentials():
            QMessageBox.information(self, _('success'), '✅ Spotify Credentials OK!')
        else:
            QMessageBox.warning(self, _('error'), '❌ Spotify Credentials Error.')
    
    def test_credentials(self):
        client_id = self.client_id_entry.text().strip()
        client_secret = self.client_secret_entry.text().strip()
        if not client_id or not client_secret:
            return False
        
        old_id = os.environ.get('SPOTIPY_CLIENT_ID')
        old_secret = os.environ.get('SPOTIPY_CLIENT_SECRET')
        os.environ['SPOTIPY_CLIENT_ID'] = client_id
        os.environ['SPOTIPY_CLIENT_SECRET'] = client_secret
        
        try:
            from ..core.spotify_client import SpotifyClient
            spotify = SpotifyClient()
            spotify.get_track_info('https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh')
            return True
        except Exception:
            return False
        finally:
            if old_id: os.environ['SPOTIPY_CLIENT_ID'] = old_id
            else: os.environ.pop('SPOTIPY_CLIENT_ID', None)
            if old_secret: os.environ['SPOTIPY_CLIENT_SECRET'] = old_secret
            else: os.environ.pop('SPOTIPY_CLIENT_SECRET', None)
    
    def save_and_close(self):
        client_id = self.client_id_entry.text().strip()
        client_secret = self.client_secret_entry.text().strip()
        
        if not client_id or not client_secret:
            QMessageBox.warning(self, _('error'), 'Please fill Spotify Credentials')
            return
        
        selected_format = self.format_combo.currentText()
        if selected_format == 'mp3' and not Config.check_ffmpeg():
            reply = QMessageBox.question(self, 'FFmpeg', _('ffmpeg_missing_warn'),
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if reply == QMessageBox.Yes:
                selected_format = 'm4a'
                self.format_combo.setCurrentText('m4a')
            else:
                return
        
        if not self.test_credentials():
            reply = QMessageBox.question(self, 'Credentials Error', 'Invalid Credentials. Save anyway?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No: return
        
        # Save to QSettings
        self.settings.setValue('spotify_client_id', client_id)
        self.settings.setValue('spotify_client_secret', client_secret)
        self.settings.setValue('audio_format', selected_format)
        self.settings.setValue('audio_quality', self.quality_combo.currentText())
        self.settings.setValue('theme', self.theme_combo.currentData())
        self.settings.setValue('language', self.lang_combo.currentData())
        self.settings.setValue('naming_format', self.naming_combo.currentData())
        self.settings.setValue('create_subfolders', self.subfolders_cb.isChecked())
        self.settings.setValue('download_lyrics', self.lyrics_cb.isChecked())
        self.settings.setValue('parallel_downloads', self.parallel_spinbox.value())
        self.settings.setValue('default_output_dir', self.output_dir_entry.text())
        self.settings.setValue('dont_show_config', self.dont_show_again_cb.isChecked())
        
        os.environ['SPOTIPY_CLIENT_ID'] = client_id
        os.environ['SPOTIPY_CLIENT_SECRET'] = client_secret
        
        # Emitir señales para actualizar main UI
        self.language_changed.emit(self.lang_combo.currentData())
        self.theme_changed.emit(self.theme_combo.currentData())
        
        QMessageBox.information(self, _('success'), 'Config Saved!')
        self.accept()
    
    def load_settings(self):
        if self.settings.value('spotify_client_id'):
            self.client_id_entry.setText(self.settings.value('spotify_client_id'))
        if self.settings.value('spotify_client_secret'):
            self.client_secret_entry.setText(self.settings.value('spotify_client_secret'))
        if self.settings.value('default_output_dir'):
            self.output_dir_entry.setText(self.settings.value('default_output_dir'))
        
        saved_format = self.settings.value('audio_format', Config.DEFAULT_FORMAT)
        if saved_format in Config.SUPPORTED_FORMATS:
            self.format_combo.setCurrentText(saved_format)
        
        saved_quality = self.settings.value('audio_quality', Config.DEFAULT_QUALITY)
        if saved_quality in Config.SUPPORTED_QUALITY:
            self.quality_combo.setCurrentText(saved_quality)

        # Cargar idioma
        saved_lang = self.settings.value('language', 'en')
        index_lang = self.lang_combo.findData(saved_lang)
        if index_lang >= 0: self.lang_combo.setCurrentIndex(index_lang)
        
        # Cargar tema
        saved_theme = self.settings.value('theme', ThemeManager.get_default_theme())
        index_theme = self.theme_combo.findData(saved_theme)
        if index_theme >= 0: self.theme_combo.setCurrentIndex(index_theme)

        # Cargar Template Nombre
        saved_naming = self.settings.value('naming_format', '{title}.{ext}')
        index_naming = self.naming_combo.findData(saved_naming)
        if index_naming >= 0: self.naming_combo.setCurrentIndex(index_naming)

        # Subfolders / Lyrics
        if self.settings.value('create_subfolders', False, type=bool):
            self.subfolders_cb.setChecked(True)
        if self.settings.value('download_lyrics', False, type=bool):
            self.lyrics_cb.setChecked(True)

        saved_parallel = self.settings.value('parallel_downloads', 2, type=int)
        if 1 <= saved_parallel <= 8:
            self.parallel_spinbox.setValue(saved_parallel)
            
        if self.settings.value('dont_show_config', False, type=bool):
            self.dont_show_again_cb.setChecked(True)

def should_show_config():
    settings = QSettings('MorphyDownloader', 'Config')
    if settings.value('dont_show_config', False, type=bool):
        if settings.value('spotify_client_id') and settings.value('spotify_client_secret'):
            return False
    if not os.environ.get('SPOTIPY_CLIENT_ID') or not os.environ.get('SPOTIPY_CLIENT_SECRET'):
        return True
    return False

def load_saved_config():
    settings = QSettings('MorphyDownloader', 'Config')
    if settings.value('spotify_client_id') and settings.value('spotify_client_secret'):
        os.environ['SPOTIPY_CLIENT_ID'] = settings.value('spotify_client_id')
        os.environ['SPOTIPY_CLIENT_SECRET'] = settings.value('spotify_client_secret')

def get_saved_audio_format():
    return QSettings('MorphyDownloader', 'Config').value('audio_format', Config.DEFAULT_FORMAT)

def get_saved_audio_quality():
    return QSettings('MorphyDownloader', 'Config').value('audio_quality', Config.DEFAULT_QUALITY)

def get_saved_parallel_downloads():
    return QSettings('MorphyDownloader', 'Config').value('parallel_downloads', 2, type=int)