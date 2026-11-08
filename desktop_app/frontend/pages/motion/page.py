"""VISIONFORGE X - Motion Intelligence Page (Enhanced)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFrame, QLabel,
    QPushButton, QScrollArea, QGroupBox, QComboBox, QSlider, QCheckBox,
    QTableWidget, QTableWidgetItem, QSpinBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QFont
import numpy as np
import cv2

from frontend.components.widgets import Panel, MetricTile, StatusBadge, CameraView
from frontend.design_system.tokens import DesignTokens as T
from backend.vision.motion import MotionAnalyzer, MotionZone, MotionDetector


class MotionIntelligencePage(QWidget):
    """Motion detection, tracking, and analysis - Enhanced."""

    def __init__(self, main_window):
        super().__init__()
        self._main = main_window
        self._analyzer = MotionAnalyzer()
        self._current_frame = None
        self._current_analysis = None
        self._frame_count = 0
        self._entry_count = 0
        self._exit_count = 0

        self._setup_ui()
        self._generate_test_frame()
        self._run_analysis()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(T.SPACING_LG, T.SPACING_LG, T.SPACING_LG, T.SPACING_LG)
        layout.setSpacing(T.SPACING_MD)

        # Title
        title = QLabel("🏃 Motion Intelligence")
        title.setStyleSheet(
            f"color: {T.ACCENT_CYAN}; font-size: {T.FONT_SIZE_HERO}px; "
            f"font-weight: 800; letter-spacing: 1px;"
        )
        layout.addWidget(title)

        # Controls
        ctrl_row = QHBoxLayout()

        method_lbl = QLabel("Method:")
        method_lbl.setObjectName("metricLabel")
        ctrl_row.addWidget(method_lbl)
        self._method_combo = QComboBox()
        self._method_combo.addItems(["frame_diff", "background_sub"])
        self._method_combo.currentTextChanged.connect(self._on_method_change)
        ctrl_row.addWidget(self._method_combo)

        ctrl_row.addSpacing(16)

        thresh_lbl = QLabel("Threshold:")
        thresh_lbl.setObjectName("metricLabel")
        ctrl_row.addWidget(thresh_lbl)
        self._thresh_slider = QSlider(Qt.Horizontal)
        self._thresh_slider.setRange(5, 100)
        self._thresh_slider.setValue(25)
        self._thresh_slider.valueChanged.connect(self._on_threshold_change)
        ctrl_row.addWidget(self._thresh_slider)
        self._thresh_label = QLabel("25")
        self._thresh_label.setObjectName("metricValue")
        self._thresh_label.setStyleSheet(f"color: {T.ACCENT_CYAN};")
        ctrl_row.addWidget(self._thresh_label)

        ctrl_row.addSpacing(16)

        self._heatmap_chk = QCheckBox("Show Heatmap")
        self._heatmap_chk.setChecked(True)
        ctrl_row.addWidget(self._heatmap_chk)

        self._tracks_chk = QCheckBox("Show Tracks")
        self._tracks_chk.setChecked(True)
        ctrl_row.addWidget(self._tracks_chk)

        ctrl_row.addStretch()

        run_btn = QPushButton("▶ Analyze Frame")
        run_btn.setObjectName("primaryBtn")
        run_btn.clicked.connect(self._run_analysis)
        ctrl_row.addWidget(run_btn)

        reset_btn = QPushButton("↺ Reset Tracker")
        reset_btn.clicked.connect(self._reset_tracker)
        ctrl_row.addWidget(reset_btn)

        layout.addLayout(ctrl_row)

        # Main content
        splitter_layout = QHBoxLayout()

        # Left: Video views
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(T.SPACING_MD)

        self._orig_view = CameraView("Original")
        self._motion_view = CameraView("Motion Analysis")
        grid = QGridLayout()
        grid.addWidget(self._orig_view, 0, 0)
        grid.addWidget(self._motion_view, 0, 1)
        left_layout.addLayout(grid, 1)

        # Motion mask view
        self._mask_view = CameraView("Motion Mask")
        left_layout.addWidget(self._mask_view)

        splitter_layout.addWidget(left, 2)

        # Right: Stats and controls
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(T.SPACING_MD)

        # Metrics
        metrics_panel = Panel("Motion Statistics")
        m_grid = QGridLayout()
        self._intensity_tile = MetricTile("Motion Intensity", "—", "", "info")
        self._objects_tile = MetricTile("Active Objects", "0", "", "info")
        self._count_tile = MetricTile("Object Count", "0", "", "info")
        self._time_tile = MetricTile("Proc. Time", "—", "ms", "info")

        m_grid.addWidget(self._intensity_tile, 0, 0)
        m_grid.addWidget(self._objects_tile, 0, 1)
        m_grid.addWidget(self._count_tile, 1, 0)
        m_grid.addWidget(self._time_tile, 1, 1)
        metrics_panel.addLayout(m_grid)
        right_layout.addWidget(metrics_panel)

        # Zones
        zone_panel = Panel("Motion Zones")
        zone_layout = zone_panel._layout
        self._zone_table = QTableWidget(0, 3)
        self._zone_table.setHorizontalHeaderLabels(["Zone", "Objects", "Status"])
        zone_layout.addWidget(self._zone_table)
        right_layout.addWidget(zone_panel)

        # Object table
        obj_panel = Panel("Tracked Objects")
        obj_layout = obj_panel._layout
        self._obj_table = QTableWidget(0, 4)
        self._obj_table.setHorizontalHeaderLabels(["ID", "Position", "Age", "Trajectory"])
        obj_layout.addWidget(self._obj_table)
        right_layout.addWidget(obj_panel, 1)

        splitter_layout.addWidget(right, 1)

        layout.addLayout(splitter_layout, 1)

    def _generate_test_frame(self):
        """Generate a test frame with moving objects."""
        self._frame_count += 1
        t = self._frame_count * 0.05
        img = np.zeros((480, 640, 3), dtype=np.uint8)

        # Background gradient
        for c in range(3):
            img[:, :, c] = np.tile(np.linspace(30 + c * 40, 100 + c * 20, 640), (480, 1))

        # Moving circles (simulating objects)
        for i, (speed, y_base, color) in enumerate([
            (1.5, 150, (0, 255, 255)),
            (2.0, 250, (255, 0, 255)),
            (1.0, 350, (0, 200, 255)),
        ]):
            x = int(100 + 450 * (0.5 + 0.5 * np.sin(t * speed + i)))
            cv2.circle(img, (x, y_base), 25, color, -1)

        self._current_frame = img

    def _run_analysis(self):
        """Run motion analysis on current frame."""
        if self._current_frame is None:
            self._generate_test_frame()

        self._analyzer.detector.set_threshold(self._thresh_slider.value())
        self._analyzer.set_method(self._method_combo.currentText())

        analysis = self._analyzer.analyze(self._current_frame)
        self._current_analysis = analysis

        # Display original
        self._display_image(self._orig_view, self._current_frame)

        # Display analysis overlay
        if self._heatmap_chk.isChecked():
            displayed = self._analyzer.draw_analysis(self._current_frame, analysis)
        else:
            displayed = self._current_frame.copy()
            for obj in analysis.get('tracked_objects', []):
                x, y, w, h = obj['bbox']
                cv2.rectangle(displayed, (x, y), (x + w, y + h), (0, 255, 255), 2)
        self._display_image(self._motion_view, displayed)

        # Display motion mask
        mask = analysis.get('motion_mask')
        if mask is not None:
            mask_color = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
            self._display_image(self._mask_view, mask_color)

        # Update metrics
        self._intensity_tile.set_value(f"{analysis['motion_intensity']:.3f}")
        self._objects_tile.set_value(str(analysis['active_count']))
        self._count_tile.set_value(str(self._frame_count))
        self._time_tile.set_value(f"{analysis['processing_time_ms']:.1f}")

        # Update object table
        self._obj_table.setRowCount(0)
        for obj in analysis.get('tracked_objects', []):
            row = self._obj_table.rowCount()
            self._obj_table.insertRow(row)
            self._obj_table.setItem(row, 0, QTableWidgetItem(str(obj['id'])))
            self._obj_table.setItem(row, 1, QTableWidgetItem(
                f"({obj['centroid'][0]}, {obj['centroid'][1]})"))
            self._obj_table.setItem(row, 2, QTableWidgetItem(str(obj['age'])))
            self._obj_table.setItem(row, 3, QTableWidgetItem(f"{len(obj['history'])} pts"))

        # Update zone table
        self._zone_table.setRowCount(0)
        for zone in self._analyzer.zones:
            row = self._zone_table.rowCount()
            self._zone_table.insertRow(row)
            self._zone_table.setItem(row, 0, QTableWidgetItem(zone.name))
            self._zone_table.setItem(row, 1, QTableWidgetItem(str(zone.current_objects)))
            self._zone_table.setItem(row, 2, QTableWidgetItem(
                "Active" if zone.current_objects > 0 else "Idle"))

    def _display_image(self, view: CameraView, image: np.ndarray):
        """Display image in camera view."""
        h, w = image.shape[:2]
        if len(image.shape) == 2:
            qimg = QImage(image.data, w, h, w, QImage.Format_Grayscale8)
        else:
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            qimg = QImage(rgb.data, w, h, w * 3, QImage.Format_RGB888)
        view.set_image(qimg)

    def _on_method_change(self, method: str):
        self._analyzer.set_method(method)
        self._run_analysis()

    def _on_threshold_change(self, value: int):
        self._thresh_label.setText(str(value))
        self._analyzer.detector.set_threshold(value)

    def _reset_tracker(self):
        self._analyzer.reset()
        self._frame_count = 0
        self._run_analysis()

    def update_telemetry(self, data: dict):
        """Update telemetry."""
        pass
