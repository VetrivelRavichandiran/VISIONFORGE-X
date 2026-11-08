"""VISIONFORGE X - Vision Studio Page (Enhanced)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFrame, QLabel,
    QPushButton, QScrollArea, QGroupBox, QComboBox, QSlider, QCheckBox,
    QSplitter, QSpinBox, QDoubleSpinBox, QListWidget, QListWidgetItem, QTabWidget
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QImage, QPixmap, QFont
import numpy as np
import cv2

from frontend.components.widgets import Panel, MetricTile, CameraView, SectionHeader
from frontend.design_system.tokens import DesignTokens as T
from backend.vision.engine import VisionEngine, ExecutionSource, ExecutionSource as ES


# Algorithm definitions with parameters
ALGORITHMS = {
    'grayscale': {'name': 'Grayscale', 'params': [], 'category': 'color'},
    'gaussian_blur': {'name': 'Gaussian Blur', 'params': [
        ('kernel_size', 'Kernel Size', int, 5, 3, 21, 2),
        ('sigma', 'Sigma', float, 0, 0, 10, 0.5)
    ], 'category': 'blur'},
    'median_blur': {'name': 'Median Blur', 'params': [
        ('kernel_size', 'Kernel Size', int, 5, 3, 21, 2)
    ], 'category': 'blur'},
    'bilateral_filter': {'name': 'Bilateral Filter', 'params': [
        ('d', 'Diameter', int, 9, 1, 25, 2),
        ('sigma_color', 'Color Sigma', float, 75, 1, 200, 10),
        ('sigma_space', 'Space Sigma', float, 75, 1, 200, 10)
    ], 'category': 'blur'},
    'histogram_equalization': {'name': 'Histogram Equalization', 'params': [], 'category': 'enhance'},
    'clahe': {'name': 'CLAHE', 'params': [
        ('clip_limit', 'Clip Limit', float, 2.0, 1.0, 10.0, 0.5),
        ('tile_grid', 'Tile Grid', int, 8, 2, 32, 2)
    ], 'category': 'enhance'},
    'gamma_correction': {'name': 'Gamma Correction', 'params': [
        ('gamma', 'Gamma', float, 1.0, 0.1, 5.0, 0.1)
    ], 'category': 'enhance'},
    'sharpening': {'name': 'Sharpening', 'params': [
        ('strength', 'Strength', float, 1.0, 0.0, 5.0, 0.5)
    ], 'category': 'enhance'},
    'sobel': {'name': 'Sobel', 'params': [
        ('dx', 'DX', int, 1, 0, 1, 1),
        ('dy', 'DY', int, 0, 0, 1, 1),
        ('ksize', 'Kernel', int, 3, 1, 7, 2)
    ], 'category': 'edge'},
    'scharr': {'name': 'Scharr', 'params': [
        ('dx', 'DX', int, 1, 0, 1, 1),
        ('dy', 'DY', int, 0, 0, 1, 1)
    ], 'category': 'edge'},
    'canny': {'name': 'Canny Edge', 'params': [
        ('threshold1', 'Thresh1', int, 100, 1, 255, 10),
        ('threshold2', 'Thresh2', int, 200, 1, 255, 10)
    ], 'category': 'edge'},
    'binary_threshold': {'name': 'Binary Threshold', 'params': [
        ('threshold', 'Threshold', int, 127, 0, 255, 5),
        ('max_value', 'Max Value', int, 255, 0, 255, 5)
    ], 'category': 'threshold'},
    'adaptive_threshold': {'name': 'Adaptive Threshold', 'params': [
        ('block_size', 'Block Size', int, 11, 3, 51, 2),
        ('C', 'C', int, 2, 0, 20, 1)
    ], 'category': 'threshold'},
    'otsu_threshold': {'name': "Otsu's Threshold", 'params': [], 'category': 'threshold'},
    'morphology': {'name': 'Morphology', 'params': [
        ('operation', 'Operation', str, 'opening', ['erosion', 'dilation', 'opening', 'closing']),
        ('kernel_size', 'Kernel Size', int, 3, 1, 15, 2),
        ('iterations', 'Iterations', int, 1, 1, 10, 1)
    ], 'category': 'morphology'},
    'roi': {'name': 'ROI', 'params': [
        ('x', 'X', int, 0, 0, 1000, 10),
        ('y', 'Y', int, 0, 0, 1000, 10),
        ('width', 'Width', int, 320, 1, 2000, 10),
        ('height', 'Height', int, 240, 1, 2000, 10)
    ], 'category': 'geometry'},
}


class VisionStudioPage(QWidget):
    """Real image processing with adjustable parameters and pipeline - Enhanced."""

    def __init__(self, main_window):
        super().__init__()
        self._main = main_window
        self._engine = VisionEngine(ExecutionSource.SIMULATION)
        self._pipeline_stages = []  # List of (name, params, enabled)
        self._current_image = None
        self._processed_image = None

        self._setup_ui()
        self._load_default_pipeline()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(T.SPACING_LG, T.SPACING_LG, T.SPACING_LG, T.SPACING_LG)
        layout.setSpacing(T.SPACING_MD)

        # Title
        title = QLabel("🔬 Vision Studio")
        title.setStyleSheet(
            f"color: {T.ACCENT_CYAN}; font-size: {T.FONT_SIZE_HERO}px; "
            f"font-weight: 800; letter-spacing: 1px;"
        )
        layout.addWidget(title)

        # Main splitter
        splitter = QSplitter(Qt.Horizontal)

        # Left: Algorithm palette
        left = Panel("Available Algorithms")
        left_layout = left._layout

        # Category filter
        cat_row = QHBoxLayout()
        cat_lbl = QLabel("Category:")
        cat_lbl.setObjectName("metricLabel")
        cat_row.addWidget(cat_lbl)
        self._cat_combo = QComboBox()
        self._cat_combo.addItems(["all", "color", "blur", "enhance", "edge", "threshold", "morphology", "geometry"])
        self._cat_combo.currentTextChanged.connect(self._filter_algorithms)
        cat_row.addWidget(self._cat_combo)
        cat_row.addStretch()
        left_layout.addLayout(cat_row)

        self._algo_list = QListWidget()
        self._algo_list.itemDoubleClicked.connect(self._add_algorithm)
        self._algo_list.setMaximumWidth(220)
        left_layout.addWidget(self._algo_list)
        self._filter_algorithms("all")
        splitter.addWidget(left)

        # Center: Pipeline and preview
        center = QWidget()
        center_layout = QVBoxLayout(center)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(T.SPACING_MD)

        # Pipeline stages
        pipeline_panel = Panel("Processing Pipeline")
        pipe_layout = pipeline_panel._layout

        self._stage_list = QListWidget()
        self._stage_list.itemSelectionChanged.connect(self._on_stage_selected)
        pipe_layout.addWidget(self._stage_list)

        # Pipeline actions
        pipe_actions = QHBoxLayout()
        up_btn = QPushButton("↑ Up")
        down_btn = QPushButton("↓ Down")
        remove_btn = QPushButton("✕ Remove")
        reset_btn = QPushButton("↺ Reset")
        remove_btn.clicked.connect(self._remove_selected_stage)
        reset_btn.clicked.connect(self._reset_pipeline)
        pipe_actions.addWidget(up_btn)
        pipe_actions.addWidget(down_btn)
        pipe_actions.addWidget(remove_btn)
        pipe_actions.addWidget(reset_btn)
        pipe_actions.addStretch()
        pipe_layout.addLayout(pipe_actions)

        center_layout.addWidget(pipeline_panel)

        # Preview area
        preview_panel = Panel("Preview")
        preview_layout = QGridLayout()
        preview_panel.addLayout(preview_layout)
        self._orig_view = CameraView("Original")
        self._proc_view = CameraView("Processed")
        preview_layout.addWidget(self._orig_view, 0, 0)
        preview_layout.addWidget(self._proc_view, 0, 1)
        center_layout.addWidget(preview_panel, 1)

        splitter.addWidget(center)

        # Right: Parameters
        right = Panel("Parameters")
        right_layout = right._layout

        self._param_scroll = QScrollArea()
        self._param_scroll.setWidgetResizable(True)
        self._param_scroll.setFrameShape(QFrame.NoFrame)
        self._param_widget = QWidget()
        self._param_layout = QVBoxLayout(self._param_widget)
        self._param_layout.setContentsMargins(0, 0, 0, 0)
        self._param_layout.setSpacing(T.SPACING_SM)
        self._param_widgets = {}
        self._param_scroll.setWidget(self._param_widget)
        right_layout.addWidget(self._param_scroll)

        # Apply button
        apply_btn = QPushButton("▶ Apply Pipeline")
        apply_btn.setObjectName("primaryBtn")
        apply_btn.clicked.connect(self._apply_pipeline)
        right_layout.addWidget(apply_btn)

        save_btn = QPushButton("💾 Save Config")
        save_btn.clicked.connect(self._save_config)
        right_layout.addWidget(save_btn)

        load_btn = QPushButton("📂 Load Config")
        load_btn.clicked.connect(self._load_config)
        right_layout.addWidget(load_btn)

        export_btn = QPushButton("📷 Export Image")
        export_btn.clicked.connect(self._export_image)
        right_layout.addWidget(export_btn)

        splitter.addWidget(right)
        splitter.setSizes([220, 700, 300])

        layout.addWidget(splitter, 1)

    def _filter_algorithms(self, category: str):
        """Filter algorithm list by category."""
        self._algo_list.clear()
        for key, info in ALGORITHMS.items():
            if category == "all" or info['category'] == category:
                item = QListWidgetItem(f"  {info['name']}")
                item.setData(Qt.UserRole, key)
                self._algo_list.addItem(item)

    def _add_algorithm(self, item: QListWidgetItem):
        """Add algorithm to pipeline."""
        algo_key = item.data(Qt.UserRole)
        if algo_key and algo_key not in [s[0] for s in self._pipeline_stages]:
            self._pipeline_stages.append((algo_key, {}, True))
            self._refresh_stage_list()
            self._show_params(len(self._pipeline_stages) - 1)

    def _refresh_stage_list(self):
        """Refresh pipeline stage list."""
        self._stage_list.clear()
        for i, (name, params, enabled) in enumerate(self._pipeline_stages):
            info = ALGORITHMS.get(name, {})
            text = f"  {i+1}. {info.get('name', name)}"
            if not enabled:
                text += " (disabled)"
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, i)
            self._stage_list.addItem(item)

    def _on_stage_selected(self):
        """Show parameters for selected stage."""
        items = self._stage_list.selectedItems()
        if items:
            idx = items[0].data(Qt.UserRole)
            self._show_params(idx)

    def _show_params(self, stage_idx: int):
        """Show parameter controls for a stage."""
        # Clear existing
        for w in list(self._param_widgets.values()):
            w.deleteLater()
        self._param_widgets.clear()

        if stage_idx >= len(self._pipeline_stages):
            return

        algo_key, params, enabled = self._pipeline_stages[stage_idx]
        info = ALGORITHMS.get(algo_key, {})

        # Enable checkbox
        chk = QCheckBox("Enabled")
        chk.setChecked(enabled)
        chk.toggled.connect(lambda c: self._toggle_stage(stage_idx, c))
        self._param_layout.addWidget(chk)
        self._param_widgets['enabled'] = chk

        # Parameters
        for pdef in info.get('params', []):
            pname, plabel, ptype, pdefault, pmin, pmax, pstep = pdef
            current = params.get(pname, pdefault)

            row = QHBoxLayout()
            lbl = QLabel(plabel)
            lbl.setObjectName("metricLabel")
            row.addWidget(lbl)

            if ptype == int:
                spin = QSpinBox()
                spin.setRange(pmin, pmax)
                spin.setSingleStep(pstep)
                spin.setValue(int(current))
                spin.valueChanged.connect(
                    lambda v, k=pname: self._set_param(stage_idx, k, v)
                )
                row.addWidget(spin)
                self._param_widgets[pname] = spin
            elif ptype == float:
                spin = QDoubleSpinBox()
                spin.setRange(pmin, pmax)
                spin.setSingleStep(pstep)
                spin.setDecimals(2)
                spin.setValue(float(current))
                spin.valueChanged.connect(
                    lambda v, k=pname: self._set_param(stage_idx, k, v)
                )
                row.addWidget(spin)
                self._param_widgets[pname] = spin
            elif ptype == str and isinstance(pmin, list):
                combo = QComboBox()
                combo.addItems(pmin)
                combo.setCurrentText(str(current))
                combo.currentTextChanged.connect(
                    lambda v, k=pname: self._set_param(stage_idx, k, v)
                )
                row.addWidget(combo)
                self._param_widgets[pname] = combo

            row.addStretch()
            self._param_layout.addLayout(row)

        self._param_layout.addStretch()

    def _set_param(self, stage_idx: int, key: str, value):
        """Set a parameter for a stage."""
        if 0 <= stage_idx < len(self._pipeline_stages):
            self._pipeline_stages[stage_idx][1][key] = value

    def _toggle_stage(self, stage_idx: int, enabled: bool):
        """Toggle stage enabled state."""
        if 0 <= stage_idx < len(self._pipeline_stages):
            self._pipeline_stages[stage_idx] = (
                self._pipeline_stages[stage_idx][0],
                self._pipeline_stages[stage_idx][1],
                enabled
            )
            self._refresh_stage_list()

    def _remove_selected_stage(self):
        """Remove selected stage from pipeline."""
        items = self._stage_list.selectedItems()
        if items:
            idx = items[0].data(Qt.UserRole)
            self._pipeline_stages.pop(idx)
            self._refresh_stage_list()
            self._clear_params()

    def _reset_pipeline(self):
        """Reset pipeline to empty."""
        self._pipeline_stages.clear()
        self._refresh_stage_list()
        self._clear_params()
        self._apply_pipeline()

    def _clear_params(self):
        """Clear parameter widgets."""
        for w in list(self._param_widgets.values()):
            w.deleteLater()
        self._param_widgets.clear()

    def _apply_pipeline(self):
        """Apply pipeline to current image."""
        import cv2
        if self._current_image is None:
            # Generate test image
            self._current_image = self._generate_test_image()

        # Build engine
        self._engine.clear_stages()
        for algo_key, params, enabled in self._pipeline_stages:
            stage = self._engine.create_stage(algo_key, **params)
            if stage:
                stage.set_enabled(enabled)
                self._engine.add_stage(stage)

        # Process
        result = self._engine.process(self._current_image)
        self._processed_image = result['output']

        # Display
        self._display_image(self._orig_view, self._current_image)
        self._display_image(self._proc_view, self._processed_image)

    def _display_image(self, view: CameraView, image: np.ndarray):
        """Display image in a camera view."""
        import cv2
        h, w = image.shape[:2]
        if len(image.shape) == 2:
            qimg = QImage(image.data, w, h, w, QImage.Format_Grayscale8)
        else:
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            qimg = QImage(rgb.data, w, h, w * 3, QImage.Format_RGB888)
        view.set_image(qimg)

    def _generate_test_image(self) -> np.ndarray:
        """Generate a test image for processing."""
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        # Gradient background
        for c in range(3):
            img[:, :, c] = np.tile(np.linspace(40 + c * 50, 150 + c * 30, 640), (480, 1))
        # Shapes
        cv2.rectangle(img, (100, 100), (300, 350), (0, 255, 255), -1)
        cv2.circle(img, (500, 240), 80, (255, 0, 255), -1)
        cv2.rectangle(img, (400, 380), (600, 460), (0, 200, 255), 3)
        # Text
        cv2.putText(img, "VISIONFORGE X", (50, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        return img

    def _load_default_pipeline(self):
        """Load a default pipeline configuration."""
        self._pipeline_stages = [
            ('gaussian_blur', {'kernel_size': 5, 'sigma': 0}, True),
            ('clahe', {'clip_limit': 2.5, 'tile_grid': 8}, True),
        ]
        self._refresh_stage_list()
        self._apply_pipeline()

    def _save_config(self):
        """Save pipeline configuration."""
        config = self._engine.save_config()
        from PySide6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getSaveFileName(self, "Save Pipeline Config",
                                               "pipeline_config.json", "JSON (*.json)")
        if path:
            import json
            with open(path, 'w') as f:
                json.dump(config, f, indent=2)

    def _load_config(self):
        """Load pipeline configuration."""
        from PySide6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getOpenFileName(self, "Load Pipeline Config",
                                               "", "JSON (*.json)")
        if path:
            import json
            with open(path, 'r') as f:
                config = json.load(f)
            self._engine.load_config(config)
            self._pipeline_stages = [
                (s.get('type', ''), s.get('params', {}), s.get('enabled', True))
                for s in config.get('stages', [])
            ]
            self._refresh_stage_list()
            self._apply_pipeline()

    def _export_image(self):
        """Export processed image."""
        if self._processed_image is not None:
            from PySide6.QtWidgets import QFileDialog
            path, _ = QFileDialog.getSaveFileName(self, "Export Image",
                                                   "processed.png", "PNG (*.png);;JPEG (*.jpg)")
            if path:
                import cv2
                cv2.imwrite(path, self._processed_image)

    def update_telemetry(self, data: dict):
        """Update telemetry (unused on this page)."""
        pass
