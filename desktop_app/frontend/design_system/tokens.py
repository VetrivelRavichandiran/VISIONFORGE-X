"""VISIONFORGE X - Enhanced Design System (Color, Typography, Spacing tokens)."""
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QColor, QFont, QFontDatabase
from PySide6.QtCore import Qt


class DesignTokens:
    """Central design token definitions - Enhanced Cyberpunk Industrial."""

    # ---- Colors ----
    # Backgrounds (deeper, richer)
    BG_OBSIDIAN = "#060A12"        # Deepest background
    BG_NAVY = "#0A0F1C"            # Secondary background
    BG_GRAPHITE = "#111A2B"        # Panel background
    BG_GRAPHITE_LIGHT = "#1A2740"  # Lighter panel / hover
    BG_SURFACE = "#0F1724"         # Card surface

    # Accents (vibrant, glowing)
    ACCENT_CYAN = "#00E5FF"        # Active processing, telemetry
    ACCENT_CYAN_GLOW = "#00E5FF40" # Cyan glow
    ACCENT_TEAL = "#00E5A0"        # Secondary accent
    ACCENT_VIOLET = "#9D65FF"      # AI-related functions
    ACCENT_VIOLET_GLOW = "#9D65FF40"
    ACCENT_BLUE = "#3B82F6"        # Info
    ACCENT_AMBER = "#FFB300"       # Warning accent

    # Status (more vivid)
    STATUS_GREEN = "#00E676"       # Healthy
    STATUS_GREEN_GLOW = "#00E67633"
    STATUS_AMBER = "#FFB300"       # Warning
    STATUS_AMBER_GLOW = "#FFB30033"
    STATUS_RED = "#FF3B5C"         # Fault / disconnected
    STATUS_RED_GLOW = "#FF3B5C33"
    STATUS_GREY = "#546E7A"        # Inactive

    # Text
    TEXT_PRIMARY = "#E8EDF5"       # Main text
    TEXT_SECONDARY = "#8B95A5"     # Secondary text
    TEXT_MUTED = "#4A5568"         # Muted text
    TEXT_ACCENT = "#00E5FF"        # Accent text

    # Borders
    BORDER_SUBTLE = "#1E2D42"      # Subtle borders
    BORDER_MEDIUM = "#2A3A4E"      # Medium borders
    BORDER_ACCENT = "#00E5FF33"    # Accent-tinted borders
    BORDER_GLOW = "#00E5FF66"      # Glowing accent border

    # Gradients (for special effects)
    GRADIENT_CYAN = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00B8D4, stop:1 #00E5FF)"
    GRADIENT_VIOLET = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7C4DFF, stop:1 #9D65FF)"
    GRADIENT_GREEN = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00C853, stop:1 #00E676)"

    # ---- Typography ----
    FONT_FAMILY = "Segoe UI"
    FONT_MONO = "Consolas"
    FONT_SIZE_TINY = 9
    FONT_SIZE_SMALL = 10
    FONT_SIZE_NORMAL = 11
    FONT_SIZE_MEDIUM = 13
    FONT_SIZE_LARGE = 16
    FONT_SIZE_TITLE = 20
    FONT_SIZE_HEADING = 24
    FONT_SIZE_HERO = 30

    # ---- Spacing ----
    SPACING_XXS = 2
    SPACING_XS = 4
    SPACING_SM = 8
    SPACING_MD = 12
    SPACING_LG = 16
    SPACING_XL = 24
    SPACING_XXL = 32

    # ---- Border Radius ----
    RADIUS_SM = 4
    RADIUS_MD = 8
    RADIUS_LG = 12
    RADIUS_XL = 16
    RADIUS_ROUND = 50

    # ---- Sidebar ----
    SIDEBAR_WIDTH = 230
    SIDEBAR_ICON_SIZE = 20
    TOPBAR_HEIGHT = 50

    # ---- Shadows ----
    SHADOW_COLOR = "#00000040"
    SHADOW_COLOR_STRONG = "#00000060"


def apply_dark_stylesheet(app: QApplication):
    """Apply the enhanced dark industrial stylesheet to the application."""
    t = DesignTokens

    stylesheet = f"""
    QMainWindow, QDialog {{
        background-color: {t.BG_OBSIDIAN};
    }}
    QWidget {{
        background-color: {t.BG_OBSIDIAN};
        color: {t.TEXT_PRIMARY};
        font-family: {t.FONT_FAMILY};
        font-size: {t.FONT_SIZE_NORMAL}px;
    }}
    /* Sidebar */
    QFrame#sidebar {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {t.BG_NAVY}, stop:1 #060A12);
        border-right: 1px solid {t.BORDER_MEDIUM};
    }}
    QFrame#topbar {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {t.BG_NAVY}, stop:1 {t.BG_SURFACE});
        border-bottom: 1px solid {t.BORDER_MEDIUM};
    }}
    QFrame#panel {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {t.BG_GRAPHITE}, stop:1 {t.BG_SURFACE});
        border: 1px solid {t.BORDER_SUBTLE};
        border-radius: {t.RADIUS_MD}px;
    }}
    QFrame#panel_light {{
        background: {t.BG_GRAPHITE_LIGHT};
        border: 1px solid {t.BORDER_SUBTLE};
        border-radius: {t.RADIUS_MD}px;
    }}
    /* Navigation buttons */
    QPushButton#navBtn {{
        background-color: transparent;
        color: {t.TEXT_SECONDARY};
        border: none;
        border-left: 3px solid transparent;
        padding: 12px 16px;
        text-align: left;
        font-size: {t.FONT_SIZE_NORMAL}px;
        border-radius: 0;
    }}
    QPushButton#navBtn:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {t.BG_GRAPHITE}, stop:1 transparent);
        color: {t.TEXT_PRIMARY};
    }}
    QPushButton#navBtn:checked {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {t.BG_GRAPHITE}, stop:1 transparent);
        color: {t.ACCENT_CYAN};
        border-left: 3px solid {t.ACCENT_CYAN};
        font-weight: 600;
    }}
    QPushButton#navBtnIcon {{
        background: transparent;
        border: none;
        color: {t.TEXT_SECONDARY};
        padding: 6px;
    }}
    /* Standard buttons */
    QPushButton {{
        background-color: {t.BG_GRAPHITE_LIGHT};
        color: {t.TEXT_PRIMARY};
        border: 1px solid {t.BORDER_SUBTLE};
        border-radius: {t.RADIUS_SM}px;
        padding: 7px 16px;
        font-size: {t.FONT_SIZE_NORMAL}px;
        transition: all 0.2s;
    }}
    QPushButton:hover {{
        background-color: #243550;
        border-color: {t.ACCENT_CYAN};
        box-shadow: 0 0 8px {t.ACCENT_CYAN_GLOW};
    }}
    QPushButton:pressed {{
        background-color: {t.BG_GRAPHITE};
    }}
    QPushButton#primaryBtn {{
        background: {t.GRADIENT_CYAN};
        color: {t.BG_OBSIDIAN};
        border: none;
        font-weight: 700;
        box-shadow: 0 2px 10px {t.ACCENT_CYAN_GLOW};
    }}
    QPushButton#primaryBtn:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00D4F0, stop:1 #33EBFF);
        box-shadow: 0 4px 16px {t.ACCENT_CYAN_GLOW};
    }}
    QPushButton#dangerBtn {{
        background: {t.STATUS_RED};
        color: white;
        border: none;
    }}
    QPushButton#dangerBtn:hover {{
        background: #FF5070;
        box-shadow: 0 0 10px {t.STATUS_RED_GLOW};
    }}
    QPushButton#successBtn {{
        background: {t.GRADIENT_GREEN};
        color: {t.BG_OBSIDIAN};
        border: none;
        font-weight: 600;
    }}
    QPushButton#successBtn:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00D460, stop:1 #00F580);
    }}
    QPushButton:disabled {{
        background-color: #1A2332;
        color: {t.TEXT_MUTED};
        border: 1px solid #1A2332;
    }}
    /* Labels */
    QLabel {{
        color: {t.TEXT_PRIMARY};
        background: transparent;
    }}
    QLabel#panelTitle {{
        color: {t.ACCENT_CYAN};
        font-size: {t.FONT_SIZE_MEDIUM}px;
        font-weight: 700;
        letter-spacing: 0.5px;
    }}
    QLabel#panelSubtitle {{
        color: {t.TEXT_SECONDARY};
        font-size: {t.FONT_SIZE_SMALL}px;
    }}
    QLabel#metricValue {{
        color: {t.TEXT_PRIMARY};
        font-size: {t.FONT_SIZE_LARGE}px;
        font-weight: 700;
    }}
    QLabel#metricLabel {{
        color: {t.TEXT_SECONDARY};
        font-size: {t.FONT_SIZE_SMALL}px;
    }}
    QLabel#statusGood {{
        color: {t.STATUS_GREEN};
    }}
    QLabel#statusWarn {{
        color: {t.STATUS_AMBER};
    }}
    QLabel#statusError {{
        color: {t.STATUS_RED};
    }}
    QLabel#statusInfo {{
        color: {t.ACCENT_CYAN};
    }}
    QLabel#aiLabel {{
        color: {t.ACCENT_VIOLET};
    }}
    /* Line edits */
    QLineEdit {{
        background-color: {t.BG_OBSIDIAN};
        color: {t.TEXT_PRIMARY};
        border: 1px solid {t.BORDER_SUBTLE};
        border-radius: {t.RADIUS_SM}px;
        padding: 7px 12px;
        font-size: {t.FONT_SIZE_NORMAL}px;
    }}
    QLineEdit:focus {{
        border: 1px solid {t.ACCENT_CYAN};
        box-shadow: 0 0 6px {t.ACCENT_CYAN_GLOW};
    }}
    /* Combo boxes */
    QComboBox {{
        background-color: {t.BG_OBSIDIAN};
        color: {t.TEXT_PRIMARY};
        border: 1px solid {t.BORDER_SUBTLE};
        border-radius: {t.RADIUS_SM}px;
        padding: 6px 12px;
    }}
    QComboBox:focus, QComboBox:on {{
        border: 1px solid {t.ACCENT_CYAN};
    }}
    QComboBox QAbstractItemView {{
        background-color: {t.BG_GRAPHITE};
        color: {t.TEXT_PRIMARY};
        border: 1px solid {t.BORDER_SUBTLE};
        selection-background-color: {t.BG_GRAPHITE_LIGHT};
    }}
    /* Spin boxes */
    QSpinBox, QDoubleSpinBox {{
        background-color: {t.BG_OBSIDIAN};
        color: {t.TEXT_PRIMARY};
        border: 1px solid {t.BORDER_SUBTLE};
        border-radius: {t.RADIUS_SM}px;
        padding: 5px 10px;
    }}
    /* Sliders */
    QSlider::groove:horizontal {{
        background: {t.BG_GRAPHITE_LIGHT};
        height: 5px;
        border-radius: 3px;
    }}
    QSlider::handle:horizontal {{
        background: {t.ACCENT_CYAN};
        width: 16px;
        height: 16px;
        margin: -6px 0;
        border-radius: 8px;
        box-shadow: 0 0 8px {t.ACCENT_CYAN_GLOW};
    }}
    QSlider::sub-page:horizontal {{
        background: {t.GRADIENT_CYAN};
        border-radius: 3px;
    }}
    /* Scroll bars */
    QScrollBar:vertical {{
        background: {t.BG_NAVY};
        width: 10px;
        margin: 0;
        border-radius: 5px;
    }}
    QScrollBar::handle:vertical {{
        background: {t.BORDER_MEDIUM};
        min-height: 30px;
        border-radius: 5px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {t.ACCENT_CYAN};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}
    QScrollBar:horizontal {{
        background: {t.BG_NAVY};
        height: 10px;
        border-radius: 5px;
    }}
    QScrollBar::handle:horizontal {{
        background: {t.BORDER_MEDIUM};
        min-width: 30px;
        border-radius: 5px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background: {t.ACCENT_CYAN};
    }}
    /* Tab widget */
    QTabWidget::pane {{
        border: 1px solid {t.BORDER_SUBTLE};
        background: {t.BG_GRAPHITE};
        border-radius: {t.RADIUS_MD}px;
    }}
    QTabBar::tab {{
        background: {t.BG_NAVY};
        color: {t.TEXT_SECONDARY};
        padding: 10px 20px;
        border: 1px solid {t.BORDER_SUBTLE};
        border-bottom: none;
        border-top-left-radius: {t.RADIUS_SM}px;
        border-top-right-radius: {t.RADIUS_SM}px;
        margin-right: 2px;
    }}
    QTabBar::tab:selected {{
        background: {t.BG_GRAPHITE};
        color: {t.ACCENT_CYAN};
        border-color: {t.ACCENT_CYAN};
    }}
    QTabBar::tab:hover {{
        color: {t.TEXT_PRIMARY};
    }}
    /* List widget */
    QListWidget {{
        background: {t.BG_OBSIDIAN};
        border: 1px solid {t.BORDER_SUBTLE};
        border-radius: {t.RADIUS_SM}px;
        color: {t.TEXT_PRIMARY};
    }}
    QListWidget::item {{
        padding: 8px;
        border-radius: {t.RADIUS_SM}px;
        margin: 2px 4px;
    }}
    QListWidget::item:selected {{
        background: {t.BG_GRAPHITE_LIGHT};
        color: {t.ACCENT_CYAN};
        border-left: 2px solid {t.ACCENT_CYAN};
    }}
    QListWidget::item:hover {{
        background: {t.BG_GRAPHITE};
    }}
    /* Table widget */
    QTableWidget {{
        background: {t.BG_OBSIDIAN};
        border: 1px solid {t.BORDER_SUBTLE};
        border-radius: {t.RADIUS_SM}px;
        color: {t.TEXT_PRIMARY};
        gridline-color: {t.BORDER_SUBTLE};
        selection-background-color: {t.BG_GRAPHITE_LIGHT};
    }}
    QTableWidget::item {{
        padding: 6px 10px;
    }}
    QTableWidget::item:selected {{
        background: {t.BG_GRAPHITE_LIGHT};
        color: {t.ACCENT_CYAN};
    }}
    QHeaderView::section {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {t.BG_GRAPHITE_LIGHT}, stop:1 {t.BG_SURFACE});
        color: {t.ACCENT_CYAN};
        padding: 8px;
        border: none;
        border-bottom: 2px solid {t.BORDER_ACCENT};
        font-weight: 700;
        font-size: {t.FONT_SIZE_SMALL}px;
    }}
    /* Group box */
    QGroupBox {{
        border: 1px solid {t.BORDER_SUBTLE};
        border-radius: {t.RADIUS_MD}px;
        margin-top: 14px;
        padding-top: 16px;
        font-weight: 600;
        color: {t.ACCENT_CYAN};
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 12px;
        padding: 0 8px;
    }}
    /* Check box / radio */
    QCheckBox, QRadioButton {{
        color: {t.TEXT_PRIMARY};
        spacing: 10px;
    }}
    QCheckBox::indicator, QRadioButton::indicator {{
        width: 18px;
        height: 18px;
        border: 1.5px solid {t.BORDER_MEDIUM};
        border-radius: 4px;
        background: {t.BG_OBSIDIAN};
    }}
    QCheckBox::indicator:checked {{
        background: {t.GRADIENT_CYAN};
        border-color: {t.ACCENT_CYAN};
    }}
    QRadioButton::indicator:checked {{
        background: {t.ACCENT_CYAN};
        border-color: {t.ACCENT_CYAN};
    }}
    /* Progress bar */
    QProgressBar {{
        background: {t.BG_OBSIDIAN};
        border: 1px solid {t.BORDER_SUBTLE};
        border-radius: {t.RADIUS_SM}px;
        text-align: center;
        color: {t.TEXT_PRIMARY};
        font-size: {t.FONT_SIZE_SMALL}px;
    }}
    QProgressBar::chunk {{
        background: {t.GRADIENT_CYAN};
        border-radius: {t.RADIUS_SM}px;
    }}
    /* Tool tips */
    QToolTip {{
        background: {t.BG_GRAPHITE_LIGHT};
        color: {t.TEXT_PRIMARY};
        border: 1px solid {t.ACCENT_CYAN};
        padding: 6px 10px;
        border-radius: {t.RADIUS_SM}px;
    }}
    /* Splitter handle */
    QSplitter::handle {{
        background: {t.BORDER_SUBTLE};
    }}
    QSplitter::handle:horizontal {{
        width: 3px;
    }}
    QSplitter::handle:vertical {{
        height: 3px;
    }}
    QSplitter::handle:hover {{
        background: {t.ACCENT_CYAN};
    }}
    """
    app.setStyleSheet(stylesheet)
