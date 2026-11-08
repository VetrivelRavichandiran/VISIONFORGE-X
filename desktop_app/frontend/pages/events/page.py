"""VISIONFORGE X - Event Intelligence Page (Enhanced)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QScrollArea, QGroupBox, QComboBox, QFileDialog,
    QTableWidget, QTableWidgetItem, QCheckBox, QLineEdit, QSplitter,
    QHeaderView
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFont

from frontend.components.widgets import Panel, MetricTile, StatusBadge
from frontend.design_system.tokens import DesignTokens as T


class EventIntelligencePage(QWidget):
    """Event management and search - Enhanced."""

    def __init__(self, main_window):
        super().__init__()
        self._main = main_window
        self._event_mgr = main_window._event_mgr

        self._setup_ui()
        self._refresh_events()

        # Auto-refresh
        self._timer = QTimer()
        self._timer.timeout.connect(self._refresh_events)
        self._timer.start(5000)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(T.SPACING_LG, T.SPACING_LG, T.SPACING_LG, T.SPACING_LG)
        layout.setSpacing(T.SPACING_MD)

        title = QLabel("📋 Event Intelligence")
        title.setStyleSheet(
            f"color: {T.ACCENT_CYAN}; font-size: {T.FONT_SIZE_HERO}px; "
            f"font-weight: 800; letter-spacing: 1px;"
        )
        layout.addWidget(title)

        # Filters
        filters = QHBoxLayout()

        filters.addWidget(QLabel("Category:"))
        self._cat_filter = QComboBox()
        self._cat_filter.addItems(["All", "device", "camera", "processing", "pipeline",
                                    "ai", "motion", "anomaly", "benchmark", "error", "system"])
        self._cat_filter.currentTextChanged.connect(self._refresh_events)
        filters.addWidget(self._cat_filter)

        filters.addWidget(QLabel("Severity:"))
        self._sev_filter = QComboBox()
        self._sev_filter.addItems(["All", "info", "warning", "error", "critical"])
        self._sev_filter.currentTextChanged.connect(self._refresh_events)
        filters.addWidget(self._sev_filter)

        filters.addWidget(QLabel("Search:"))
        self._search_box = QLineEdit()
        self._search_box.setPlaceholderText("Filter events...")
        self._search_box.textChanged.connect(self._refresh_events)
        self._search_box.setMaximumWidth(200)
        filters.addWidget(self._search_box)

        filters.addStretch()

        ack_btn = QPushButton("✓ Acknowledge Selected")
        ack_btn.clicked.connect(self._acknowledge_selected)
        filters.addWidget(ack_btn)

        clear_btn = QPushButton("🗑 Clear")
        clear_btn.clicked.connect(self._clear_events)
        filters.addWidget(clear_btn)

        export_btn = QPushButton("📤 Export")
        export_btn.clicked.connect(self._export_events)
        filters.addWidget(export_btn)

        layout.addLayout(filters)

        # Stats row
        stats = QHBoxLayout()
        self._total_tile = MetricTile("Total Events", "0", "", "info")
        self._unread_tile = MetricTile("Unacknowledged", "0", "", "warn")
        self._error_tile = MetricTile("Errors", "0", "", "error")
        stats.addWidget(self._total_tile)
        stats.addWidget(self._unread_tile)
        stats.addWidget(self._error_tile)
        stats.addStretch()
        layout.addLayout(stats)

        # Event table
        table_panel = Panel("Event Log")
        table_layout = table_panel._layout

        self._event_table = QTableWidget(0, 6)
        self._event_table.setHorizontalHeaderLabels(
            ["ID", "Timestamp", "Category", "Severity", "Description", "Status"]
        )
        self._event_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self._event_table.setSelectionBehavior(QTableWidget.SelectRows)
        self._event_table.setEditTriggers(QTableWidget.NoEditTriggers)
        table_layout.addWidget(self._event_table)
        layout.addWidget(table_panel, 1)

    def _refresh_events(self):
        """Refresh event table."""
        category = self._cat_filter.currentText()
        category = None if category == "All" else category
        severity = self._sev_filter.currentText()
        severity = None if severity == "All" else severity

        events = self._event_mgr.get_events(
            category=category, severity=severity, limit=500
        )

        # Apply search filter
        search = self._search_box.text().lower()
        if search:
            events = [e for e in events if search in e.description.lower()]

        self._event_table.setRowCount(0)
        for event in events:
            row = self._event_table.rowCount()
            self._event_table.insertRow(row)
            self._event_table.setItem(row, 0, QTableWidgetItem(event.id))
            self._event_table.setItem(row, 1, QTableWidgetItem(event.timestamp[:19]))
            self._event_table.setItem(row, 2, QTableWidgetItem(event.category))

            # Severity with color
            sev_item = QTableWidgetItem(event.severity)
            sev_colors = {
                'critical': QColor(T.STATUS_RED),
                'error': QColor(T.STATUS_RED),
                'warning': QColor(T.STATUS_AMBER),
                'info': QColor(T.ACCENT_CYAN),
                'debug': QColor(T.TEXT_MUTED),
            }
            sev_item.setForeground(sev_colors.get(event.severity, QColor(T.TEXT_PRIMARY)))
            self._event_table.setItem(row, 3, sev_item)

            self._event_table.setItem(row, 4, QTableWidgetItem(event.description))

            status = "Ack" if event.acknowledged else "New"
            status_item = QTableWidgetItem(status)
            if event.acknowledged:
                status_item.setForeground(QColor(T.STATUS_GREEN))
            else:
                status_item.setForeground(QColor(T.STATUS_AMBER))
            self._event_table.setItem(row, 5, status_item)

        # Update stats
        all_events = self._event_mgr.get_events(limit=10000)
        self._total_tile.set_value(str(len(all_events)))
        unread = [e for e in all_events if not e.acknowledged]
        self._unread_tile.set_value(str(len(unread)))
        errors = [e for e in all_events if e.severity in ('error', 'critical')]
        self._error_tile.set_value(str(len(errors)))

    def _acknowledge_selected(self):
        """Acknowledge selected events."""
        rows = self._event_table.selectionModel().selectedRows()
        for idx in rows:
            event_id = self._event_table.item(idx.row(), 0).text()
            self._event_mgr.acknowledge(event_id)
        self._refresh_events()

    def _clear_events(self):
        """Clear all events."""
        self._event_mgr.clear()
        self._refresh_events()

    def _export_events(self):
        """Export events to CSV."""
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Events", "events.csv", "CSV (*.csv);;JSON (*.json)")
        if path:
            import csv, json
            events = self._event_mgr.get_events(limit=10000)
            if path.endswith('.json'):
                with open(path, 'w') as f:
                    json.dump([e.to_dict() for e in events], f, indent=2)
            else:
                with open(path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['ID', 'Timestamp', 'Category', 'Severity',
                                     'Description', 'Acknowledged'])
                    for e in events:
                        writer.writerow([e.id, e.timestamp, e.category, e.severity,
                                         e.description, e.acknowledged])
            self._main._event_mgr.emit(
                'system', 'info', f'Events exported: {len(events)} records'
            )

    def update_telemetry(self, data: dict):
        pass
