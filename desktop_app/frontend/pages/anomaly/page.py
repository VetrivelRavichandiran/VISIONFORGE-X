"""VISIONFORGE X - Anomaly Laboratory Page (Enhanced)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QScrollArea, QGroupBox, QComboBox, QSlider,
    QTableWidget, QTableWidgetItem, QFileDialog, QSpinBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QFont
import numpy as np
import cv2

from frontend.components.widgets import Panel, MetricTile, StatusBadge, CameraView
from frontend.design_system.tokens import DesignTokens as T
from backend.ai.registry import AnomalyEngine


class AnomalyLabPage(QWidget):
    """Anomaly detection and analysis - Enhanced."""

    def __init__(self, main_window):
        super().__init__()
        self._main = main_window
        self._engine = AnomalyEngine()
        self._current_frame = None
        self._anomaly_map = None

        self._setup_ui()
        self._generate_test_images()
        self._run_analysis()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(T.SPACING_LG, T.SPACING_LG, T.SPACING_LG, T.SPACING_LG)
        layout.setSpacing(T.SPACING_MD)

        title = QLabel("⚠️ Anomaly Laboratory")
        title.setStyleSheet(
            f"color: {T.STATUS_AMBER}; font-size: {T.FONT_SIZE_HERO}px; "
            f"font-weight: 800; letter-spacing: 1px;"
        )
        layout.addWidget(title)

        # Controls
        ctrl = QHBoxLayout()
        ctrl.addWidget(QLabel("Threshold:"))
        self._thresh_slider = QSlider(Qt.Horizontal)
        self._thresh_slider.setRange(10, 90)
        self._thresh_slider.setValue(50)
        self._thresh_slider.valueChanged.connect(lambda v: self._thresh_lbl.setText(f"{v/100:.2f}"))
        ctrl.addWidget(self._thresh_slider)
        self._thresh_lbl = QLabel("0.50")
        self._thresh_lbl.setObjectName("metricValue")
        self._thresh_lbl.setStyleSheet(f"color: {T.STATUS_AMBER};")
        ctrl.addWidget(self._thresh_lbl)
        ctrl.addSpacing(16)
        run_btn = QPushButton("▶ Analyze")
        run_btn.setObjectName("primaryBtn")
        run_btn.clicked.connect(self._run_analysis)
        ctrl.addWidget(run_btn)
        load_btn = QPushButton("📂 Load Image")
        load_btn.clicked.connect(self._load_image)
        ctrl.addWidget(load_btn)
        ctrl.addStretch()
        layout.addLayout(ctrl)

        # Main content
        grid = QGridLayout()

        # Original
        self._orig_view = CameraView("Input Image")
        grid.addWidget(self._orig_view, 0, 0)

        # Anomaly map
        self._anomaly_view = CameraView("Anomaly Heatmap")
        grid.addWidget(self._anomaly_view, 0, 1)

        # Overlay
        self._overlay_view = CameraView("Overlay")
        grid.addWidget(self._overlay_view, 1, 0, 1, 2)

        layout.addLayout(grid, 1)

        # Results
        result_panel = Panel("Analysis Results")
        r_layout = QGridLayout()
        result_panel.addLayout(r_layout)
        self._score_tile = MetricTile("Anomaly Score", "—", "", "warn")
        self._status_tile = StatusBadge("—", "info")
        self._method_lbl = QLabel("Method: Heuristic (statistical)")
        self._method_lbl.setObjectName("metricLabel")

        r_layout.addWidget(self._score_tile, 0, 0)
        r_layout.addWidget(self._status_tile, 0, 1)
        r_layout.addWidget(self._method_lbl, 1, 0, 1, 2)
        layout.addWidget(result_panel)

        # History
        hist_panel = Panel("Analysis History")
        h_layout = hist_panel._layout
        self._hist_table = QTableWidget(0, 4)
        self._hist_table.setHorizontalHeaderLabels(["Timestamp", "Score", "Status", "Method"])
        h_layout.addWidget(self._hist_table)
        layout.addWidget(hist_panel, 1)

    def _generate_test_images(self):
        """Generate normal and anomalous test images."""
        self._normal_img = np.zeros((400, 600, 3), dtype=np.uint8)
        for c in range(3):
            self._normal_img[:, :, c] = np.tile(
                np.linspace(60 + c * 40, 140 + c * 30, 600), (400, 1)
            )
        cv2.rectangle(self._normal_img, (100, 100), (300, 300), (0, 200, 255), -1)
        cv2.circle(self._normal_img, (450, 200), 60, (255, 100, 255), -1)

        self._anomaly_img = self._normal_img.copy()
        # Add anomalous region
        cv2.rectangle(self._anomaly_img, (400, 280), (580, 380), (255, 0, 0), -1)
        cv2.putText(self._anomaly_img, "ANOMALY", (410, 340),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    def _run_analysis(self):
        """Run anomaly analysis."""
        self._engine.threshold = self._thresh_slider.value() / 100.0

        # Analyze both images
        for name, img in [("normal", self._normal_img), ("anomaly", self._anomaly_img)]:
            result = self._engine.infer(img)
            score = result.predictions[0]['anomaly_score'] if result.predictions else 0
            is_anom = result.predictions[0]['is_anomalous'] if result.predictions else False

            if name == "anomaly":
                self._current_frame = img
                self._score_tile.set_value(f"{score:.4f}")
                self._status_tile.setText("ANOMALOUS" if is_anom else "Normal")
                self._status_tile.set_status("error" if is_anom else "good")

                # Compute anomaly heatmap
                self._anomaly_map = self._compute_heatmap(img, score)
                self._display_image(self._anomaly_view, self._anomaly_map)

                # Overlay
                overlay = self._create_overlay(img, score, is_anom)
                self._display_image(self._overlay_view, overlay)

        # Display input
        self._display_image(self._orig_view, self._current_frame)

        # Record in history
        row = self._hist_table.rowCount()
        self._hist_table.insertRow(row)
        import time
        self._hist_table.setItem(row, 0, QTableWidgetItem(time.strftime("%H:%M:%S")))
        self._hist_table.setItem(row, 1, QTableWidgetItem(f"{score:.4f}"))
        self._hist_table.setItem(row, 2, QTableWidgetItem(
            "ANOMALOUS" if is_anom else "Normal"))
        self._hist_table.setItem(row, 3, QTableWidgetItem("Heuristic"))

    def _compute_heatmap(self, img: np.ndarray, score: float) -> np.ndarray:
        """Compute anomaly heatmap visualization."""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Simple gradient-based anomaly highlighting
        blur = cv2.GaussianBlur(gray, (15, 15), 0)
        diff = cv2.absdiff(gray, blur)
        _, mask = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
        mask = cv2.GaussianBlur(mask, (21, 21), 0)
        heatmap = cv2.applyColorMap(mask.astype(np.uint8), cv2.COLORMAP_JET)
        return cv2.addWeighted(img, 0.5, heatmap, 0.5, 0)

    def _create_overlay(self, img: np.ndarray, score: float, is_anom: bool) -> np.ndarray:
        """Create overlay with anomaly indication."""
        out = img.copy()
        color = (0, 0, 255) if is_anom else (0, 255, 0)
        label = "ANOMALY DETECTED" if is_anom else "NORMAL"
        cv2.rectangle(out, (10, 10), (out.shape[1] - 10, 50), color, 3)
        cv2.putText(out, f"{label} (score: {score:.3f})", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        return out

    def _display_image(self, view: CameraView, image: np.ndarray):
        h, w = image.shape[:2]
        if len(image.shape) == 2:
            qimg = QImage(image.data, w, h, w, QImage.Format_Grayscale8)
        else:
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            qimg = QImage(rgb.data, w, h, w * 3, QImage.Format_RGB888)
        view.set_image(qimg)

    def _load_image(self):
        """Load image for analysis."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if path:
            self._current_frame = cv2.imread(path)
            if self._current_frame is not None:
                self._display_image(self._orig_view, self._current_frame)
                self._run_analysis()

    def update_telemetry(self, data: dict):
        pass
