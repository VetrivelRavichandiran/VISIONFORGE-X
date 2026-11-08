"""VISIONFORGE X - Research Reports Page (Enhanced)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QScrollArea, QGroupBox, QComboBox, QFileDialog,
    QCheckBox, QSpinBox, QFormLayout, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from frontend.components.widgets import Panel, MetricTile, StatusBadge
from frontend.design_system.tokens import DesignTokens as T
from backend.reports.generator import ReportGenerator, ReportConfig


class ResearchReportsPage(QWidget):
    """Report generation module - Enhanced."""

    def __init__(self, main_window):
        super().__init__()
        self._main = main_window
        self._report_gen = main_window._report_gen

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(T.SPACING_LG, T.SPACING_LG, T.SPACING_LG, T.SPACING_LG)
        layout.setSpacing(T.SPACING_MD)

        title = QLabel("📄 Research Reports")
        title.setStyleSheet(
            f"color: {T.ACCENT_CYAN}; font-size: {T.FONT_SIZE_HERO}px; "
            f"font-weight: 800; letter-spacing: 1px;"
        )
        layout.addWidget(title)

        # Report configuration
        config_panel = Panel("Report Configuration")
        cfg_layout = config_panel._layout

        # Report type
        type_row = QHBoxLayout()
        type_row.addWidget(QLabel("Report Type:"))
        self._report_type = QComboBox()
        self._report_type.addItems(["benchmark", "system", "experiment", "event_summary"])
        type_row.addWidget(self._report_type)
        type_row.addStretch()
        cfg_layout.addLayout(type_row)

        # Title
        title_row = QHBoxLayout()
        title_row.addWidget(QLabel("Report Title:"))
        self._report_title = QLabel("VISIONFORGE X Report")
        title_row.addWidget(self._report_title)
        title_row.addStretch()
        cfg_layout.addLayout(title_row)

        # Include options
        self._opt_metadata = QCheckBox("Include Platform Metadata")
        self._opt_metadata.setChecked(True)
        cfg_layout.addWidget(self._opt_metadata)

        self._opt_benchmark = QCheckBox("Include Benchmark Results")
        cfg_layout.addWidget(self._opt_benchmark)

        self._opt_events = QCheckBox("Include Event Summary")
        cfg_layout.addWidget(self._opt_events)

        self._opt_fpga = QCheckBox("Include FPGA Information")
        cfg_layout.addWidget(self._opt_fpga)

        # Generate button
        gen_btn = QPushButton("📄 Generate Report (PDF + CSV + JSON)")
        gen_btn.setObjectName("primaryBtn")
        gen_btn.clicked.connect(self._generate_report)
        cfg_layout.addWidget(gen_btn)

        layout.addWidget(config_panel)

        # History
        hist_panel = Panel("Report History")
        h_layout = hist_panel._layout

        self._history_list = QGroupBox("Generated Reports")
        hist_scroll = QScrollArea()
        hist_scroll.setWidgetResizable(True)
        hist_scroll.setFrameShape(QFrame.NoFrame)
        self._history_container = QWidget()
        self._history_layout = QVBoxLayout(self._history_container)
        self._history_layout.setContentsMargins(4, 4, 4, 4)
        self._history_layout.setSpacing(4)
        self._history_layout.addStretch()
        hist_scroll.setWidget(self._history_container)
        self._history_list.setLayout(QVBoxLayout())
        self._history_list.layout().addWidget(hist_scroll)
        h_layout.addWidget(self._history_list, 1)

        layout.addWidget(hist_panel, 1)

        self._refresh_history()

    def _generate_report(self):
        """Generate report."""
        config = ReportConfig(
            report_type=self._report_type.currentText(),
            title=self._report_title.text(),
            include_metadata=self._opt_metadata.isChecked(),
            include_benchmark=self._opt_benchmark.isChecked(),
            include_events=self._opt_events.isChecked(),
            include_fpga=self._opt_fpga.isChecked(),
        )

        paths = self._report_gen.generate(config)

        if paths:
            for fmt, path in paths.items():
                self._main._event_mgr.emit(
                    'system', 'info',
                    f'Report generated ({fmt.upper()}): {os.path.basename(path)}'
                )
            self._refresh_history()
        else:
            self._main._event_mgr.emit(
                'system', 'error',
                'Report generation failed - check logs'
            )

    def _refresh_history(self):
        """Refresh report history."""
        # Clear existing widgets (but keep the stretch)
        while self._history_layout.count() > 1:  # keep last stretch
            item = self._history_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        reports = self._main._db.query(
            "SELECT * FROM report_history ORDER BY created_at DESC LIMIT 20"
        )

        for r in reports:
            row = QFrame()
            row.setStyleSheet(
                f"background: {T.BG_GRAPHITE}; border: 1px solid {T.BORDER_SUBTLE}; "
                f"border-radius: {T.RADIUS_MD}px; padding: 6px; margin: 2px 0;"
            )
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(8, 6, 8, 6)

            type_lbl = StatusBadge(r['report_type'], "info")
            row_layout.addWidget(type_lbl)

            title_lbl = QLabel(r['title'])
            title_lbl.setObjectName("metricLabel")
            title_lbl.setWordWrap(True)
            row_layout.addWidget(title_lbl)

            time_lbl = QLabel(r['created_at'][:19])
            time_lbl.setObjectName("metricLabel")
            row_layout.addWidget(time_lbl)

            open_btn = QPushButton("Open")
            open_btn.setMaximumWidth(60)
            open_btn.clicked.connect(
                lambda checked, p=r['file_path']: self._open_report(p)
            )
            row_layout.addWidget(open_btn)

            self._history_layout.insertWidget(
                self._history_layout.count() - 1, row
            )

        if not reports:
            lbl = QLabel("No reports generated yet")
            lbl.setObjectName("metricLabel")
            self._history_layout.insertWidget(
                self._history_layout.count() - 1, lbl
            )

    def _open_report(self, path: str):
        """Open report file."""
        if path and os.path.exists(path):
            import subprocess
            try:
                if os.name == 'nt':
                    os.startfile(path)
                else:
                    subprocess.run(['xdg-open', path])
            except Exception:
                self._main._event_mgr.emit(
                    'system', 'warning',
                    f'Could not open report: {path}'
                )

    def update_telemetry(self, data: dict):
        pass
