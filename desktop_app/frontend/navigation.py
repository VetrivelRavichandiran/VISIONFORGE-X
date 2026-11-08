"""VISIONFORGE X - Enhanced Navigation sidebar component."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QScrollArea
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont
from frontend.design_system.tokens import DesignTokens as T


class NavItem:
    """Navigation item definition."""
    def __init__(self, key: str, label: str, icon: str = ""):
        self.key = key
        self.label = label
        self.icon = icon


NAV_ITEMS = [
    NavItem("command_center", "Command Center", "⚡"),
    NavItem("vision_studio", "Vision Studio", "🔬"),
    NavItem("ai_lab", "AI Intelligence Lab", "🧠"),
    NavItem("motion", "Motion Intelligence", "🏃"),
    NavItem("anomaly", "Anomaly Laboratory", "⚠️"),
    NavItem("pipeline", "Pipeline Architect", "🔗"),
    NavItem("fpga_monitor", "FPGA Monitor", "🔧"),
    NavItem("performance", "Performance Lab", "📊"),
    NavItem("datasets", "Dataset Explorer", "📁"),
    NavItem("events", "Event Intelligence", "📋"),
    NavItem("reports", "Research Reports", "📄"),
    NavItem("settings", "System Config", "⚙️"),
]


class NavigationRail(QFrame):
    """Enhanced persistent left navigation rail with glow effects."""

    page_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(T.SIDEBAR_WIDTH)
        self.setMinimumWidth(180)
        self._buttons = {}
        self._current = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Logo area with gradient
        logo = QFrame()
        logo.setFixedHeight(64)
        logo.setStyleSheet(
            f"background: qlineargradient(x1:0, y1:0, x2:1, y2:1, "
            f"stop:0 {T.BG_NAVY}, stop:1 {T.BG_GRAPHITE}); "
            f"border-bottom: 1px solid {T.BORDER_SUBTLE};"
        )
        logo_layout = QVBoxLayout(logo)
        logo_layout.setContentsMargins(T.SPACING_LG, T.SPACING_MD,
                                       T.SPACING_LG, T.SPACING_MD)

        # Logo title with glow
        title = QLabel("VISIONFORGE X")
        title.setStyleSheet(
            f"color: {T.ACCENT_CYAN}; font-size: {T.FONT_SIZE_MEDIUM+1}px; "
            f"font-weight: 800; letter-spacing: 1.5px; "
            f"qproperty-text: 'VISIONFORGE X';"
        )
        title.setFont(QFont(T.FONT_FAMILY, 14, QFont.Bold))
        logo_layout.addWidget(title)

        subtitle = QLabel("Edge Vision Intelligence")
        subtitle.setStyleSheet(
            f"color: {T.TEXT_MUTED}; font-size: {T.FONT_SIZE_TINY}px; "
            f"margin-top: 2px; letter-spacing: 0.5px;"
        )
        logo_layout.addWidget(subtitle)
        layout.addWidget(logo)

        # Separator
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: qlineargradient(x1:0, y1:0, x2:1, y2:0, "
                          f"stop:0 transparent, stop:0.5 {T.BORDER_SUBTLE}, stop:1 transparent);")
        layout.addWidget(sep)

        # Scroll area for nav items
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")

        nav_container = QWidget()
        nav_layout = QVBoxLayout(nav_container)
        nav_layout.setContentsMargins(6, 6, 6, 6)
        nav_layout.setSpacing(3)

        for item in NAV_ITEMS:
            btn = QPushButton(f"  {item.icon}  {item.label}")
            btn.setObjectName("navBtn")
            btn.setCheckable(True)
            btn.setMinimumHeight(42)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setToolTip(item.label)
            btn.clicked.connect(lambda checked, k=item.key: self._select(k))
            nav_layout.addWidget(btn)
            self._buttons[item.key] = btn

        nav_layout.addStretch()
        scroll.setWidget(nav_container)
        layout.addWidget(scroll, 1)

    def _select(self, key: str):
        if self._current and self._current in self._buttons:
            self._buttons[self._current].setChecked(False)
        if key in self._buttons:
            self._buttons[key].setChecked(True)
            self._current = key
            self.page_changed.emit(key)

    def set_current(self, key: str):
        self._select(key)

    def get_current(self) -> str:
        return self._current
