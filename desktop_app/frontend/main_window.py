"""VISIONFORGE X - Main Application Window."""
import sys
import os
import logging
import threading
import time
import numpy as np

# Add desktop_app root to path for imports
_app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _app_dir not in sys.path:
    sys.path.insert(0, _app_dir)

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QSplitter, QFrame, QLabel, QApplication, QFileDialog, QSystemTrayIcon
)
from PySide6.QtCore import Qt, QTimer, Signal, QThread
from PySide6.QtGui import QImage
from PySide6.QtGui import QIcon, QPixmap, QColor, QPainter

from frontend.design_system.tokens import DesignTokens as T, apply_dark_stylesheet
from frontend.navigation import NavigationRail
from frontend.components.topbar import TopBar
from frontend.components.widgets import Panel, MetricTile, StatusBadge, CameraView

# Backend imports
from config.settings import SettingsManager
from adapters.base_device import create_device, ConnectionState
from backend.storage.database import DatabaseManager
from backend.events.manager import EventManager
from backend.vision.engine import VisionEngine, ExecutionSource
from backend.vision.motion import MotionAnalyzer
from backend.ai.registry import ModelRegistry
from backend.adaptive.controller import AdaptiveController, SystemMetrics
from backend.pipeline.engine import PipelineEngine
from backend.analytics.benchmark import PerformanceTracker, BenchmarkRunner
from backend.reports.generator import ReportGenerator, ReportConfig

logger = logging.getLogger(__name__)


class FrameWorker(QThread):
    """Worker thread for frame processing."""
    frame_ready = Signal(object, object, float)  # original, processed, processing_time
    telemetry_update = Signal(dict)

    def __init__(self, device, vision_engine, motion_analyzer,
                 pipeline_engine, perf_tracker, event_mgr, config=None):
        super().__init__()
        self._device = device
        self._vision = vision_engine
        self._motion = motion_analyzer
        self._pipeline = pipeline_engine
        self._perf = perf_tracker
        self._event_mgr = event_mgr
        self._config = config or {}
        self._running = False
        self._frame_count = 0
        self._simulated = True

    def run(self):
        self._running = True
        import cv2

        while self._running:
            try:
                if not self._device or not self._device.is_connected():
                    time.sleep(0.1)
                    continue

                self._frame_count += 1

                if self._simulated:
                    # Generate simulated frame
                    frame, seq = self._device.generate_frame(640, 480)
                    original = frame.copy()
                else:
                    original = None

                # Vision processing
                t0 = time.perf_counter()
                if self._simulated:
                    result = self._vision.process(frame)
                    processed = result['output']
                    proc_time = result['total_time_ms']
                else:
                    processed = original.copy() if original is not None else frame
                    proc_time = 0

                # Motion analysis
                motion_result = {}
                if self._motion:
                    motion_result = self._motion.analyze(processed)
                    proc_time += motion_result.get('processing_time_ms', 0)

                elapsed = (time.perf_counter() - t0) * 1000

                # Record performance
                self._perf.record_frame(proc_time, cpu=25, memory=40)

                # Generate telemetry
                fps = self._perf.get_current_fps()
                latency = self._perf.get_avg_latency()
                telemetry = {
                    'timestamp': time.time(),
                    'device_name': self._device.status.device_name if self._device else 'N/A',
                    'processing_fps': round(fps, 1),
                    'latency_ms': round(latency, 1),
                    'dropped_frames': self._perf.get_dropped_frames(),
                    'cpu_usage': 25 + np.random.uniform(0, 20),
                    'memory_usage': 40 + np.random.uniform(0, 20),
                    'motion_intensity': motion_result.get('motion_intensity', 0),
                    'anomaly_score': np.random.uniform(0, 0.3),
                    'ai_inference_ms': 30 + np.random.uniform(0, 15),
                    'pipeline_active': True,
                    'dma_status': 'running',
                }

                # Store as BGR for OpenCV compatibility
                if len(processed.shape) == 2:
                    processed_bgr = cv2.cvtColor(processed, cv2.COLOR_GRAY2BGR)
                else:
                    processed_bgr = processed

                self.frame_ready.emit(original, processed_bgr, proc_time)
                self.telemetry_update.emit(telemetry)

                # Small sleep to control FPS
                time.sleep(0.01)

            except Exception as e:
                logger.error(f"Frame worker error: {e}")
                time.sleep(0.1)

    def stop(self):
        self._running = False
        self.wait(2000)


class MainWindow(QMainWindow):
    """Main application window with all 12 pages."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("VISIONFORGE X — Universal Adaptive Edge Vision Intelligence Platform")
        self.setMinimumSize(1280, 800)
        self.resize(1440, 900)

        # Initialize backend components
        self._settings = SettingsManager()
        self._settings.load()
        self._db = DatabaseManager(self._settings.config.storage.db_path)
        self._event_mgr = EventManager(self._db)
        self._device = None
        self._vision = VisionEngine(ExecutionSource.SIMULATION)
        self._motion = MotionAnalyzer()
        self._pipeline = PipelineEngine()
        self._perf = PerformanceTracker()
        self._benchmark = BenchmarkRunner(self._db, self._event_mgr)
        self._model_registry = ModelRegistry(self._db)
        self._adaptive = AdaptiveController()
        self._report_gen = ReportGenerator(self._db, self._event_mgr, self._benchmark)
        self._frame_worker = None

        # Page references for cross-page communication
        self._pages = {}

        self._setup_ui()
        self._setup_pages()
        self._apply_stylesheet()
        self._connect_signals()

        logger.info("VISIONFORGE X initialized")

    def _setup_ui(self):
        """Set up main UI layout."""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Top bar
        self._topbar = TopBar()
        main_layout.addWidget(self._topbar)

        # Main content with navigation
        content = QWidget()
        content.setStyleSheet(f"background: {T.BG_OBSIDIAN};")
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Navigation rail
        self._nav = NavigationRail()
        content_layout.addWidget(self._nav)

        # Page stack with subtle background
        self._page_stack = QStackedWidget()
        self._page_stack.setStyleSheet(
            f"background: {T.BG_OBSIDIAN}; border: none;"
        )
        content_layout.addWidget(self._page_stack, 1)

        main_layout.addWidget(content, 1)

    def _apply_stylesheet(self):
        """Apply dark industrial stylesheet."""
        from PySide6.QtWidgets import QApplication
        apply_dark_stylesheet(QApplication.instance())

    def _setup_pages(self):
        """Create and register all 12 pages."""
        from frontend.pages.command_center.page import CommandCenterPage
        from frontend.pages.vision_studio.page import VisionStudioPage
        from frontend.pages.ai_lab.page import AILabPage
        from frontend.pages.motion.page import MotionIntelligencePage
        from frontend.pages.anomaly.page import AnomalyLabPage
        from frontend.pages.pipeline.page import PipelineArchitectPage
        from frontend.pages.fpga_monitor.page import FPGAMonitorPage
        from frontend.pages.performance.page import PerformanceLabPage
        from frontend.pages.datasets.page import DatasetExplorerPage
        from frontend.pages.events.page import EventIntelligencePage
        from frontend.pages.reports.page import ResearchReportsPage
        from frontend.pages.settings.page import SystemConfigPage

        page_classes = [
            ("command_center", CommandCenterPage),
            ("vision_studio", VisionStudioPage),
            ("ai_lab", AILabPage),
            ("motion", MotionIntelligencePage),
            ("anomaly", AnomalyLabPage),
            ("pipeline", PipelineArchitectPage),
            ("fpga_monitor", FPGAMonitorPage),
            ("performance", PerformanceLabPage),
            ("datasets", DatasetExplorerPage),
            ("events", EventIntelligencePage),
            ("reports", ResearchReportsPage),
            ("settings", SystemConfigPage),
        ]

        for key, cls in page_classes:
            page = cls(self)
            self._page_stack.addWidget(page)
            self._pages[key] = page

        # Set initial page
        self._nav.set_current("command_center")

    def _connect_signals(self):
        """Connect UI signals."""
        self._nav.page_changed.connect(self._switch_page)
        self._topbar.connect_clicked.connect(self._connect_device)
        self._topbar.disconnect_clicked.connect(self._disconnect_device)
        self._topbar.start_clicked.connect(self._start_processing)
        self._topbar.stop_clicked.connect(self._stop_processing)
        self._topbar.mode_changed.connect(self._on_mode_changed)

    def _switch_page(self, key: str):
        """Switch to a different page."""
        if key in self._pages:
            idx = list(self._pages.keys()).index(key)
            self._page_stack.setCurrentIndex(idx)

    def _connect_device(self):
        """Connect to device (simulation or hardware)."""
        config = {
            'mode': self._settings.config.device.mode,
            'board_ip': self._settings.config.device.board_ip,
            'tcp_port': self._settings.config.device.tcp_port,
            'udp_port': self._settings.config.device.udp_port,
        }
        self._device = create_device(config)
        self._device.on('telemetry', self._on_telemetry)
        self._device.on('event', self._on_device_event)
        self._device.on('state_change', self._on_state_change)

        if self._device.connect():
            self._topbar.set_connected(True, self._device.status.device_name)
            self._topbar.set_simulated(self._device.status.is_simulated)
            self._simulated = self._device.status.is_simulated
            self._event_mgr.emit('device', 'info',
                                 f'Device connected: {self._device.status.device_name}')
            self._start_frame_worker()
        else:
            self._event_mgr.emit('device', 'error',
                                 'Device connection failed')

    def _disconnect_device(self):
        """Disconnect from device."""
        self._stop_frame_worker()
        if self._device:
            self._device.disconnect()
            self._topbar.set_connected(False)
            self._event_mgr.emit('device', 'info', 'Device disconnected')

    def _start_processing(self):
        """Start camera and processing."""
        if self._device:
            self._device.start_camera()
            self._device.start_processing()
            self._device.set_processing_mode(
                self._settings.config.camera.processing_mode
            )
            self._topbar.set_processing(True)
            self._event_mgr.emit('processing', 'info', 'Processing started')

    def _stop_processing(self):
        """Stop camera and processing."""
        if self._device:
            self._device.stop_camera()
            self._device.stop_processing()
            self._topbar.set_processing(False)
            self._event_mgr.emit('processing', 'info', 'Processing stopped')

    def _on_mode_changed(self, mode: str):
        """Handle processing mode change."""
        self._settings.config.camera.processing_mode = mode
        if self._device:
            self._device.set_processing_mode(mode)
        self._adaptive.set_mode(mode)

    def _start_frame_worker(self):
        """Start the frame processing worker thread."""
        self._frame_worker = FrameWorker(
            self._device, self._vision, self._motion,
            self._pipeline, self._perf, self._event_mgr,
            {'simulated': self._simulated}
        )
        self._frame_worker._simulated = self._simulated
        self._frame_worker.frame_ready.connect(self._on_frame_ready)
        self._frame_worker.telemetry_update.connect(self._on_telemetry)
        self._frame_worker.start()

    def _stop_frame_worker(self):
        """Stop the frame processing worker."""
        if self._frame_worker:
            self._frame_worker.stop()
            self._frame_worker = None

    def _on_frame_ready(self, original, processed, proc_time):
        """Handle new frame from worker."""
        # Update command center
        if 'command_center' in self._pages:
            self._pages['command_center'].update_frames(original, processed, proc_time)

    def _on_telemetry(self, data: dict):
        """Handle telemetry update."""
        # Persist to database
        self._db.insert_telemetry(data, is_simulated=self._simulated)

        # Update all pages that need telemetry
        for page_key, page in self._pages.items():
            if hasattr(page, 'update_telemetry'):
                try:
                    page.update_telemetry(data)
                except Exception:
                    pass

    def _on_device_event(self, event: dict):
        """Handle device event."""
        self._event_mgr.emit(
            event.get('category', 'system'),
            event.get('severity', 'info'),
            event.get('description', ''),
            data=event.get('data', {})
        )

    def _on_state_change(self, state: dict):
        """Handle device state change."""
        pass

    def get_pages(self) -> dict:
        return self._pages

    def closeEvent(self, event):
        """Handle window close."""
        self._stop_frame_worker()
        if self._device:
            self._device.disconnect()
        self._settings.save()
        self._db.close()
        event.accept()
