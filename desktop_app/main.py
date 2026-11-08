"""VISIONFORGE X - Main Application Entry Point."""
import sys
import os
import logging

# Ensure project root is in path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from frontend.main_window import MainWindow


def setup_logging():
    """Configure application logging."""
    log_dir = os.path.join(project_root, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'visionforge.log')

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )


def main():
    """Application entry point."""
    setup_logging()
    logger = logging.getLogger(__name__)

    app = QApplication(sys.argv)
    # High DPI scaling is enabled by default in Qt 6.x; these attributes are deprecated
    app.setApplicationName("VISIONFORGE X")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("VisionForge")

    try:
        window = MainWindow()
        window.show()
        logger.info("VISIONFORGE X started successfully")
        sys.exit(app.exec())
    except Exception as e:
        logger.error(f"Application startup failed: {e}", exc_info=True)
        # Show error dialog
        from PySide6.QtWidgets import QMessageBox
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("VISIONFORGE X - Startup Error")
        msg.setText(f"Failed to start application: {e}")
        msg.setDetailedText("Check logs/visionforge.log for details.")
        msg.exec()
        sys.exit(1)


if __name__ == "__main__":
    main()
