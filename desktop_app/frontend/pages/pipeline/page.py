"""VISIONFORGE X - Pipeline Architect Page (Enhanced)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QScrollArea, QGroupBox, QComboBox, QFileDialog,
    QListWidget, QListWidgetItem, QTableWidget, QTableWidgetItem,
    QSplitter, QFrame, QCheckBox, QSpinBox, QLineEdit, QDialog, QDialogButtonBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QImage, QFont
import numpy as np
import cv2

from frontend.components.widgets import Panel, MetricTile, StatusBadge
from frontend.design_system.tokens import DesignTokens as T
from backend.pipeline.engine import (
    PipelineEngine, PipelineNode, PipelineConnection,
    PipelineValidator, NodeType
)


class NodeConfigDialog(QDialog):
    """Dialog to configure a pipeline node."""

    def __init__(self, node: PipelineNode, parent=None):
        super().__init__(parent)
        self._node = node
        self.setWindowTitle(f"Configure: {node.node_type}")
        self.setMinimumWidth(350)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel(f"Node: {node.node_type}"))

        self._param_widgets = {}
        config = node.config

        # Default params based on type
        defaults = {
            'grayscale': {},
            'gaussian_blur': {'kernel_size': 5},
            'median_filter': {'kernel_size': 5},
            'clahe': {'clip_limit': 2.0, 'tile_grid': 8},
            'edge_detection': {'threshold1': 100, 'threshold2': 200},
            'threshold': {'threshold': 127},
            'morphology': {'operation': 'opening', 'kernel_size': 3, 'iterations': 1},
            'roi': {'x': 0, 'y': 0, 'width': 320, 'height': 240},
            'motion_detection': {'threshold': 25, 'min_area': 500},
            'ai_inference': {'interval': 1},
            'anomaly_detection': {'threshold': 0.5},
        }
        params = defaults.get(node.node_type, {})

        for key, default in params.items():
            row = QHBoxLayout()
            row.addWidget(QLabel(f"{key}:"))
            if isinstance(default, float):
                spin = QSpinBox()
                spin.setRange(0, 1000)
                spin.setSingleStep(1)
                spin.setValue(int(config.get(key, default) * 100))
                spin.valueChanged.connect(
                    lambda v, k=key: self._update_param(k, v / 100.0)
                )
                row.addWidget(spin)
                self._param_widgets[key] = spin
            elif isinstance(default, str):
                combo = QComboBox()
                if key == 'operation':
                    combo.addItems(['erosion', 'dilation', 'opening', 'closing'])
                combo.setCurrentText(str(config.get(key, default)))
                combo.currentTextChanged.connect(
                    lambda v, k=key: self._update_param(k, v)
                )
                row.addWidget(combo)
                self._param_widgets[key] = combo
            else:
                spin = QSpinBox()
                spin.setRange(0, 10000)
                spin.setValue(int(config.get(key, default)))
                spin.valueChanged.connect(
                    lambda v, k=key: self._update_param(k, v)
                )
                row.addWidget(spin)
                self._param_widgets[key] = spin
            row.addStretch()
            layout.addLayout(row)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _update_param(self, key, value):
        self._node.config[key] = value


class PipelineArchitectPage(QWidget):
    """Visual processing pipeline editor - Enhanced."""

    def __init__(self, main_window):
        super().__init__()
        self._main = main_window
        self._engine = PipelineEngine()
        self._node_counter = 0
        self._selected_node = None

        self._setup_ui()
        self._load_template("Basic Enhancement")

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(T.SPACING_LG, T.SPACING_LG, T.SPACING_LG, T.SPACING_LG)
        layout.setSpacing(T.SPACING_MD)

        title = QLabel("🔗 Pipeline Architect")
        title.setStyleSheet(
            f"color: {T.ACCENT_CYAN}; font-size: {T.FONT_SIZE_HERO}px; "
            f"font-weight: 800; letter-spacing: 1px;"
        )
        layout.addWidget(title)

        # Toolbar
        toolbar = QHBoxLayout()

        template_lbl = QLabel("Template:")
        template_lbl.setObjectName("metricLabel")
        toolbar.addWidget(template_lbl)
        self._template_combo = QComboBox()
        self._template_combo.addItems(["Basic Enhancement", "Motion Detection", "AI Analysis"])
        self._template_combo.currentTextChanged.connect(self._load_template)
        toolbar.addWidget(self._template_combo)

        toolbar.addSpacing(10)

        add_btn = QPushButton("➕ Add Node")
        add_btn.clicked.connect(self._add_node_dialog)
        toolbar.addWidget(add_btn)

        save_btn = QPushButton("💾 Save")
        save_btn.clicked.connect(self._save_pipeline)
        toolbar.addWidget(save_btn)

        load_btn = QPushButton("📂 Load")
        load_btn.clicked.connect(self._load_pipeline)
        toolbar.addWidget(load_btn)

        validate_btn = QPushButton("✓ Validate")
        validate_btn.clicked.connect(self._validate_pipeline)
        toolbar.addWidget(validate_btn)

        apply_btn = QPushButton("▶ Apply")
        apply_btn.setObjectName("primaryBtn")
        apply_btn.clicked.connect(self._apply_pipeline)
        toolbar.addWidget(apply_btn)

        toolbar.addStretch()

        self._status_badge = StatusBadge("Not validated", "info")
        toolbar.addWidget(self._status_badge)

        layout.addLayout(toolbar)

        # Main splitter
        splitter = QSplitter(Qt.Horizontal)

        # Left: Node palette
        left = Panel("Node Types")
        left_layout = left._layout
        self._node_palette = QListWidget()
        for nt in NodeType:
            item = QListWidgetItem(f"  {nt.value}")
            item.setData(Qt.UserRole, nt.value)
            self._node_palette.addItem(item)
        self._node_palette.itemDoubleClicked.connect(self._add_node_from_palette)
        left_layout.addWidget(self._node_palette)
        splitter.addWidget(left)

        # Center: Node list and connections
        center = Panel("Pipeline Configuration")
        center_layout = center._layout

        self._node_table = QTableWidget(0, 5)
        self._node_table.setHorizontalHeaderLabels(["ID", "Type", "Enabled", "Source", "Actions"])
        self._node_table.itemSelectionChanged.connect(self._on_node_selected)
        center_layout.addWidget(self._node_table)

        # Connection editor
        conn_panel = QGroupBox("Connections")
        conn_layout = QHBoxLayout(conn_panel)
        conn_layout.addWidget(QLabel("From:"))
        self._conn_from = QComboBox()
        conn_layout.addWidget(self._conn_from)
        conn_layout.addWidget(QLabel("To:"))
        self._conn_to = QComboBox()
        conn_layout.addWidget(self._conn_to)
        connect_btn = QPushButton("Connect")
        connect_btn.clicked.connect(self._add_connection)
        conn_layout.addWidget(connect_btn)
        remove_conn_btn = QPushButton("Remove")
        remove_conn_btn.clicked.connect(self._remove_connection)
        conn_layout.addWidget(remove_conn_btn)
        conn_layout.addStretch()
        center_layout.addWidget(conn_panel)

        splitter.addWidget(center)

        # Right: Node details
        right = Panel("Node Details")
        right_layout = right._layout
        self._node_detail = QLabel("Select a node to view details")
        self._node_detail.setWordWrap(True)
        right_layout.addWidget(self._node_detail)

        config_btn = QPushButton("⚙ Configure")
        config_btn.clicked.connect(self._configure_selected)
        right_layout.addWidget(config_btn)

        enable_chk = QCheckBox("Enabled")
        enable_chk.toggled.connect(self._toggle_selected)
        right_layout.addWidget(enable_chk)
        self._enable_chk = enable_chk

        remove_node_btn = QPushButton("🗑 Remove Node")
        remove_node_btn.clicked.connect(self._remove_selected)
        right_layout.addWidget(remove_node_btn)

        right_layout.addStretch()
        splitter.addWidget(right)

        splitter.setSizes([180, 500, 250])
        layout.addWidget(splitter, 1)

    def _add_node_from_palette(self, item: QListWidgetItem):
        node_type = item.data(Qt.UserRole)
        self._create_node(node_type)

    def _add_node_dialog(self):
        """Add node via dialog."""
        self._create_node('grayscale')

    def _create_node(self, node_type: str):
        self._node_counter += 1
        node = PipelineNode(
            id=f"node_{self._node_counter}",
            node_type=node_type,
            config={},
            enabled=True,
            execution_source="HOST"
        )
        self._engine.add_node(node)
        self._refresh_node_table()
        self._refresh_combo_boxes()

    def _refresh_node_table(self):
        """Refresh node table."""
        self._node_table.setRowCount(0)
        for node in self._engine._nodes.values():
            row = self._node_table.rowCount()
            self._node_table.insertRow(row)
            self._node_table.setItem(row, 0, QTableWidgetItem(node.id))
            self._node_table.setItem(row, 1, QTableWidgetItem(node.node_type))

            enabled_item = QTableWidgetItem("✓" if node.enabled else "✗")
            self._node_table.setItem(row, 2, enabled_item)
            self._node_table.setItem(row, 3, QTableWidgetItem(node.execution_source))

            # Config button
            config_btn = QPushButton("⚙")
            config_btn.setMaximumWidth(30)
            config_btn.clicked.connect(
                lambda checked, n=node: self._configure_node(n)
            )
            self._node_table.setCellWidget(row, 4, config_btn)

    def _refresh_combo_boxes(self):
        """Refresh connection combo boxes."""
        for combo in [self._conn_from, self._conn_to]:
            current = combo.currentText()
            combo.clear()
            for node in self._engine._nodes.values():
                combo.addItem(f"{node.id} ({node.node_type})")
            idx = combo.findText(current)
            if idx >= 0:
                combo.setCurrentIndex(idx)

    def _on_node_selected(self):
        """Show details for selected node."""
        items = self._node_table.selectedItems()
        if items:
            node_id = items[0].text()
            node = self._engine._nodes.get(node_id)
            if node:
                self._selected_node = node
                self._node_detail.setText(
                    f"ID: {node.id}\nType: {node.node_type}\n"
                    f"Enabled: {node.enabled}\nSource: {node.execution_source}\n"
                    f"Config: {node.config}"
                )
                self._enable_chk.setChecked(node.enabled)

    def _configure_selected(self):
        if self._selected_node:
            self._configure_node(self._selected_node)

    def _configure_node(self, node: PipelineNode):
        dialog = NodeConfigDialog(node, self)
        if dialog.exec():
            self._refresh_node_table()
            self._on_node_selected()

    def _toggle_selected(self, enabled: bool):
        if self._selected_node:
            self._engine.set_node_enabled(self._selected_node.id, enabled)
            self._refresh_node_table()

    def _remove_selected(self):
        if self._selected_node:
            self._engine.remove_node(self._selected_node.id)
            self._selected_node = None
            self._node_detail.setText("Select a node to view details")
            self._refresh_node_table()
            self._refresh_combo_boxes()

    def _add_connection(self):
        from_text = self._conn_from.currentText().split()[0]
        to_text = self._conn_to.currentText().split()[0]
        self._engine.connect(from_text, to_text)
        self._status_badge.setText("Connections updated")
        self._status_badge.set_status("info")

    def _remove_connection(self):
        from_text = self._conn_from.currentText().split()[0]
        to_text = self._conn_to.currentText().split()[0]
        self._engine.disconnect(from_text, to_text)

    def _validate_pipeline(self):
        is_valid, errors = self._engine.validate()
        if is_valid:
            self._status_badge.setText("Valid ✓")
            self._status_badge.set_status("good")
        else:
            self._status_badge.setText(f"Invalid: {len(errors)} errors")
            self._status_badge.set_status("error")
            msg = "\n".join(errors)
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Validation Failed", msg)

    def _apply_pipeline(self):
        is_valid, _ = self._engine.validate()
        if not is_valid:
            self._validate_pipeline()
            return

        # Generate test frame and process
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        for c in range(3):
            test_frame[:, :, c] = np.tile(
                np.linspace(40 + c * 50, 150 + c * 30, 640), (480, 1)
            )
        cv2.rectangle(test_frame, (100, 100), (300, 350), (0, 255, 255), -1)

        result = self._engine.process_frame(test_frame)
        self._main._event_mgr.emit(
            'pipeline', 'info',
            f'Pipeline applied: {len(result.get("stages", []))} stages processed'
        )

    def _load_template(self, name: str):
        """Load a predefined template."""
        templates = PipelineEngine.get_templates()
        for t in templates:
            if t.name == name:
                self._engine._nodes.clear()
                self._engine._connections.clear()
                for nd in t.nodes:
                    node = PipelineNode(
                        id=nd['id'], node_type=nd['node_type'],
                        config=nd.get('config', {}),
                        enabled=nd.get('enabled', True),
                        execution_source=nd.get('execution_source', 'HOST'),
                        position=nd.get('position', {'x': 0, 'y': 0})
                    )
                    self._engine.add_node(node)
                for c in t.connections:
                    self._engine.connect(c['source_id'], c['target_id'])
                self._refresh_node_table()
                self._refresh_combo_boxes()
                break

    def _save_pipeline(self):
        config = self._engine.get_config()
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Pipeline", "pipeline.json", "JSON (*.json)")
        if path:
            import json
            with open(path, 'w') as f:
                json.dump(config, f, indent=2)

    def _load_pipeline(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Load Pipeline", "", "JSON (*.json)")
        if path:
            import json
            with open(path, 'r') as f:
                config = json.load(f)
            self._engine.load_config(config)
            self._refresh_node_table()
            self._refresh_combo_boxes()

    def update_telemetry(self, data: dict):
        pass
