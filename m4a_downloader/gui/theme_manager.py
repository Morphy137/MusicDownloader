"""
Módulo para gestionar Temas Dinámicos (Claros y Oscuros) y colores de la UI.
"""
from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QApplication

THEMES = {
    # === TEMAS OSCUROS MINIMALISTAS ===
    "dark_mora": {
        "name": "Mora Oscura (Defecto)",
        "is_dark": True,
        "PRIMARY_COLOR": "#6C5CE7",
        "PRIMARY_DARK": "#5A49E0",
        "PRIMARY_LIGHT": "#8172F8",
        "BG_COLOR": "#12131C",
        "SURFACE_BG": "#1A1B28",
        "FG_COLOR": "#F1F3F9",
        "MUTED_FG": "#8C92B1",
        "ENTRY_BG": "#222434",
        "BORDER_COLOR": "#2E3146",
        "SUCCESS_COLOR": "#10B981",
        "ERROR_COLOR": "#EF4444",
    },
    "dark_ocean": {
        "name": "Océano Noche",
        "is_dark": True,
        "PRIMARY_COLOR": "#0091FF",
        "PRIMARY_DARK": "#0072C6",
        "PRIMARY_LIGHT": "#33A7FF",
        "BG_COLOR": "#0F172A",
        "SURFACE_BG": "#1E293B",
        "FG_COLOR": "#F8FAFC",
        "MUTED_FG": "#94A3B8",
        "ENTRY_BG": "#334155",
        "BORDER_COLOR": "#475569",
        "SUCCESS_COLOR": "#10B981",
        "ERROR_COLOR": "#F43F5E",
    },
    "dark_forest": {
        "name": "Bosque Oscuro",
        "is_dark": True,
        "PRIMARY_COLOR": "#10B981",
        "PRIMARY_DARK": "#059669",
        "PRIMARY_LIGHT": "#34D399",
        "BG_COLOR": "#061A14",
        "SURFACE_BG": "#0D2A20",
        "FG_COLOR": "#ECFDF5",
        "MUTED_FG": "#6EE7B7",
        "ENTRY_BG": "#133E30",
        "BORDER_COLOR": "#1F5140",
        "SUCCESS_COLOR": "#34D399",
        "ERROR_COLOR": "#F87171",
    },
    "dark_purple": {
        "name": "Púrpura Neón",
        "is_dark": True,
        "PRIMARY_COLOR": "#D946EF",
        "PRIMARY_DARK": "#C026D3",
        "PRIMARY_LIGHT": "#E879F9",
        "BG_COLOR": "#160C22",
        "SURFACE_BG": "#231435",
        "FG_COLOR": "#FAF5FF",
        "MUTED_FG": "#A855F7",
        "ENTRY_BG": "#321D4B",
        "BORDER_COLOR": "#462768",
        "SUCCESS_COLOR": "#22C55E",
        "ERROR_COLOR": "#FF4B4B",
    },

    # === TEMAS CLAROS MINIMALISTAS ===
    "light_snow": {
        "name": "Blanco Nieve",
        "is_dark": False,
        "PRIMARY_COLOR": "#6C5CE7",
        "PRIMARY_DARK": "#5A49E0",
        "PRIMARY_LIGHT": "#8172F8",
        "BG_COLOR": "#F8FAFC",
        "SURFACE_BG": "#FFFFFF",
        "FG_COLOR": "#0F172A",
        "MUTED_FG": "#64748B",
        "ENTRY_BG": "#F1F5F9",
        "BORDER_COLOR": "#E2E8F0",
        "SUCCESS_COLOR": "#059669",
        "ERROR_COLOR": "#DC2626",
    },
    "light_sky": {
        "name": "Cielo Claro",
        "is_dark": False,
        "PRIMARY_COLOR": "#0284C7",
        "PRIMARY_DARK": "#0369A1",
        "PRIMARY_LIGHT": "#38BDF8",
        "BG_COLOR": "#F0F9FF",
        "SURFACE_BG": "#FFFFFF",
        "FG_COLOR": "#0C4A6E",
        "MUTED_FG": "#0284C7",
        "ENTRY_BG": "#E0F2FE",
        "BORDER_COLOR": "#BAE6FD",
        "SUCCESS_COLOR": "#10B981",
        "ERROR_COLOR": "#E11D48",
    },
    "light_mint": {
        "name": "Menta Fresca",
        "is_dark": False,
        "PRIMARY_COLOR": "#059669",
        "PRIMARY_DARK": "#047857",
        "PRIMARY_LIGHT": "#10B981",
        "BG_COLOR": "#ECFDF5",
        "SURFACE_BG": "#FFFFFF",
        "FG_COLOR": "#064E3B",
        "MUTED_FG": "#059669",
        "ENTRY_BG": "#D1FAE5",
        "BORDER_COLOR": "#A7F3D0",
        "SUCCESS_COLOR": "#059669",
        "ERROR_COLOR": "#DC2626",
    },
    "light_warm": {
        "name": "Crema Suave",
        "is_dark": False,
        "PRIMARY_COLOR": "#EA580C",
        "PRIMARY_DARK": "#C2410C",
        "PRIMARY_LIGHT": "#F97316",
        "BG_COLOR": "#FFFBEB",
        "SURFACE_BG": "#FFFFFF",
        "FG_COLOR": "#78350F",
        "MUTED_FG": "#D97706",
        "ENTRY_BG": "#FEF3C7",
        "BORDER_COLOR": "#FDE68A",
        "SUCCESS_COLOR": "#16A34A",
        "ERROR_COLOR": "#DC2626",
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
        surface_bg = thm.get("SURFACE_BG", thm["BG_COLOR"])
        border_col = thm.get("BORDER_COLOR", thm["ENTRY_BG"])
        muted_fg = thm.get("MUTED_FG", "#888888")
        primary_light = thm.get("PRIMARY_LIGHT", thm["PRIMARY_COLOR"])

        return f"""
        QWidget {{ 
            background-color: {thm["BG_COLOR"]};
            color: {thm["FG_COLOR"]};
            font-family: 'Inter', 'Segoe UI', -apple-system, sans-serif;
        }}

        QFrame[class="card"] {{
            background-color: {surface_bg};
            border: 1px solid {border_col};
            border-radius: 16px;
        }}

        QLineEdit {{ 
            background-color: {thm["ENTRY_BG"]};
            color: {thm["FG_COLOR"]}; 
            border-radius: 12px; 
            padding: 10px 16px;
            border: 1px solid {border_col};
            font-size: 13px;
            font-weight: 400;
            selection-background-color: {thm["PRIMARY_COLOR"]};
        }}
        QLineEdit:focus {{
            border: 2px solid {thm["PRIMARY_COLOR"]};
            background-color: {surface_bg};
        }}

        QComboBox {{
            background-color: {thm["ENTRY_BG"]};
            color: {thm["FG_COLOR"]};
            border-radius: 10px;
            padding: 8px 14px;
            border: 1px solid {border_col};
            font-size: 13px;
            font-weight: 500;
            min-width: 90px;
        }}
        QComboBox:focus {{
            border: 2px solid {thm["PRIMARY_COLOR"]};
        }}
        QComboBox::drop-down {{
            border: none;
            width: 24px;
        }}
        QComboBox QAbstractItemView {{
            background-color: {surface_bg};
            color: {thm["FG_COLOR"]};
            border: 1px solid {border_col};
            border-radius: 8px;
            selection-background-color: {thm["PRIMARY_COLOR"]};
            padding: 4px;
        }}

        QTextEdit {{ 
            background-color: {thm["ENTRY_BG"]};
            color: {thm["FG_COLOR"]}; 
            border-radius: 14px;
            border: 1px solid {border_col};
            font-size: 12px;
            padding: 10px;
            line-height: 1.6;
        }}

        QPushButton {{ 
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {thm["PRIMARY_COLOR"]}, stop:1 {primary_light});
            color: white; 
            border-radius: 12px; 
            padding: 10px 20px;
            font-weight: 600; 
            font-size: 13px;
            border: none;
        }}
        QPushButton:hover {{ 
            background: {thm["PRIMARY_DARK"]};
        }}
        QPushButton:disabled {{
            background-color: {'#2A2C3C' if thm['is_dark'] else '#E2E8F0'};
            color: {'#5A5E78' if thm['is_dark'] else '#94A3B8'};
            border: none;
        }}

        QPushButton[type="secondary"] {{
            background: {thm["ENTRY_BG"]};
            border: 1px solid {border_col};
            color: {thm["FG_COLOR"]};
            border-radius: 12px;
            padding: 8px;
            font-weight: 500;
        }}
        QPushButton[type="secondary"]:hover {{
            background: {border_col};
            color: {thm["PRIMARY_COLOR"]};
        }}

        QProgressBar {{ 
            background-color: {thm["ENTRY_BG"]};
            border-radius: 10px;
            text-align: center; 
            color: {thm["FG_COLOR"]}; 
            font-size: 11px;
            font-weight: 600;
            border: 1px solid {border_col};
        }}
        QProgressBar::chunk {{ 
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 {thm["PRIMARY_COLOR"]}, stop: 1 {primary_light});
            border-radius: 9px;
        }}

        QLabel {{
            color: {thm["FG_COLOR"]};
            font-weight: 500;
        }}
        QLabel[class="muted"] {{
            color: {muted_fg};
            font-size: 12px;
        }}

        QGroupBox {{
            font-weight: 600;
            border: 1px solid {border_col};
            border-radius: 14px;
            margin-top: 1ex;
            padding-top: 14px;
            background-color: {surface_bg};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 14px;
            padding: 0 6px 0 6px;
            color: {thm["PRIMARY_COLOR"]};
        }}

        QTabWidget::pane {{
            border: 1px solid {border_col};
            border-radius: 12px;
            background-color: {surface_bg};
        }}
        QTabBar::tab {{
            background-color: {thm["ENTRY_BG"]};
            color: {thm["FG_COLOR"]};
            padding: 8px 18px;
            margin: 3px;
            border-radius: 8px;
            font-weight: 500;
        }}
        QTabBar::tab:selected {{
            background-color: {thm["PRIMARY_COLOR"]};
            color: white;
            font-weight: 600;
        }}

        QCheckBox {{
            color: {thm["FG_COLOR"]};
            font-size: 13px;
            spacing: 8px;
        }}
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border-radius: 5px;
            border: 1px solid {border_col};
            background-color: {thm["ENTRY_BG"]};
        }}
        QCheckBox::indicator:checked {{
            background-color: {thm["PRIMARY_COLOR"]};
            border-color: {thm["PRIMARY_COLOR"]};
        }}
        """

    @staticmethod
    def apply_theme(widget, theme_id):
        style = ThemeManager.get_stylesheet(theme_id)
        widget.setStyleSheet(style)
        return ThemeManager.get_theme(theme_id)
