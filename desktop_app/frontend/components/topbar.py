"""VISIONFORGE X - Enhanced Top status bar component."""
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton, QFrame, QComboBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from frontend.components.widgets import StatusBadge
from frontend.design_system.tokens import DesignTokens as T


class TopBar(QFrame):
    """Enhanced top status bar with device status, mode selector, and controls."""

    connect_clicked = Signal()
    disconnect_clicked = Signal()
    start_clicked = Signal()
    stop_clicked = Signal()
    mode_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("topbar")
        self.setFixedHeight(T.TOPBAR_HEIGHT)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(T.SPACING_LG, 0, T.SPACING_LG, 0)
        layout.setSpacing(T.SPACING_MD)

        # Connection status
        self._status_badge = StatusBadge("Disconnected", "error")
        layout.addWidget(self._status_badge)

        # Mode indicator with glow
        self._mode_label = QLabel("SIMULATION MODE")
        self._mode_label.setStyleSheet(
            f"color: {T.ACCENT_CYAN}; font-size: {T.FONT_SIZE_SMALL}px; "
            f"font-weight: 700; padding: 3px 10px; "
            f"background: #003D44; border-radius: {T.RADIUS_SM}px; "
            f"border: 1px solid {T.ACCENT_CYAN}44;"
        )
        layout.addWidget(self._mode_label)

        layout.addSpacing(16)

        # Device info
        self._device_label = QLabel("No device")
        self._device_label.setObjectName("metricLabel")
        layout.addWidget(self._device_label)

        layout.addStretch()

        # Connection controls
        self._connect_btn = QPushButton("Connect")
        self._connect_btn.setObjectName("successBtn")
        self._connect_btn.setCursor(Qt.PointingHandCursor)
        self._connect_btn.clicked.connect(self.connect_clicked)
        layout.addWidget(self._connect_btn)

        self._disconnect_btn = QPushButton("Disconnect")
        self._disconnect_btn.setObjectName("dangerBtn")
        self._disconnect_btn.setCursor(Qt.PointingHandCursor)
        self._disconnect_btn.setEnabled(False)
        self._disconnect_btn.clicked.connect(self.disconnect_clicked)
        layout.addWidget(self._disconnect_btn)

        layout.addSpacing(8)

        # Processing controls
        self._start_btn = QPushButton("▶ Start")
        self._start_btn.setObjectName("primaryBtn")
        self._start_btn.setCursor(Qt.PointingHandCursor)
        self._start_btn.setEnabled(False)
        self._start_btn.clicked.connect(self.start_clicked)
        layout.addWidget(self._start_btn)

        self._stop_btn = QPushButton("⏹ Stop")
        self._stop_btn.setObjectName("dangerBtn")
        self._stop_btn.setCursor(Qt.PointingHandCursor)
        self._stop_btn.setEnabled(False)
        self._stop_btn.clicked.connect(self.stop_clicked)
        layout.addWidget(self._stop_btn)

        layout.addSpacing(8)

        # Mode selector
        mode_lbl = QLabel("Mode:")
        mode_lbl.setObjectName("metricLabel")
        layout.addWidget(mode_lbl)
        self._mode_combo = QComboBox()
        self._mode_combo.addItems(["Quality", "Balanced", "Performance"])
        self._mode_combo.setCurrentText("Balanced")
        self._mode_combo.setMaximumWidth(110)
        self._mode_combo.setCursor(Qt.PointingHandCursor)
        self._mode_combo.currentTextChanged.connect(
            lambda t: self.mode_changed.emit(t.lower())
        )
        layout.addWidget(self._mode_combo)

    def set_connected(self, connected: bool, device_name: str = ""):
        if connected:
            self._status_badge.set_status("good")
            self._status_badge.setText("Connected")
            self._connect_btn.setEnabled(False)
            self._disconnect_btn.setEnabled(True)
            self._start_btn.setEnabled(True)
            self._device_label.setText(device_name)
        else:
            self._status_badge.set_status("error")
            self._status_badge.setText("Disconnected")
            self._connect_btn.setEnabled(True)
            self._disconnect_btn.setEnabled(False)
            self._start_btn.setEnabled(False)
            self._stop_btn.setEnabled(False)
            self._device_label.setText("No device")

    def set_processing(self, active: bool):
        self._start_btn.setEnabled(not active)
        self._stop_btn.setEnabled(active)

    def set_simulated(self, simulated: bool):
        if simulated:
            self._mode_label.setText("SIMULATION MODE")
            self._mode_label.setStyleSheet(
                f"color: {T.ACCENT_CYAN}; font-size: {T.FONT_SIZE_SMALL}px; "
                f"font-weight: 700; padding: 3px 10px; "
                f"background: #003D44; border-radius: {T.RADIUS_SM}px; "
                f"border: 1px solid {T.ACCENT_CYAN}44;"
            )
        else:
            self._mode_label.setText("HARDWARE MODE")
            self._mode_label.setStyleSheet(
                f"color: {T.ACCENT_VIOLET}; font-size: {T.FONT_SIZE_SMALL}px; "
                f"font-weight: 700; padding: 3px 10px; "
                f"background: #2A1A66; border-radius: {T.RADIUS_SM}px; "
                f"border: 1px solid {T.ACCENT_VIOLET}44;"
            )
