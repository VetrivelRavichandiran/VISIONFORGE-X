"""VISIONFORGE X - Performance Laboratory Page (Enhanced)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QScrollArea, QGroupBox, QComboBox, QFileDialog,
    QTableWidget, QTableWidgetItem, QProgressBar, QSpinBox, QCheckBox
)
from PySide6.QtCore import Qt, QTimer
import numpy as np

from frontend.components.widgets import Panel, MetricTile, StatusBadge, GlowProgressBar
from frontend.design_system.tokens import DesignTokens as T


class PerformanceLabPage(QWidget):
    """Performance benchmarking and analysis - Enhanced."""

    def __init__(self, main_window):
        super().__init__()
        self._main = main_window
        self._benchmark = main_window._benchmark
        self._session_counter = 0

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(T.SPACING_LG, T.SPACING_LG, T.SPACING_LG, T.SPACING_LG)
        layout.setSpacing(T.SPACING_MD)

        title = QLabel("📊 Performance Laboratory")
        title.setStyleSheet(
            f"color: {T.ACCENT_CYAN}; font-size: {T.FONT_SIZE_HERO}px; "
            f"font-weight: 800; letter-spacing: 1px;"
        )
        layout.addWidget(title)

        # Benchmark controls
        ctrl = QHBoxLayout()

        ctrl.addWidget(QLabel("Benchmark:"))
        self._bench_name = QLabel("Live Performance")
        self._bench_name.setObjectName("metricValue")
        self._bench_name.setStyleSheet(f"color: {T.ACCENT_CYAN};")
        ctrl.addWidget(self._bench_name)

        ctrl.addSpacing(10)
        start_btn = QPushButton("▶ Start Benchmark")
        start_btn.setObjectName("primaryBtn")
        start_btn.clicked.connect(self._start_benchmark)
        ctrl.addWidget(start_btn)

        stop_btn = QPushButton("⏹ Stop")
        stop_btn.setObjectName("dangerBtn")
        stop_btn.setEnabled(False)
        stop_btn.clicked.connect(self._stop_benchmark)
        ctrl.addWidget(stop_btn)
        self._stop_btn = stop_btn

        ctrl.addStretch()

        export_btn = QPushButton("📊 Export Results")
        export_btn.clicked.connect(self._export_results)
        ctrl.addWidget(export_btn)

        layout.addLayout(ctrl)

        # Live metrics
        metrics_panel = Panel("Live Performance Metrics")
        m_grid = QGridLayout()

        self._fps_tile = MetricTile("FPS", "—", "fps", "info")
        self._avg_lat_tile = MetricTile("Avg Latency", "—", "ms", "info")
        self._min_lat_tile = MetricTile("Min Latency", "—", "ms", "info")
        self._max_lat_tile = MetricTile("Max Latency", "—", "ms", "info")
        self._p95_lat_tile = MetricTile("P95 Latency", "—", "ms", "info")
        self._throughput_tile = MetricTile("Throughput", "—", "MB/s", "info")
        self._dropped_tile = MetricTile("Dropped Frames", "0", "", "info")
        self._total_tile = MetricTile("Total Frames", "0", "", "info")

        m_grid.addWidget(self._fps_tile, 0, 0)
        m_grid.addWidget(self._avg_lat_tile, 0, 1)
        m_grid.addWidget(self._min_lat_tile, 0, 2)
        m_grid.addWidget(self._max_lat_tile, 1, 0)
        m_grid.addWidget(self._p95_lat_tile, 1, 1)
        m_grid.addWidget(self._throughput_tile, 1, 2)
        m_grid.addWidget(self._dropped_tile, 2, 0)
        m_grid.addWidget(self._total_tile, 2, 1)
        metrics_panel.addLayout(m_grid)
        layout.addWidget(metrics_panel)

        # CPU/Memory
        sys_panel = Panel("System Resources")
        s_grid = QGridLayout()

        self._cpu_bar = GlowProgressBar(color=T.ACCENT_CYAN)
        self._cpu_bar.setRange(0, 100)
        s_grid.addWidget(QLabel("CPU Usage:"), 0, 0)
        s_grid.addWidget(self._cpu_bar, 0, 1)

        self._mem_bar = GlowProgressBar(color=T.ACCENT_TEAL)
        self._mem_bar.setRange(0, 100)
        s_grid.addWidget(QLabel("Memory Usage:"), 1, 0)
        s_grid.addWidget(self._mem_bar, 1, 1)

        self._ai_tile = MetricTile("AI Inference", "—", "ms", "ai")
        s_grid.addWidget(self._ai_tile, 2, 0, 1, 2)

        sys_panel.addLayout(s_grid)
        layout.addWidget(sys_panel)

        # Session history
        hist_panel = Panel("Benchmark Session History")
        h_layout = hist_panel._layout

        self._session_table = QTableWidget(0, 7)
        self._session_table.setHorizontalHeaderLabels(
            ["ID", "Name", "Mode", "Duration", "Avg FPS", "Avg Latency", "Actions"]
        )
        h_layout.addWidget(self._session_table)
        hist_panel.addLayout(h_layout)
        layout.addWidget(hist_panel, 1)

        # Comparison
        self._refresh_sessions()

    def _start_benchmark(self):
        """Start a benchmark session."""
        self._session_counter += 1
        name = f"Session {self._session_counter}"
        mode = "simulation" if self._main._simulated else "hardware"
        self._benchmark.start(name, {'resolution': '640x480'}, mode)
        self._stop_btn.setEnabled(True)
        self._main._event_mgr.emit('benchmark', 'info', f'Benchmark started: {name}')

    def _stop_benchmark(self):
        """Stop benchmark session."""
        session = self._benchmark.stop()
        if session:
            self._refresh_sessions()
        self._stop_btn.setEnabled(False)
        self._main._event_mgr.emit('benchmark', 'info', 'Benchmark stopped')

    def _refresh_sessions(self):
        """Refresh session history table."""
        self._session_table.setRowCount(0)
        for s in self._benchmark.get_sessions():
            row = self._session_table.rowCount()
            self._session_table.insertRow(row)
            self._session_table.setItem(row, 0, QTableWidgetItem(str(s.id)))
            self._session_table.setItem(row, 1, QTableWidgetItem(s.name))
            self._session_table.setItem(row, 2, QTableWidgetItem(s.mode))
            dur = "—"
            if s.ended_at:
                from datetime import datetime
                start = datetime.fromisoformat(s.started_at)
                end = datetime.fromisoformat(s.ended_at)
                dur = f"{(end - start).total_seconds():.1f}s"
            self._session_table.setItem(row, 3, QTableWidgetItem(dur))

            # Metrics
            metrics = s.metrics
            fps_vals = metrics.get('fps', [])
            lat_vals = metrics.get('latency_ms', [])
            avg_fps = f"{np.mean(fps_vals):.1f}" if fps_vals else "—"
            avg_lat = f"{np.mean(lat_vals):.1f}" if lat_vals else "—"
            self._session_table.setItem(row, 4, QTableWidgetItem(avg_fps))
            self._session_table.setItem(row, 5, QTableWidgetItem(avg_lat))

            # Mode indicator
            mode_item = QTableWidgetItem("SIM" if s.is_simulated else "HW")
            mode_item.setForeground(QColor(T.ACCENT_CYAN if s.is_simulated else T.ACCENT_VIOLET))
            self._session_table.setItem(row, 6, mode_item)

    def _export_results(self):
        """Export benchmark results."""
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Results", "benchmark_results.csv", "CSV (*.csv);;JSON (*.json)")
        if path:
            import json, csv
            sessions = self._benchmark.get_sessions()
            if path.endswith('.json'):
                data = [self._benchmark._summarize(s) for s in sessions]
                with open(path, 'w') as f:
                    json.dump(data, f, indent=2, default=str)
            else:
                with open(path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Session', 'Mode', 'Metric', 'Avg', 'Min', 'Max', 'P95'])
                    for s in sessions:
                        summary = self._benchmark._summarize(s)
                        for metric, vals in summary.get('metrics', {}).items():
                            if isinstance(vals, dict):
                                writer.writerow([
                                    summary['name'], summary['mode'], metric,
                                    vals.get('avg', 0), vals.get('min', 0),
                                    vals.get('max', 0), vals.get('p95', 0)
                                ])
            self._main._event_mgr.emit('benchmark', 'info', f'Results exported: {os.path.basename(path)}')

    def update_telemetry(self, data: dict):
        """Update live performance metrics."""
        perf = self._main._perf
        fps = perf.get_current_fps()
        lat_stats = perf.get_latency_stats()

        self._fps_tile.set_value(f"{fps:.1f}")
        self._avg_lat_tile.set_value(f"{lat_stats['avg']:.1f}")
        self._min_lat_tile.set_value(f"{lat_stats['min']:.1f}")
        self._max_lat_tile.set_value(f"{lat_stats['max']:.1f}")
        self._p95_lat_tile.set_value(f"{lat_stats['p95']:.1f}")
        self._dropped_tile.set_value(str(perf.get_dropped_frames()))
        self._total_tile.set_value(str(perf.get_total_frames()))

        # Throughput
        res = "640x480"
        bytes_per_frame = 640 * 480 * 3
        throughput = (fps * bytes_per_frame) / (1024 * 1024)
        self._throughput_tile.set_value(f"{throughput:.1f}")

        # System resources
        self._cpu_bar.setValue(int(data.get('cpu_usage', 30)))
        self._mem_bar.setValue(int(data.get('memory_usage', 40)))
        self._ai_tile.set_value(f"{data.get('ai_inference_ms', 0):.1f}")

        # Record benchmark metrics if running
        if self._benchmark.is_running():
            self._benchmark.record_metric('fps', fps)
            self._benchmark.record_metric('latency_ms', data.get('latency_ms', 0))
            self._benchmark.record_metric('cpu_usage', data.get('cpu_usage', 0))
            self._benchmark.record_metric('memory_usage', data.get('memory_usage', 0))
