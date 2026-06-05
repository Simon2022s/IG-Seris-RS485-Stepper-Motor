#!/usr/bin/env python3
"""
RS485 Stepper Motor Controller - Main Application
Entry point for the RS485 stepper motor control software
"""

import sys
import os
import logging

# 配置日志（在导入其他模块前配置）
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from gui import RS485StepperMotorGUI
from config import WINDOW_TITLE, DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZE


def setup_application():
    """Setup application configuration"""
    # Set application attributes for high DPI support
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    # Create application instance
    app = QApplication(sys.argv)

    # Set application-wide font
    font = QFont(DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZE)
    app.setFont(font)

    return app


def main():
    """Main application entry point"""
    logger = logging.getLogger(__name__)

    try:
        logger.info("Starting RS485 Stepper Motor Controller")

        # Setup application
        app = setup_application()

        # Create and show main window
        window = RS485StepperMotorGUI()
        window.setWindowTitle(WINDOW_TITLE)
        window.show()

        logger.info("Application initialized successfully")

        # Start application event loop
        sys.exit(app.exec_())

    except Exception as e:
        logger.exception(f"Application error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()