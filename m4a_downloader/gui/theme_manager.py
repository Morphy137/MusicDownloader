"""
Módulo para gestionar Temas Dinámicos (Claros y Oscuros) y colores de la UI.
"""
from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QApplication

THEMES = {
    # === TEMAS OSCUROS ===
    "dark_mora": {
        "name": "Mora Oscura (Defecto)",
        "is_dark": True,
        "PRIMARY_COLOR": "#E94560",
        "PRIMARY_DARK": "#B8233A",
        "BG_COLOR": "#181A20",
        "FG_COLOR": "#F5F6FA",
        "ENTRY_BG": "#23243A",
        "SUCCESS_COLOR": "#22C55E",
        "ERROR_COLOR": "#F43F5E",
    },
    "dark_ocean": {
        "name": "Océano Noche",
        "is_dark": True,
        "PRIMARY_COLOR": "#3498db",
        "PRIMARY_DARK": "#2980b9",
        "BG_COLOR": "#1a252c",
        "FG_COLOR": "#ecf0f1",
        "ENTRY_BG": "#2c3e50",
        "SUCCESS_COLOR": "#2ecc71",
        "ERROR_COLOR": "#e74c3c",
    },
    "dark_forest": {
        "name": "Bosque Oscuro",
        "is_dark": True,
        "PRIMARY_COLOR": "#2ecc71",
        "PRIMARY_DARK": "#27ae60",
        "BG_COLOR": "#1a2f1a",
        "FG_COLOR": "#e8f8f5",
        "ENTRY_BG": "#2c4a30",
        "SUCCESS_COLOR": "#f1c40f",
        "ERROR_COLOR": "#e74c3c",
    },
    "dark_purple": {
        "name": "Púrpura Neón",
        "is_dark": True,
        "PRIMARY_COLOR": "#9b59b6",
        "PRIMARY_DARK": "#8e44ad",
        "BG_COLOR": "#1e1a25",
        "FG_COLOR": "#f4ecf7",
        "ENTRY_BG": "#2c243a",
        "SUCCESS_COLOR": "#2ecc71",
        "ERROR_COLOR": "#e74c3c",
    },

    # === TEMAS CLAROS ===
    "light_snow": {
        "name": "Blanco Nieve",
        "is_dark": False,
        "PRIMARY_COLOR": "#E94560",
        "PRIMARY_DARK": "#B8233A",
        "BG_COLOR": "#f5f6fa",
        "FG_COLOR": "#2d3436",
        "ENTRY_BG": "#ffffff",
        "SUCCESS_COLOR": "#27ae60",
        "ERROR_COLOR": "#c0392b",
    },
    "light_sky": {
        "name": "Cielo Claro",
        "is_dark": False,
        "PRIMARY_COLOR": "#3498db",
        "PRIMARY_DARK": "#2980b9",
        "BG_COLOR": "#e8f4f8",
        "FG_COLOR": "#2c3e50",
        "ENTRY_BG": "#ffffff",
        "SUCCESS_COLOR": "#27ae60",
        "ERROR_COLOR": "#c0392b",
    },
    "light_mint": {
        "name": "Menta Fresca",
        "is_dark": False,
        "PRIMARY_COLOR": "#2ecc71",
        "PRIMARY_DARK": "#27ae60",
        "BG_COLOR": "#e9f7ef",
        "FG_COLOR": "#145a32",
        "ENTRY_BG": "#ffffff",
        "SUCCESS_COLOR": "#f39c12",
        "ERROR_COLOR": "#c0392b",
    },
    "light_warm": {
        "name": "Crema Suave",
        "is_dark": False,
        "PRIMARY_COLOR": "#d35400",
        "PRIMARY_DARK": "#a04000",
        "BG_COLOR": "#fdfbf7",
        "FG_COLOR": "#3e2723",
        "ENTRY_BG": "#ffffff",
        "SUCCESS_COLOR": "#27ae60",
        "ERROR_COLOR": "#c0392b",
    }
}

class ThemeManager:
    @staticmethod
    def get_theme_names():
        return [(k, v["name"]) for k, v in THEMES.items()]
    
    @staticmethod
    def get_default_theme():
        return "dark_mora"
        
    @staticmethod
    def get_theme(theme_id):
        return THEMES.get(theme_id, THEMES["dark_mora"])
    
    @staticmethod
    def get_stylesheet(theme_id):
        thm = ThemeManager.get_theme(theme_id)
        
        return f"""
        QWidget {{ 
            background: {thm["BG_COLOR"]}; 
            color: {thm["FG_COLOR"]};
            font-family: 'Segoe UI', 'Inter', sans-serif;
        }}
        QLineEdit {{ 
            background: {thm["ENTRY_BG"]}; 
            color: {thm["FG_COLOR"]}; 
            border-radius: 12px; 
            padding: 12px 16px; 
            border: 2px solid transparent;
            font-size: 14px;
            font-weight: 400;
            min-height: 24px;
        }}
        QLineEdit:focus {{
            border: 2px solid {thm["PRIMARY_COLOR"]};
        }}
        QComboBox {{
            background: {thm["ENTRY_BG"]};
            color: {thm["FG_COLOR"]};
            border-radius: 8px;
            padding: 8px 12px;
            border: 1px solid #444 if {thm["is_dark"]} else 1px solid #ccc;
            font-size: 13px;
            min-width: 80px;
        }}
        QComboBox:focus {{
            border: 2px solid {thm["PRIMARY_COLOR"]};
        }}
        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}
        QComboBox QAbstractItemView {{
            background: {thm["ENTRY_BG"]};
            color: {thm["FG_COLOR"]};
            selection-background-color: {thm["PRIMARY_COLOR"]};
        }}
        QTextEdit {{ 
            background: {thm["BG_COLOR"]}; 
            color: {thm["FG_COLOR"]}; 
            border-radius: 12px; 
            border: 2px solid {thm["ENTRY_BG"]}; 
            font-size: 12px;
            padding: 8px;
        }}
        QPushButton {{ 
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 {thm["PRIMARY_COLOR"]}, stop: 1 {thm["PRIMARY_DARK"]}); 
            color: white; 
            border-radius: 12px; 
            padding: 12px 20px; 
            font-weight: 600; 
            font-size: 14px;
            border: none;
        }}
        QPushButton:hover {{ 
            opacity: 0.9;
            background: {thm["PRIMARY_COLOR"]};
        }}
        QPushButton:disabled {{
            background: #404040 if {thm["is_dark"]} else #dcdcdc;
            color: #888;
        }}
        QPushButton[type="secondary"] {{
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 {thm["PRIMARY_COLOR"]}, stop: 1 {thm["PRIMARY_DARK"]});
            border: 1px solid {thm["ENTRY_BG"]};
            color: white;
            border-radius: 12px;
            padding: 8px;
        }}
        QPushButton[type="secondary"]:hover {{
            background: {thm["PRIMARY_COLOR"]};
        }}
        QProgressBar {{ 
            background: {thm["ENTRY_BG"]}; 
            border-radius: 12px; 
            text-align: center; 
            color: {thm["FG_COLOR"]}; 
            font-size: 12px; 
            font-weight: 500;
        }}
        QProgressBar::chunk {{ 
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 {thm["PRIMARY_COLOR"]}, stop: 1 {thm["PRIMARY_DARK"]}); 
            border-radius: 11px;
        }}
        QLabel {{
            color: {thm["FG_COLOR"]};
            font-weight: 500;
        }}
        QGroupBox {{
            font-weight: bold;
            border: 2px solid {thm["ENTRY_BG"]};
            border-radius: 12px;
            margin-top: 1ex;
            padding-top: 10px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }}
        QTabWidget::pane {{
            border: 1px solid {thm["ENTRY_BG"]};
            border-radius: 8px;
            background: {thm["BG_COLOR"]};
        }}
        QTabBar::tab {{
            background: {thm["ENTRY_BG"]};
            color: {thm["FG_COLOR"]};
            padding: 10px 16px;
            margin: 2px;
            border-radius: 6px;
        }}
        QTabBar::tab:selected {{
            background: {thm["PRIMARY_COLOR"]};
            color: white;
        }}
        QCheckBox {{
            color: {thm["FG_COLOR"]};
        }}
        """

    @staticmethod
    def apply_theme(widget, theme_id):
        style = ThemeManager.get_stylesheet(theme_id)
        widget.setStyleSheet(style)
        return ThemeManager.get_theme(theme_id)
