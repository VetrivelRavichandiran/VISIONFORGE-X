"""VISIONFORGE X - Enhanced Reusable UI Components."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGraphicsDropShadowEffect, QSizePolicy, QProgressBar
)
from PySide6.QtGui import QColor, QPainter, QPen, QBrush, QFont
from PySide6.QtCore import Qt, Signal, QSize
from frontend.design_system.tokens import DesignTokens as T


class Panel(QFrame):
    """Enhanced panel component with subtle border, rounded corners, and glow."""

    def __init__(self, title: str = "", parent=None, light: bool = False):
        super().__init__(parent)
        self.setObjectName("panel_light" if light else "panel")
        self.setFrameShape(QFrame.StyledPanel)

        # Add subtle shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(T.SHADOW_COLOR))
        self.setGraphicsEffect(shadow)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(T.SPACING_LG, T.SPACING_LG,
                                        T.SPACING_LG, T.SPACING_LG)
        self._layout.setSpacing(T.SPACING_MD)

        if title:
            self._title_label = QLabel(title)
            self._title_label.setObjectName("panelTitle")
            self._layout.addWidget(self._title_label)

    def addWidget(self, widget):
        self._layout.addWidget(widget)

    def addLayout(self, layout):
        self._layout.addLayout(layout)


class MetricTile(Panel):
    """Enhanced compact metric display tile with status glow."""

    def __init__(self, label: str, value: str = "—", unit: str = "",
                 status: str = "info", parent=None):
        super().__init__("", parent)
        self._layout.setContentsMargins(T.SPACING_MD, T.SPACING_MD,
                                        T.SPACING_MD, T.SPACING_MD)
        self._layout.setSpacing(T.SPACING_XS)

        self._label = QLabel(label)
        self._label.setObjectName("metricLabel")
        self._label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._layout.addWidget(self._label)

        h = QHBoxLayout()
        self._value = QLabel(value)
        self._value.setObjectName("metricValue")
        self._value.setStyleSheet(f"color: {T.ACCENT_CYAN};")
        h.addWidget(self._value)
        if unit:
            self._unit = QLabel(unit)
            self._unit.setObjectName("metricLabel")
            h.addWidget(self._unit)
        h.addStretch()
        self._layout.addLayout(h)

        # Status glow border
        self._status = status
        self._apply_status()

    def _apply_status(self):
        colors = {
            "good": (T.STATUS_GREEN, T.STATUS_GREEN_GLOW),
            "warn": (T.STATUS_AMBER, T.STATUS_AMBER_GLOW),
            "error": (T.STATUS_RED, T.STATUS_RED_GLOW),
            "info": (T.ACCENT_CYAN, T.ACCENT_CYAN_GLOW),
            "ai": (T.ACCENT_VIOLET, T.ACCENT_VIOLET_GLOW),
        }
        fg, glow = colors.get(self._status, (T.ACCENT_CYAN, T.ACCENT_CYAN_GLOW))
        self._value.setStyleSheet(f"color: {fg};")
        self.setStyleSheet(
            f"background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {T.BG_GRAPHITE}, stop:1 {T.BG_SURFACE});"
            f"border: 1px solid {fg}33; border-radius: {T.RADIUS_MD}px;"
        )

    def set_value(self, value, unit: str = ""):
        self._value.setText(str(value))
        if unit:
            # Rebuild to include unit
            for i in reversed(range(self._value.parent().layout().count())):
                w = self._value.parent().layout().itemAt(i).widget()
                if w and w is not self._value:
                    w.deleteLater()
            u = QLabel(unit)
            u.setObjectName("metricLabel")
            self._value.parent().layout().addWidget(u)

    def set_status(self, status: str):
        self._status = status
        self._apply_status()


class StatusBadge(QLabel):
    """Enhanced colored status indicator badge with glow."""

    def __init__(self, text: str, status: str = "info", parent=None):
        super().__init__(text, parent)
        self.set_status(status)

    def set_status(self, status: str):
        colors = {
            "good": (T.STATUS_GREEN, "#003D1F"),
            "warn": (T.STATUS_AMBER, "#4D3600"),
            "error": (T.STATUS_RED, "#4D0814"),
            "info": (T.ACCENT_CYAN, "#003D44"),
            "ai": (T.ACCENT_VIOLET, "#2A1A66"),
        }
        fg, bg = colors.get(status, (T.TEXT_SECONDARY, T.BG_GRAPHITE))
        self.setText(f"  {self.text().strip()}  ")
        self.setStyleSheet(
            f"color: {fg}; background: {bg}; "
            f"padding: 3px 10px; border-radius: {T.RADIUS_ROUND}px; "
            f"font-size: {T.FONT_SIZE_TINY}px; font-weight: 700; "
            f"border: 1px solid {fg}44;"
        )


class SectionHeader(QFrame):
    """Enhanced section header with title and optional action button."""

    clicked = Signal()

    def __init__(self, title: str, action_text: str = "", parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(T.SPACING_MD)

        self._title = QLabel(title)
        self._title.setObjectName("panelTitle")
        self._title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(self._title)

        if action_text:
            btn = QPushButton(action_text)
            btn.setMaximumHeight(28)
            btn.clicked.connect(self.clicked)
            layout.addWidget(btn)

        layout.addStretch()


class EventRow(QFrame):
    """Enhanced event row in the event list."""

    def __init__(self, event: dict, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self._event = event

        layout = QHBoxLayout(self)
        layout.setContentsMargins(T.SPACING_SM, T.SPACING_XS,
                                  T.SPACING_SM, T.SPACING_XS)
        layout.setSpacing(T.SPACING_SM)

        # Severity indicator with glow
        sev_colors = {
            "critical": T.STATUS_RED, "error": T.STATUS_RED,
            "warning": T.STATUS_AMBER, "info": T.ACCENT_CYAN,
            "debug": T.TEXT_MUTED,
        }
        color = sev_colors.get(event.get('severity', 'info'), T.ACCENT_CYAN)
        indicator = QFrame()
        indicator.setFixedSize(4, 30)
        indicator.setStyleSheet(f"background: {color}; border-radius: 2px;")
        layout.addWidget(indicator)

        # Timestamp
        ts = QLabel(event.get('timestamp', '')[:19])
        ts.setObjectName("metricLabel")
        ts.setMaximumWidth(180)
        layout.addWidget(ts)

        # Category
        cat = StatusBadge(event.get('category', ''), event.get('severity', 'info'))
        layout.addWidget(cat)

        # Description
        desc = QLabel(event.get('description', ''))
        desc.setObjectName("TEXT_PRIMARY")
        desc.setWordWrap(True)
        desc.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(desc)

        # Acknowledge button
        if not event.get('acknowledged', False):
            ack_btn = QPushButton("Ack")
            ack_btn.setMaximumHeight(24)
            ack_btn.setMaximumWidth(50)
            ack_btn.clicked.connect(lambda: self._on_ack(event))
            layout.addWidget(ack_btn)

    def _on_ack(self, event):
        event['acknowledged'] = True
        self.hide()


class CameraView(QFrame):
    """Enhanced camera preview panel with label overlay and scanline effect."""

    def __init__(self, label: str, parent=None):
        super().__init__(parent)
        self.setObjectName("panel")
        self._label_text = label
        self._image = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(T.SPACING_SM, T.SPACING_SM,
                                  T.SPACING_SM, T.SPACING_SM)

        # Label
        self._label = QLabel(label)
        self._label.setObjectName("panelTitle")
        self._label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._label)

        # Image area
        self._image_area = QFrame()
        self._image_area.setObjectName("panel")
        self._image_area.setFrameShape(QFrame.StyledPanel)
        self._image_layout = QVBoxLayout(self._image_area)
        self._image_layout.setContentsMargins(0, 0, 0, 0)

        self._placeholder = QLabel("No Signal")
        self._placeholder.setAlignment(Qt.AlignCenter)
        self._placeholder.setObjectName("metricLabel")
        self._placeholder.setStyleSheet(
            f"color: {T.STATUS_AMBER}; font-size: {T.FONT_SIZE_MEDIUM}px; "
            f"font-weight: 600;"
        )
        self._image_layout.addWidget(self._placeholder)

        layout.addWidget(self._image_area, 1)

    def set_image(self, qimage):
        """Set a QImage to display."""
        self._image = qimage
        # Remove placeholder
        for i in reversed(range(self._image_layout.count())):
            w = self._image_layout.itemAt(i).widget()
            if w:
                w.deleteLater()
        from PySide6.QtWidgets import QLabel
        from PySide6.QtGui import QPixmap
        scaled = qimage.scaled(self._image_area.size(), Qt.KeepAspectRatio,
                               Qt.SmoothTransformation)
        img_label = QLabel()
        img_label.setPixmap(QPixmap.fromImage(scaled))
        img_label.setAlignment(Qt.AlignCenter)
        self._image_layout.addWidget(img_label)

    def set_placeholder(self, text: str, color: str = None):
        """Show placeholder text."""
        for i in reversed(range(self._image_layout.count())):
            w = self._image_layout.itemAt(i).widget()
            if w:
                w.deleteLater()
        self._placeholder.setText(text)
        if color:
            self._placeholder.setStyleSheet(
                f"color: {color}; font-size: {T.FONT_SIZE_MEDIUM}px; "
                f"font-weight: 600;"
            )
        self._image_layout.addWidget(self._placeholder)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._image:
            self.set_image(self._image)


class GlowProgressBar(QProgressBar):
    """Enhanced progress bar with gradient fill and glow effect."""

    def __init__(self, parent=None, color: str = T.ACCENT_CYAN):
        super().__init__(parent)
        self._color = color
        self._set_glow_style()

    def _set_glow_style(self):
        self.setStyleSheet(
            f"QProgressBar {{ background: {T.BG_OBSIDIAN}; "
            f"border: 1px solid {T.BORDER_SUBTLE}; "
            f"border-radius: {T.RADIUS_SM}px; "
            f"height: 10px; color: {T.TEXT_PRIMARY}; font-size: {T.FONT_SIZE_TINY}px; }}"
            f"QProgressBar::chunk {{ background: qlineargradient(x1:0, y1:0, x2:1, y2:0, "
            f"stop:0 {self._color}88, stop:1 {self._color}); "
            f"border-radius: {T.RADIUS_SM}px; }}"
        )

    def set_color(self, color: str):
        self._color = color
        self._set_glow_style()


class InfoCard(QFrame):
    """Enhanced info card with icon, title, and content."""

    def __init__(self, title: str, content: str = "", icon: str = "📊", parent=None):
        super().__init__(parent)
        self.setObjectName("panel")
        self.setFrameShape(QFrame.StyledPanel)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(T.SPACING_LG, T.SPACING_LG,
                                  T.SPACING_LG, T.SPACING_LG)
        layout.setSpacing(T.SPACING_MD)

        # Header
        header = QHBoxLayout()
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"font-size: {T.FONT_SIZE_LARGE}px;")
        header.addWidget(icon_lbl)
        title_lbl = QLabel(title)
        title_lbl.setObjectName("panelTitle")
        header.addWidget(title_lbl)
        header.addStretch()
        layout.addLayout(header)

        # Content
        if content:
            content_lbl = QLabel(content)
            content_lbl.setWordWrap(True)
            content_lbl.setObjectName("metricLabel")
            layout.addWidget(content_lbl)

    def set_content(self, content: str):
        # Remove existing content label if any
        for i in reversed(range(self._layout.count())):
            w = self._layout.itemAt(i).widget()
            if w and w.objectName() == "metricLabel":
                w.deleteLater()
        content_lbl = QLabel(content)
        content_lbl.setWordWrap(True)
        content_lbl.setObjectName("metricLabel")
        self._layout.addWidget(content_lbl)


class StatRow(QFrame):
    """Enhanced stat row with label and value."""

    def __init__(self, label: str, value: str = "—", status: str = "info", parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(T.SPACING_MD)

        lbl = QLabel(label)
        lbl.setObjectName("metricLabel")
        lbl.setMinimumWidth(120)
        layout.addWidget(lbl)

        badge = StatusBadge(value, status)
        layout.addWidget(badge)
        layout.addStretch()
