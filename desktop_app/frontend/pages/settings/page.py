"""VISIONFORGE X - System Configuration Page (Enhanced)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QScrollArea, QGroupBox, QComboBox, QFileDialog,
    QCheckBox, QSpinBox, QDoubleSpinBox, QLineEdit, QFormLayout,
    QTabWidget, QFrame, QInputDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from frontend.components.widgets import Panel, MetricTile, StatusBadge
from frontend.design_system.tokens import DesignTokens as T


class SystemConfigPage(QWidget):
    """System configuration and preferences - Enhanced."""

    def __init__(self, main_window):
        super().__init__()
        self._main = main_window
        self._settings = main_window._settings

        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(T.SPACING_LG, T.SPACING_LG, T.SPACING_LG, T.SPACING_LG)
        layout.setSpacing(T.SPACING_MD)

        title = QLabel("⚙️ System Configuration")
        title.setStyleSheet(
            f"color: {T.ACCENT_CYAN}; font-size: {T.FONT_SIZE_HERO}px; "
            f"font-weight: 800; letter-spacing: 1px;"
        )
        layout.addWidget(title)

        tabs = QTabWidget()

        # ---- Device Tab ----
        device_tab = QWidget()
        device_layout = QVBoxLayout(device_tab)

        device_panel = Panel("Device Connection")
        d_form = QFormLayout()

        # Mode
        self._mode_combo = QComboBox()
        self._mode_combo.addItems(["simulation", "hardware"])
        self._mode_combo.currentTextChanged.connect(self._on_mode_change)
        d_form.addRow("Mode:", self._mode_combo)

        # Board IP
        self._board_ip = QLineEdit("192.168.1.100")
        d_form.addRow("Board IP:", self._board_ip)

        # Ports
        self._tcp_port = QSpinBox()
        self._tcp_port.setRange(1, 65535)
        self._tcp_port.setValue(5000)
        d_form.addRow("TCP Port:", self._tcp_port)

        self._udp_port = QSpinBox()
        self._udp_port.setRange(1, 65535)
        self._udp_port.setValue(5001)
        d_form.addRow("UDP Port:", self._udp_port)

        # Timeouts
        self._comm_timeout = QDoubleSpinBox()
        self._comm_timeout.setRange(0.1, 30.0)
        self._comm_timeout.setSingleStep(0.5)
        self._comm_timeout.setValue(5.0)
        d_form.addRow("Comm Timeout (s):", self._comm_timeout)

        self._hb_timeout = QDoubleSpinBox()
        self._hb_timeout.setRange(1.0, 60.0)
        self._hb_timeout.setValue(10.0)
        d_form.addRow("Heartbeat Timeout (s):", self._hb_timeout)

        # Reconnect
        self._reconnect_chk = QCheckBox("Enable Auto-Reconnect")
        self._reconnect_chk.setChecked(True)
        d_form.addRow("", self._reconnect_chk)

        self._reconnect_delay = QDoubleSpinBox()
        self._reconnect_delay.setRange(0.5, 30.0)
        self._reconnect_delay.setSingleStep(0.5)
        self._reconnect_delay.setValue(2.0)
        d_form.addRow("Reconnect Delay (s):", self._reconnect_delay)

        device_panel.addLayout(d_form)
        device_layout.addWidget(device_panel)
        tabs.addTab(device_tab, "Device")

        # ---- Camera Tab ----
        camera_tab = QWidget()
        camera_layout = QVBoxLayout(camera_tab)

        cam_panel = Panel("Camera Settings")
        c_form = QFormLayout()

        self._res_combo = QComboBox()
        self._res_combo.addItems(["320x240", "640x480", "800x600", "1280x720"])
        c_form.addRow("Preview Resolution:", self._res_combo)

        self._target_fps = QSpinBox()
        self._target_fps.setRange(1, 60)
        self._target_fps.setValue(30)
        c_form.addRow("Target FPS:", self._target_fps)

        self._proc_mode = QComboBox()
        self._proc_mode.addItems(["quality", "balanced", "performance"])
        c_form.addRow("Processing Mode:", self._proc_mode)

        self._cam_source = QComboBox()
        self._cam_source.addItems(["simulation", "webcam", "file"])
        c_form.addRow("Source:", self._cam_source)

        cam_panel.addLayout(c_form)
        camera_layout.addWidget(cam_panel)
        tabs.addTab(camera_tab, "Camera")

        # ---- AI Tab ----
        ai_tab = QWidget()
        ai_layout = QVBoxLayout(ai_tab)

        ai_panel = Panel("AI Settings")
        a_form = QFormLayout()

        self._ai_device = QComboBox()
        self._ai_device.addItems(["cpu", "cuda"])
        a_form.addRow("Inference Device:", self._ai_device)

        self._conf_threshold = QDoubleSpinBox()
        self._conf_threshold.setRange(0.0, 1.0)
        self._conf_threshold.setSingleStep(0.05)
        self._conf_threshold.setValue(0.5)
        a_form.addRow("Confidence Threshold:", self._conf_threshold)

        self._infer_interval = QSpinBox()
        self._infer_interval.setRange(1, 30)
        self._infer_interval.setValue(1)
        a_form.addRow("Inference Interval (frames):", self._infer_interval)

        self._adaptive_chk = QCheckBox("Enable Adaptive Controller")
        self._adaptive_chk.setChecked(True)
        a_form.addRow("", self._adaptive_chk)

        ai_panel.addLayout(a_form)
        ai_layout.addWidget(ai_panel)
        tabs.addTab(ai_tab, "AI")

        # ---- Storage Tab ----
        storage_tab = QWidget()
        storage_layout = QVBoxLayout(storage_tab)

        storage_panel = Panel("Storage Settings")
        s_form = QFormLayout()

        self._db_path = QLineEdit("./storage/visionforge.db")
        browse_db = QPushButton("Browse")
        browse_db.clicked.connect(lambda: self._browse_path(self._db_path))
        db_row = QHBoxLayout()
        db_row.addWidget(self._db_path)
        db_row.addWidget(browse_db)
        s_form.addRow("Database Path:", db_row)

        self._storage_path = QLineEdit("./storage")
        browse_st = QPushButton("Browse")
        browse_st.clicked.connect(lambda: self._browse_path(self._storage_path))
        st_row = QHBoxLayout()
        st_row.addWidget(self._storage_path)
        st_row.addWidget(browse_st)
        s_form.addRow("Storage Path:", st_row)

        self._dataset_path = QLineEdit("./datasets")
        browse_ds = QPushButton("Browse")
        browse_ds.clicked.connect(lambda: self._browse_path(self._dataset_path))
        ds_row = QHBoxLayout()
        ds_row.addWidget(self._dataset_path)
        ds_row.addWidget(browse_ds)
        s_form.addRow("Dataset Path:", ds_row)

        self._log_path = QLineEdit("./logs")
        s_form.addRow("Log Path:", self._log_path)

        self._retention = QSpinBox()
        self._retention.setRange(7, 365)
        self._retention.setValue(90)
        s_form.addRow("Data Retention (days):", self._retention)

        storage_layout.addWidget(storage_panel)
        tabs.addTab(storage_tab, "Storage")

        # ---- Actions Tab ----
        actions_tab = QWidget()
        actions_layout = QVBoxLayout(actions_tab)

        # Save/Load config
        save_btn = QPushButton("💾 Save Configuration")
        save_btn.setObjectName("primaryBtn")
        save_btn.clicked.connect(self._save_settings)
        actions_layout.addWidget(save_btn)

        export_btn = QPushButton("📤 Export Configuration")
        export_btn.clicked.connect(self._export_config)
        actions_layout.addWidget(export_btn)

        import_btn = QPushButton("📥 Import Configuration")
        import_btn.clicked.connect(self._import_config)
        actions_layout.addWidget(import_btn)

        reset_btn = QPushButton("↺ Reset to Defaults")
        reset_btn.clicked.connect(self._reset_config)
        actions_layout.addWidget(reset_btn)

        # Status
        self._status = StatusBadge("Ready", "info")
        actions_layout.addWidget(self._status)

        actions_layout.addStretch()
        tabs.addTab(actions_tab, "Actions")

        layout.addWidget(tabs, 1)

    def _load_settings(self):
        """Load current settings into UI."""
        cfg = self._settings.config
        self._mode_combo.setCurrentText(cfg.device.mode)
        self._board_ip.setText(cfg.device.board_ip)
        self._tcp_port.setValue(cfg.device.tcp_port)
        self._udp_port.setValue(cfg.device.udp_port)
        self._comm_timeout.setValue(cfg.device.comm_timeout)
        self._hb_timeout.setValue(cfg.device.heartbeat_timeout)
        self._reconnect_chk.setChecked(cfg.device.reconnect_enabled)
        self._reconnect_delay.setValue(cfg.device.reconnect_delay)

        self._res_combo.setCurrentText(cfg.camera.preview_resolution)
        self._target_fps.setValue(cfg.camera.target_fps)
        self._proc_mode.setCurrentText(cfg.camera.processing_mode)
        self._cam_source.setCurrentText(cfg.camera.source)

        self._ai_device.setCurrentText(cfg.ai.device)
        self._conf_threshold.setValue(cfg.ai.confidence_threshold)
        self._infer_interval.setValue(cfg.ai.inference_interval)
        self._adaptive_chk.setChecked(cfg.adaptive_enabled)

        self._db_path.setText(cfg.storage.db_path)
        self._storage_path.setText(cfg.storage.base_path)
        self._dataset_path.setText(cfg.storage.dataset_path)
        self._log_path.setText(cfg.storage.log_path)
        self._retention.setValue(cfg.storage.data_retention_days)

    def _save_settings(self):
        """Save UI settings to config."""
        cfg = self._settings.config
        cfg.device.mode = self._mode_combo.currentText()
        cfg.device.board_ip = self._board_ip.text()
        cfg.device.tcp_port = self._tcp_port.value()
        cfg.device.udp_port = self._udp_port.value()
        cfg.device.comm_timeout = self._comm_timeout.value()
        cfg.device.heartbeat_timeout = self._hb_timeout.value()
        cfg.device.reconnect_enabled = self._reconnect_chk.isChecked()
        cfg.device.reconnect_delay = self._reconnect_delay.value()

        cfg.camera.preview_resolution = self._res_combo.currentText()
        cfg.camera.target_fps = self._target_fps.value()
        cfg.camera.processing_mode = self._proc_mode.currentText()
        cfg.camera.source = self._cam_source.currentText()

        cfg.ai.device = self._ai_device.currentText()
        cfg.ai.confidence_threshold = self._conf_threshold.value()
        cfg.ai.inference_interval = self._infer_interval.value()
        cfg.adaptive_enabled = self._adaptive_chk.isChecked()

        cfg.storage.db_path = self._db_path.text()
        cfg.storage.base_path = self._storage_path.text()
        cfg.storage.dataset_path = self._dataset_path.text()
        cfg.storage.log_path = self._log_path.text()
        cfg.storage.data_retention_days = self._retention.value()

        if self._settings.save():
            self._status.setText("Saved")
            self._status.set_status("good")
            self._main._event_mgr.emit('system', 'info', 'Configuration saved')
        else:
            self._status.setText("Save Failed")
            self._status.set_status("error")

    def _on_mode_change(self, mode: str):
        """Handle mode change."""
        hw_enabled = (mode == "hardware")
        self._board_ip.setEnabled(hw_enabled)
        self._tcp_port.setEnabled(hw_enabled)
        self._udp_port.setEnabled(hw_enabled)
        self._comm_timeout.setEnabled(hw_enabled)
        self._hb_timeout.setEnabled(hw_enabled)
        self._reconnect_chk.setEnabled(hw_enabled)
        self._reconnect_delay.setEnabled(hw_enabled)

    def _browse_path(self, line_edit: QLineEdit):
        """Browse for path."""
        if line_edit.text().endswith('.db') or 'database' in line_edit.objectName().lower():
            path, _ = QFileDialog.getSaveFileName(self, "Select Path", line_edit.text())
        else:
            path = QFileDialog.getExistingDirectory(self, "Select Directory", line_edit.text())
        if path:
            line_edit.setText(path)

    def _export_config(self):
        """Export configuration to file."""
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Config", "config_export.json", "JSON (*.json)")
        if path and self._settings.export(path):
            self._main._event_mgr.emit('system', 'info', f'Config exported: {os.path.basename(path)}')

    def _import_config(self):
        """Import configuration from file."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Import Config", "", "JSON (*.json)")
        if path and self._settings.import_config(path):
            self._load_settings()
            self._main._event_mgr.emit('system', 'info', 'Config imported')

    def _reset_config(self):
        """Reset configuration to defaults."""
        self._settings.reset()
        self._load_settings()
        self._main._event_mgr.emit('system', 'info', 'Config reset to defaults')

    def update_telemetry(self, data: dict):
        pass
