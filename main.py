#!/usr/bin/env python3
"""
RS485 Stepper Motor Controller - Main Application
Entry point for the RS485 stepper motor control software
"""

import sys
import os
import logging
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
    try:
        # Setup application
        app = setup_application()

        # Create and show main window
        window = RS485StepperMotorGUI()
        window.setWindowTitle(WINDOW_TITLE)
        window.show()

        # Start application event loop
        sys.exit(app.exec_())

    except Exception as e:
        print(f"Application error: {str(e)}")
        logging.exception("Application error occurred")
        sys.exit(1)


if __name__ == "__main__":
    main()