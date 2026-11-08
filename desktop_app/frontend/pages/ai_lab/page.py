"""VISIONFORGE X - AI Intelligence Lab Page (Enhanced)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFrame, QLabel,
    QPushButton, QScrollArea, QGroupBox, QComboBox, QFileDialog,
    QListWidget, QListWidgetItem, QTableWidget, QTableWidgetItem, QTabWidget,
    QProgressBar, QSlider
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QFont
import numpy as np
import cv2

from frontend.components.widgets import Panel, MetricTile, StatusBadge, CameraView
from frontend.design_system.tokens import DesignTokens as T
from backend.ai.registry import ModelRegistry, ModelType, ModelLoader


class AILabPage(QWidget):
    """AI model management and inference - Enhanced."""

    def __init__(self, main_window):
        super().__init__()
        self._main = main_window
        self._registry = main_window._model_registry
        self._current_inference = None
        self._detection_overlay = None

        self._setup_ui()
        self._refresh_model_list()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(T.SPACING_LG, T.SPACING_LG, T.SPACING_LG, T.SPACING_LG)
        layout.setSpacing(T.SPACING_MD)

        # Title
        title = QLabel("🧠 AI Intelligence Lab")
        title.setStyleSheet(
            f"color: {T.ACCENT_VIOLET}; font-size: {T.FONT_SIZE_HERO}px; "
            f"font-weight: 800; letter-spacing: 1px;"
        )
        layout.addWidget(title)

        # Tabs
        tabs = QTabWidget()

        # ---- Model Library Tab ----
        model_tab = QWidget()
        model_layout = QHBoxLayout(model_tab)

        # Model list
        model_list_panel = Panel("Model Library")
        list_layout = model_list_panel._layout

        self._model_list = QListWidget()
        self._model_list.itemSelectionChanged.connect(self._on_model_selected)
        list_layout.addWidget(self._model_list)

        # Model actions
        actions = QHBoxLayout()
        import_btn = QPushButton("📂 Import Model")
        import_btn.clicked.connect(self._import_model)
        load_btn = QPushButton("▶ Load")
        load_btn.clicked.connect(self._load_model)
        unload_btn = QPushButton("⏹ Unload")
        unload_btn.clicked.connect(self._unload_model)
        actions.addWidget(import_btn)
        actions.addWidget(load_btn)
        actions.addWidget(unload_btn)
        list_layout.addLayout(actions)

        model_layout.addWidget(model_list_panel)

        # Model details
        detail_panel = Panel("Model Details")
        detail_layout = detail_panel._layout

        self._model_name = QLabel("—")
        self._model_name.setStyleSheet(
            f"font-size: {T.FONT_SIZE_MEDIUM+2}px; font-weight: 700; color: {T.ACCENT_VIOLET};"
        )
        detail_layout.addWidget(self._model_name)

        detail_grid = QGridLayout()
        self._model_type_lbl = QLabel("Type: —")
        self._model_ver_lbl = QLabel("Version: —")
        self._model_shape_lbl = QLabel("Input: —")
        self._model_fw_lbl = QLabel("Framework: —")
        self._model_status = StatusBadge("Unloaded", "error")
        self._model_classes_lbl = QLabel("Classes: —")

        detail_grid.addWidget(QLabel("Type:"), 0, 0)
        detail_grid.addWidget(self._model_type_lbl, 0, 1)
        detail_grid.addWidget(QLabel("Version:"), 1, 0)
        detail_grid.addWidget(self._model_ver_lbl, 1, 1)
        detail_grid.addWidget(QLabel("Input:"), 2, 0)
        detail_grid.addWidget(self._model_shape_lbl, 2, 1)
        detail_grid.addWidget(QLabel("Framework:"), 3, 0)
        detail_grid.addWidget(self._model_fw_lbl, 3, 1)
        detail_grid.addWidget(QLabel("Status:"), 4, 0)
        detail_grid.addWidget(self._model_status, 4, 1)
        detail_grid.addWidget(QLabel("Classes:"), 5, 0, 1, 2)
        detail_layout.addLayout(detail_grid)

        self._model_classes_lbl.setWordWrap(True)
        detail_layout.addWidget(self._model_classes_lbl)

        # Confidence threshold
        conf_row = QHBoxLayout()
        conf_row.addWidget(QLabel("Confidence Threshold:"))
        self._conf_slider = QSlider(Qt.Horizontal)
        self._conf_slider.setRange(0, 100)
        self._conf_slider.setValue(50)
        self._conf_slider.valueChanged.connect(
            lambda v: self._conf_label.setText(f"{v/100:.2f}")
        )
        conf_row.addWidget(self._conf_slider)
        self._conf_label = QLabel("0.50")
        self._conf_label.setObjectName("metricValue")
        self._conf_label.setStyleSheet(f"color: {T.ACCENT_VIOLET};")
        conf_row.addWidget(self._conf_label)
        detail_layout.addLayout(conf_row)

        model_layout.addWidget(detail_panel, 1)
        tabs.addTab(model_tab, "Model Library")

        # ---- Inference Tab ----
        infer_tab = QWidget()
        infer_layout = QVBoxLayout(infer_tab)

        # Preview
        self._infer_view = CameraView("Inference Preview")
        self._infer_view.set_placeholder("Load a model and run inference", T.TEXT_MUTED)
        infer_layout.addWidget(self._infer_view, 1)

        # Controls
        ctrl_row = QHBoxLayout()
        run_btn = QPushButton("▶ Run Inference")
        run_btn.setObjectName("primaryBtn")
        run_btn.clicked.connect(self._run_inference)
        ctrl_row.addWidget(run_btn)

        self._infer_status = StatusBadge("Ready", "info")
        ctrl_row.addWidget(self._infer_status)
        ctrl_row.addStretch()
        infer_layout.addLayout(ctrl_row)

        # Results
        result_panel = Panel("Inference Results")
        result_layout = result_panel._layout

        self._infer_time = QLabel("Inference Time: —")
        self._infer_time.setObjectName("metricLabel")
        result_layout.addWidget(self._infer_time)

        self._infer_conf = QLabel("Confidence: —")
        self._infer_conf.setObjectName("metricLabel")
        result_layout.addWidget(self._infer_conf)

        self._infer_results = QTableWidget(0, 3)
        self._infer_results.setHorizontalHeaderLabels(["Class", "Confidence", "Bounding Box"])
        self._infer_results.setMaximumHeight(200)
        result_layout.addWidget(self._infer_results)

        infer_layout.addWidget(result_panel)
        tabs.addTab(infer_tab, "Inference")

        # ---- History Tab ----
        hist_tab = QWidget()
        hist_layout = QVBoxLayout(hist_tab)
        self._history_table = QTableWidget(0, 4)
        self._history_table.setHorizontalHeaderLabels(["Timestamp", "Model", "Time (ms)", "Confidence"])
        hist_layout.addWidget(self._history_table)
        tabs.addTab(hist_tab, "History")

        layout.addWidget(tabs, 1)

    def _refresh_model_list(self):
        """Refresh model list."""
        self._model_list.clear()
        for model in self._registry.get_models():
            status = "loaded" if self._registry.is_model_loaded(model.name) else "unloaded"
            item = QListWidgetItem(f"  {model.name} ({model.model_type})")
            item.setData(Qt.UserRole, model)
            color = T.STATUS_GREEN if status == "loaded" else T.TEXT_MUTED
            item.setForeground(QColor(color))
            self._model_list.addItem(item)

    def _on_model_selected(self):
        """Show model details."""
        items = self._model_list.selectedItems()
        if items:
            model = items[0].data(Qt.UserRole)
            self._model_name.setText(model.name)
            self._model_type_lbl.setText(f"Type: {model.model_type}")
            self._model_ver_lbl.setText(f"Version: {model.version}")
            self._model_shape_lbl.setText(f"Input: {model.input_shape}")
            self._model_fw_lbl.setText(f"Framework: {model.framework}")
            self._model_status.setText("Loaded" if self._registry.is_model_loaded(model.name) else "Unloaded")
            self._model_status.set_status("good" if self._registry.is_model_loaded(model.name) else "error")
            self._model_classes_lbl.setText(f"Classes: {', '.join(model.classes)}")

    def _import_model(self):
        """Import a new model."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Model File", "",
            "Models (*.onnx *.pt *.pth *.tflite);;All Files (*)"
        )
        if path:
            name = os.path.splitext(os.path.basename(path))[0]
            valid, msg, meta = ModelLoader.validate_model(path)

            # Determine type
            model_type = ModelType.CLASSIFICATION.value
            classes = ['class_0', 'class_1', 'class_2']

            model = self._registry.register(
                name=name,
                model_type=model_type,
                path=path,
                version=meta.get('ir_version', '1.0'),
                input_shape=tuple(meta.get('input_shape', [1, 3, 224, 224])),
                classes=classes,
                framework=meta.get('framework', 'onnx'),
                quantized=False,
                metadata=meta
            )
            if model:
                self._refresh_model_list()
                self._main._event_mgr.emit('ai', 'info', f'Model imported: {name}')

    def _load_model(self):
        """Load selected model."""
        items = self._model_list.selectedItems()
        if items:
            model = items[0].data(Qt.UserRole)
            if self._registry.load_model(model.name, self._main._settings.config.ai.device):
                self._model_status.setText("Loaded")
                self._model_status.set_status("good")
                self._infer_view.set_placeholder("Model loaded - ready for inference", T.STATUS_GREEN)
                self._main._event_mgr.emit('ai', 'info', f'Model loaded: {model.name}')
            else:
                self._model_status.setText("Error")
                self._model_status.set_status("error")
                self._main._event_mgr.emit('ai', 'error', f'Failed to load model: {model.name}')
            self._refresh_model_list()

    def _unload_model(self):
        """Unload selected model."""
        items = self._model_list.selectedItems()
        if items:
            model = items[0].data(Qt.UserRole)
            self._registry.unload_model(model.name)
            self._model_status.setText("Unloaded")
            self._model_status.set_status("error")
            self._refresh_model_list()

    def _run_inference(self):
        """Run inference on test image."""
        if not self._registry.is_model_loaded():
            self._infer_status.setText("No model loaded")
            self._infer_status.set_status("error")
            return

        # Generate test image
        test_img = np.zeros((480, 640, 3), dtype=np.uint8)
        for c in range(3):
            test_img[:, :, c] = np.tile(np.linspace(40 + c * 50, 150 + c * 30, 640), (480, 1))
        cv2.rectangle(test_img, (100, 100), (300, 350), (0, 255, 255), -1)
        cv2.circle(test_img, (500, 240), 80, (255, 0, 255), -1)

        # Run inference
        threshold = self._conf_slider.value() / 100.0
        result = self._registry.infer(test_img, threshold)

        if result:
            self._current_inference = result
            self._infer_time.setText(f"Inference Time: {result.inference_time_ms:.2f} ms")
            self._infer_conf.setText(f"Confidence: {result.confidence:.3f}")
            self._infer_status.setText("Completed")
            self._infer_status.set_status("good")

            # Display results
            self._infer_results.setRowCount(0)
            for pred in result.predictions:
                row = self._infer_results.rowCount()
                self._infer_results.insertRow(row)
                self._infer_results.setItem(row, 0, QTableWidgetItem(pred.get('class', 'N/A')))
                self._infer_results.setItem(row, 1, QTableWidgetItem(f"{pred.get('confidence', 0):.3f}"))
                bbox = pred.get('bbox')
                if bbox:
                    self._infer_results.setItem(row, 2, QTableWidgetItem(
                        f"[{bbox[0]}, {bbox[1]}, {bbox[2]}, {bbox[3]}]"))
                else:
                    self._infer_results.setItem(row, 2, QTableWidgetItem("-"))

            # Display image
            h, w = test_img.shape[:2]
            rgb = cv2.cvtColor(test_img, cv2.COLOR_BGR2RGB)
            qimg = QImage(rgb.data, w, h, w * 3, QImage.Format_RGB888)
            self._infer_view.set_image(qimg)

            # Record in history
            hist_row = self._history_table.rowCount()
            self._history_table.insertRow(hist_row)
            self._history_table.setItem(hist_row, 0, QTableWidgetItem(result.timestamp))
            self._history_table.setItem(hist_row, 1, QTableWidgetItem(result.model_name))
            self._history_table.setItem(hist_row, 2, QTableWidgetItem(f"{result.inference_time_ms:.2f}"))
            self._history_table.setItem(hist_row, 3, QTableWidgetItem(f"{result.confidence:.3f}"))

    def update_telemetry(self, data: dict):
        """Update telemetry."""
        pass


import os
