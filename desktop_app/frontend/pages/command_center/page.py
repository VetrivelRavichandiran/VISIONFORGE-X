"""VISIONFORGE X - Command Center Page (Enhanced)."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFrame, QLabel,
    QPushButton, QSplitter, QScrollArea, QComboBox, QCheckBox, QGroupBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap, QFont
import numpy as np

from frontend.components.widgets import Panel, MetricTile, StatusBadge, CameraView
from frontend.design_system.tokens import DesignTokens as T


class CommandCenterPage(QWidget):
    """Central live monitoring and control page - Enhanced."""

    def __init__(self, main_window):
        super().__init__()
        self._main = main_window
        self._original_frame = None
        self._processed_frame = None
        self._fps_history = []
        self._latency_history = []

        self._setup_ui()
        self._setup_timer()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(T.SPACING_LG, T.SPACING_LG,
                                  T.SPACING_LG, T.SPACING_LG)
        layout.setSpacing(T.SPACING_MD)

        # Title row with enhanced styling
        title_row = QHBoxLayout()
        title = QLabel("⚡ Command Center")
        title.setStyleSheet(
            f"color: {T.ACCENT_CYAN}; font-size: {T.FONT_SIZE_HERO}px; "
            f"font-weight: 800; letter-spacing: 1px;"
        )
        title_row.addWidget(title)
        title_row.addStretch()

        # Overlay controls
        self._overlay_chk = QCheckBox("Show Overlays")
        self._overlay_chk.setChecked(True)
        title_row.addWidget(self._overlay_chk)

        # Resolution selector
        res_lbl = QLabel("Resolution:")
        res_lbl.setObjectName("metricLabel")
        title_row.addWidget(res_lbl)
        self._res_combo = QComboBox()
        self._res_combo.addItems(["320x240", "640x480", "800x600", "1280x720"])
        self._res_combo.setCurrentText("640x480")
        self._res_combo.setMaximumWidth(110)
        title_row.addWidget(self._res_combo)

        layout.addLayout(title_row)

        # Main content splitter
        splitter = QSplitter(Qt.Horizontal)

        # Left: Camera views
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(T.SPACING_MD)

        # Camera comparison with enhanced styling
        cam_grid = QGridLayout()
        self._original_view = CameraView("Original")
        self._original_view.set_placeholder("No Signal", T.STATUS_AMBER)
        self._processed_view = CameraView("Processed")
        self._processed_view.set_placeholder("No Signal", T.STATUS_AMBER)

        cam_grid.addWidget(self._original_view, 0, 0)
        cam_grid.addWidget(self._processed_view, 0, 1)
        left_layout.addLayout(cam_grid, 1)

        # Camera status row
        cam_status = QHBoxLayout()
        self._cam_status_badge = StatusBadge("Camera: Stopped", "error")
        cam_status.addWidget(self._cam_status_badge)
        cam_status.addStretch()
        left_layout.addLayout(cam_status)

        splitter.addWidget(left_panel)

        # Right: Metrics and events
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(T.SPACING_MD)

        # System metrics with enhanced tiles
        metrics_panel = Panel("System Telemetry")
        metrics_grid = QGridLayout()
        metrics_panel.addLayout(metrics_grid)

        self._fps_tile = MetricTile("FPS", "—", "fps", "info")
        self._latency_tile = MetricTile("Latency", "—", "ms", "info")
        self._throughput_tile = MetricTile("Throughput", "—", "MB/s", "info")
        self._motion_tile = MetricTile("Motion", "—", "", "info")
        self._anomaly_tile = MetricTile("Anomaly", "—", "", "warn")
        self._cpu_tile = MetricTile("CPU", "—", "%", "info")
        self._mem_tile = MetricTile("Memory", "—", "%", "info")
        self._ai_tile = MetricTile("AI Inference", "—", "ms", "ai")

        metrics_grid.addWidget(self._fps_tile, 0, 0)
        metrics_grid.addWidget(self._latency_tile, 0, 1)
        metrics_grid.addWidget(self._throughput_tile, 0, 2)
        metrics_grid.addWidget(self._motion_tile, 1, 0)
        metrics_grid.addWidget(self._anomaly_tile, 1, 1)
        metrics_grid.addWidget(self._cpu_tile, 2, 0)
        metrics_grid.addWidget(self._mem_tile, 2, 1)
        metrics_grid.addWidget(self._ai_tile, 3, 0, 1, 2)
        right_layout.addWidget(metrics_panel)

        # Device info
        dev_panel = Panel("Device Status")
        dev_layout = dev_panel._layout

        self._mode_badge = StatusBadge("Simulation", "info")
        dev_layout.addWidget(self._mode_badge)

        self._pipeline_label = QLabel("Active Pipeline: None")
        self._pipeline_label.setObjectName("metricLabel")
        dev_layout.addWidget(self._pipeline_label)

        self._hw_status = StatusBadge("Hardware: N/A", "info")
        dev_layout.addWidget(self._hw_status)

        right_layout.addWidget(dev_panel)

        # Event feed
        event_panel = Panel("Event Feed")
        event_layout = event_panel._layout
        self._event_list = QGroupBox("Recent Events")
        event_scroll = QScrollArea()
        event_scroll.setWidgetResizable(True)
        event_scroll.setFrameShape(QFrame.NoFrame)
        self._event_container = QWidget()
        self._event_layout = QVBoxLayout(self._event_container)
        self._event_layout.setContentsMargins(4, 4, 4, 4)
        self._event_layout.setSpacing(2)
        self._event_layout.addStretch()
        event_scroll.setWidget(self._event_container)
        self._event_list.setLayout(QVBoxLayout())
        self._event_list.layout().addWidget(event_scroll)
        event_layout.addWidget(self._event_list)
        right_layout.addWidget(event_panel, 1)

        splitter.addWidget(right_panel)
        splitter.setSizes([700, 500])

        layout.addWidget(splitter, 1)

    def _setup_timer(self):
        """Setup periodic UI refresh timer."""
        self._timer = QTimer()
        self._timer.timeout.connect(self._refresh)
        self._timer.start(500)

    def _refresh(self):
        """Refresh UI elements."""
        # Update FPS display if we have history
        if self._fps_history:
            avg_fps = np.mean(self._fps_history[-10:])
            self._fps_tile.set_value(f"{avg_fps:.1f}")
            status = "good" if avg_fps > 20 else "warn" if avg_fps > 10 else "error"
            self._fps_tile.set_status(status)

        if self._latency_history:
            avg_lat = np.mean(self._latency_history[-10:])
            self._latency_tile.set_value(f"{avg_lat:.1f}")
            status = "good" if avg_lat < 20 else "warn" if avg_lat < 50 else "error"
            self._latency_tile.set_status(status)

    def update_frames(self, original, processed, proc_time):
        """Update camera views with new frames."""
        try:
            from PySide6.QtGui import QImage
            import cv2

            # Update original
            if original is not None:
                h, w = original.shape[:2]
                if len(original.shape) == 2:
                    qimg = QImage(original.data, w, h, w, QImage.Format_Grayscale8)
                else:
                    rgb = cv2.cvtColor(original, cv2.COLOR_BGR2RGB)
                    stride = w * 3
                    qimg = QImage(rgb.data, w, h, stride, QImage.Format_RGB888)
                self._original_view.set_image(qimg)

            # Update processed
            if processed is not None:
                h, w = processed.shape[:2]
                if len(processed.shape) == 2:
                    qimg = QImage(processed.data, w, h, w, QImage.Format_Grayscale8)
                else:
                    rgb = cv2.cvtColor(processed, cv2.COLOR_BGR2RGB)
                    stride = w * 3
                    qimg = QImage(rgb.data, w, h, stride, QImage.Format_RGB888)
                self._processed_view.set_image(qimg)

            self._fps_history.append(1000.0 / max(proc_time, 0.1))
            self._latency_history.append(proc_time)
            self._fps_history = self._fps_history[-60:]
            self._latency_history = self._latency_history[-60:]

        except Exception:
            pass

    def update_telemetry(self, data: dict):
        """Update telemetry displays."""
        try:
            fps = data.get('processing_fps', 0)
            latency = data.get('latency_ms', 0)
            motion = data.get('motion_intensity', 0)
            anomaly = data.get('anomaly_score', 0)
            cpu = data.get('cpu_usage', 0)
            mem = data.get('memory_usage', 0)
            ai = data.get('ai_inference_ms', 0)

            self._fps_tile.set_value(f"{fps:.1f}")
            self._latency_tile.set_value(f"{latency:.1f}")
            self._motion_tile.set_value(f"{motion:.2f}")
            self._anomaly_tile.set_value(f"{anomaly:.2f}")
            self._cpu_tile.set_value(f"{cpu:.0f}")
            self._mem_tile.set_value(f"{mem:.0f}")
            self._ai_tile.set_value(f"{ai:.1f}")

            # Throughput estimate
            res = self._res_combo.currentText()
            w, h = map(int, res.split('x'))
            bytes_per_frame = w * h * 3
            throughput = (fps * bytes_per_frame) / (1024 * 1024)
            self._throughput_tile.set_value(f"{throughput:.1f}")

        except Exception:
            pass
