"""
Serial Setup Dialog for RS485 Stepper Motor Controller
"""

import sys
import os
import serial.tools.list_ports
from PyQt5.QtWidgets import (
    QDialog, QWidget, QGroupBox, QVBoxLayout, QHBoxLayout,
    QFormLayout, QLabel, QComboBox, QPushButton, QMessageBox
)
from PyQt5.QtCore import Qt
from config import BAUDRATE_OPTIONS, DEFAULT_BAUDRATE


class SerialSetupDialog(QDialog):
    """Serial Setup Dialog Window"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Serial Setup")
        self.setFixedSize(320, 300)
        self.setup_ui()
        self.refresh_ports()

    def setup_ui(self):
        """Setup the dialog UI"""
        # Main layout
        main_layout = QVBoxLayout(self)

        # Serial configuration group
        serial_group = QGroupBox("Serial Configuration")
        serial_group.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 1px solid #00a1cb;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 15px;
                font-size: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #00a1cb;
            }
        """)

        serial_layout = QFormLayout()
        serial_layout.setSpacing(10)

        # Port selection
        self.port_combo = QComboBox()
        self.port_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                border: 1px solid #00a1cb;
                border-radius: 4px;
                padding: 2px 8px;
                min-height: 25px;
            }
        """)

        self.refresh_btn = QPushButton("🔄")
        self.refresh_btn.setFixedWidth(40)
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #00a1cb;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #008fb3;
            }
        """)
        self.refresh_btn.clicked.connect(self.refresh_ports)

        port_layout = QHBoxLayout()
        port_layout.addWidget(self.port_combo)
        port_layout.addWidget(self.refresh_btn)

        # Baud rate selection
        self.baud_combo = QComboBox()
        for baud in BAUDRATE_OPTIONS:
            self.baud_combo.addItem(str(baud), baud)
        self.baud_combo.setCurrentText(str(DEFAULT_BAUDRATE))
        self.baud_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                border: 1px solid #00a1cb;
                border-radius: 4px;
                padding: 2px 8px;
                min-height: 25px;
            }
        """)

        # Data bits
        self.databits_combo = QComboBox()
        self.databits_combo.addItems(['5', '6', '7', '8'])
        self.databits_combo.setCurrentText('8')
        self.databits_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                border: 1px solid #00a1cb;
                border-radius: 4px;
                padding: 2px 8px;
                min-height: 25px;
            }
        """)

        # Parity
        self.parity_combo = QComboBox()
        self.parity_combo.addItems(['None', 'Even', 'Odd', 'Mark', 'Space'])
        self.parity_combo.setCurrentText('None')
        self.parity_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                border: 1px solid #00a1cb;
                border-radius: 4px;
                padding: 2px 8px;
                min-height: 25px;
            }
        """)

        # Stop bits
        self.stopbits_combo = QComboBox()
        self.stopbits_combo.addItems(['1', '1.5', '2'])
        self.stopbits_combo.setCurrentText('1')
        self.stopbits_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                border: 1px solid #00a1cb;
                border-radius: 4px;
                padding: 2px 8px;
                min-height: 25px;
            }
        """)

        # Add rows to form
        serial_layout.addRow("Port:", port_layout)
        serial_layout.addRow("Baud Rate:", self.baud_combo)
        serial_layout.addRow("Data Bits:", self.databits_combo)
        serial_layout.addRow("Parity:", self.parity_combo)
        serial_layout.addRow("Stop Bits:", self.stopbits_combo)

        serial_group.setLayout(serial_layout)
        main_layout.addWidget(serial_group)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.ok_btn = QPushButton("OK")
        self.ok_btn.setFixedWidth(80)
        self.ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #00a1cb;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #008fb3;
            }
        """)
        self.ok_btn.clicked.connect(self.accept)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setFixedWidth(80)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        self.cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(self.ok_btn)
        button_layout.addWidget(self.cancel_btn)
        main_layout.addLayout(button_layout)

    def refresh_ports(self):
        """Refresh available COM ports"""
        self.port_combo.clear()

        # Get available ports
        ports = serial.tools.list_ports.comports()

        if not ports:
            self.port_combo.addItem("No COM ports found")
            self.port_combo.setEnabled(False)
        else:
            self.port_combo.setEnabled(True)
            for port in ports:
                self.port_combo.addItem(f"{port.device} - {port.description}", port.device)

    def get_settings(self):
        """Get current serial settings"""
        try:
            if not self.port_combo.isEnabled() or self.port_combo.currentText() == "No COM ports found":
                return None

            # Safely get port name
            port_data = self.port_combo.currentData()
            if port_data:
                port = port_data
            else:
                # Fallback to parsing text
                port_text = self.port_combo.currentText()
                port = port_text.split(' - ')[0] if ' - ' in port_text else port_text

            # Safely get baud rate
            baud_data = self.baud_combo.currentData()
            baudrate = baud_data if baud_data else int(self.baud_combo.currentText())

            return {
                'port': port,
                'baudrate': baudrate,
                'bytesize': int(self.databits_combo.currentText()),
                'parity': self.parity_combo.currentText()[0],  # N, E, O, M, S
                'stopbits': float(self.stopbits_combo.currentText())
            }
        except Exception as e:
            print(f"Error getting serial settings: {e}")
            return None

    def accept(self):
        """Override accept to validate settings"""
        try:
            settings = self.get_settings()
            if not settings:
                QMessageBox.warning(self, "Warning", "Please select a valid COM port")
                return

            # Additional validation
            if not settings.get('port'):
                QMessageBox.warning(self, "Warning", "Invalid port selection")
                return

            super().accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")
            print(f"Serial setup accept error: {e}")


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    dialog = SerialSetupDialog()
    if dialog.exec_() == QDialog.Accepted:
        print("Settings:", dialog.get_settings())
    sys.exit()