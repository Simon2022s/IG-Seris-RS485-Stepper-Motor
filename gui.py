"""
RS485 Stepper Motor Controller GUI
PyQt5-based user interface for motor control
"""

import sys
import os
import logging
from datetime import datetime
from typing import Optional

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QGroupBox, QVBoxLayout, QHBoxLayout,
    QGridLayout, QFormLayout, QLabel, QLineEdit, QPushButton, QComboBox,
    QTextEdit, QMessageBox, QFileDialog, QCheckBox, QFrame, QTabWidget, QDialog
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QFont, QIcon, QIntValidator, QDoubleValidator

from stepper_motor_controller import StepperMotorController
from config import *
from serial_setup_dialog import SerialSetupDialog


class LogSignals(QObject):
    """Signals for thread-safe logging"""
    log_message = pyqtSignal(str, str)  # message, level


class RS485StepperMotorGUI(QMainWindow):
    """
    Main GUI for RS485 Stepper Motor Controller
    """

    def __init__(self):
        super().__init__()
        self.controller = StepperMotorController()
        self.log_signals = LogSignals()
        self.status_timer = QTimer()

        # Initialize serial settings
        self.serial_settings = self.load_serial_settings()

        # Track version number for UI updates
        self.version_number = None

        self.setup_logging()
        self.init_ui()
        self.setup_connections()
        self.setup_status_timer()

    def setup_logging(self):
        """Setup logging configuration"""
        # Create logs directory if it doesn't exist
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)

        # Configure logging
        log_filename = datetime.now().strftime('%Y-%m-%d.log')
        log_path = os.path.join(LOG_DIR, log_filename)

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_path, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )

        self.logger = logging.getLogger(__name__)

        # Connect logging callback
        self.controller.set_log_callback(self.handle_log_message)
        self.log_signals.log_message.connect(self.append_log)

    def handle_log_message(self, message: str, level: str = "INFO"):
        """Handle log messages from controller"""
        self.log_signals.log_message.emit(message, level)

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle(WINDOW_TITLE)
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

        # Set application icon
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Set application font
        font = QFont(DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZE)
        QApplication.setFont(font)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Create main control area
        control_widget = QWidget()
        main_layout.addWidget(control_widget)

        # Setup control area
        self.setup_control_area(control_widget)

        # Create right-side log panel (initially hidden)
        self.create_log_panel()

        self.update_ui_state()

    def setup_control_area(self, widget):
        """Setup the main control area"""
        layout = QVBoxLayout(widget)

        # 1. Connection Section
        self.connection_group = QGroupBox("Connection")
        self.connection_group.setStyleSheet("QGroupBox { font-size: 11px; padding-top: 10px; }")
        setup_layout = QHBoxLayout()

        # Connection buttons - rectangular with equal dimensions
        self.serial_setup_btn = QPushButton("Serial Setup")
        self.serial_setup_btn.setFixedSize(100, 31)
        self.serial_setup_btn.setStyleSheet("""
            QPushButton {
                background-color: #00A1CB;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #008FB3;
            }
        """)

        # Combined Connect/Disconnect toggle button
        self.connection_toggle_btn = QPushButton("Connect")
        self.connection_toggle_btn.setFixedSize(100, 31)
        self.connection_toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #00A1CB;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #008FB3;
            }
        """)

        # Logs button - same style as connection buttons
        self.logs_button = QPushButton("Logs")
        self.logs_button.setFixedSize(100, 31)
        self.logs_button.setStyleSheet("""
            QPushButton {
                background-color: #00A1CB;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #008FB3;
            }
        """)

        # Enable/Disable toggle button
        self.enable_disable_btn = QPushButton("Enable")
        self.enable_disable_btn.setFixedSize(100, 31)
        self.enable_disable_btn.setEnabled(False)  # Disabled until connected
        self.enable_disable_btn.setStyleSheet("""
            QPushButton {
                background-color: #00A1CB;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #008FB3;
            }
        """)

        # Restart button
        self.restart_btn = QPushButton("Restart")
        self.restart_btn.setFixedSize(100, 31)
        self.restart_btn.setEnabled(False)  # Disabled until connected
        self.restart_btn.setStyleSheet("""
            QPushButton {
                background-color: #00A1CB;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #008FB3;
            }
        """)

        # Add to layout
        setup_layout.addWidget(self.serial_setup_btn)
        setup_layout.addWidget(self.connection_toggle_btn)
        setup_layout.addWidget(self.enable_disable_btn)
        setup_layout.addWidget(self.restart_btn)
        setup_layout.addStretch()
        setup_layout.addWidget(self.logs_button)

        self.connection_group.setLayout(setup_layout)
        layout.addWidget(self.connection_group)

        # 2. Parameters & Status Section
        params_status_group = QGroupBox("Parameters")
        params_status_layout = QHBoxLayout()

        # Left side - Motor Information parameters
        left_params_layout = QVBoxLayout()

        # Motor ID
        motor_id_layout = QHBoxLayout()
        motor_id_layout.addWidget(QLabel("Motor ID:"))
        self.motor_id_param_input = QLineEdit(str(DEFAULT_MOTOR_ID))
        self.motor_id_param_input.setFixedWidth(80)
        self.motor_id_param_input.setValidator(QIntValidator(1, 247))
        # Alias for test compatibility
        self.motor_id_spin_params = self.motor_id_param_input
        self.query_motor_id_btn = QPushButton("?")
        self.query_motor_id_btn.setFixedSize(35, 31)
        self.query_motor_id_btn.setStyleSheet("""
            QPushButton {
                background-color: #00A1CB;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #008FB3;
            }
        """)
        self.set_motor_id_param_btn = QPushButton("Set")
        self.set_motor_id_param_btn.setFixedSize(35, 31)
        self.set_motor_id_param_btn.setStyleSheet("""
            QPushButton {
                background-color: #00A1CB;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #008FB3;
            }
        """)
        # Alias for test compatibility
        self.set_motor_id_btn = self.set_motor_id_param_btn
        motor_id_layout.addWidget(self.motor_id_param_input)
        motor_id_layout.addWidget(self.query_motor_id_btn)
        motor_id_layout.addWidget(self.set_motor_id_param_btn)
        left_params_layout.addLayout(motor_id_layout)

        # Rated Current
        rated_current_layout = QHBoxLayout()
        rated_current_layout.addWidget(QLabel("Rated Current(cA):"))
        self.rated_current_input = QLineEdit("1000")
        self.rated_current_input.setFixedWidth(80)
        self.query_rated_current_btn = QPushButton("?")
        self.query_rated_current_btn.setFixedSize(35, 31)
        self.query_rated_current_btn.setStyleSheet("""
            QPushButton {
                background-color: #00A1CB;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #008FB3;
            }
        """)
        self.set_rated_current_btn = QPushButton("Set")
        self.set_rated_current_btn.setFixedSize(35, 31)
        self.set_rated_current_btn.setStyleSheet("""
            QPushButton {
                background-color: #00A1CB;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #008FB3;
            }
        """)
        rated_current_layout.addWidget(self.rated_current_input)
        rated_current_layout.addWidget(self.query_rated_current_btn)
        rated_current_layout.addWidget(self.set_rated_current_btn)
        left_params_layout.addLayout(rated_current_layout)

        # PPR
        ppr_layout = QHBoxLayout()
        ppr_layout.addWidget(QLabel("PPR(pulses/rev):"))
        self.ppr_input = QLineEdit("3200")
        self.ppr_input.setFixedWidth(80)
        self.query_ppr_btn = QPushButton("?")
        self.query_ppr_btn.setFixedSize(35, 31)
        self.query_ppr_btn.setStyleSheet("""
            QPushButton {
                background-color: #00A1CB;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #008FB3;
            }
        """)
        self.set_ppr_btn = QPushButton("Set")
        self.set_ppr_btn.setFixedSize(35, 31)
        self.set_ppr_btn.setStyleSheet("""
            QPushButton {
                background-color: #00A1CB;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #008FB3;
            }
        """)
        ppr_layout.addWidget(self.ppr_input)
        ppr_layout.addWidget(self.query_ppr_btn)
        ppr_layout.addWidget(self.set_ppr_btn)
        left_params_layout.addLayout(ppr_layout)

        # Idle Current
        idle_current_layout = QHBoxLayout()
        idle_current_layout.addWidget(QLabel("Idle Current(%):"))
        self.idle_current_input = QLineEdit("30")
        self.idle_current_input.setFixedWidth(80)
        self.idle_current_input.setValidator(QIntValidator(0, 100))  # Restrict to 0-100 range
        self.query_idle_current_btn = QPushButton("?")
        self.query_idle_current_btn.setFixedSize(35, 31)
        self.query_idle_current_btn.setStyleSheet("""
            QPushButton {
                background-color: #00A1CB;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #008FB3;
            }
        """)
        self.set_idle_current_btn = QPushButton("Set")
        self.set_idle_current_btn.setFixedSize(35, 31)
        self.set_idle_current_btn.setStyleSheet("""
            QPushButton {
                background-color: #00A1CB;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #008FB3;
            }
        """)
        idle_current_layout.addWidget(self.idle_current_input)
        idle_current_layout.addWidget(self.query_idle_current_btn)
        idle_current_layout.addWidget(self.set_idle_current_btn)
        left_params_layout.addLayout(idle_current_layout)

        # Work Speed
        work_speed_layout = QHBoxLayout()
        work_speed_layout.addWidget(QLabel("Work Speed(RPM):"))
        self.work_speed_input = QLineEdit("100")
        self.work_speed_input.setFixedWidth(80)
        self.query_work_speed_btn = QPushButton("?")
        self.query_work_speed_btn.setFixedSize(35, 31)
        self.query_work_speed_btn.setStyleSheet("""
            QPushButton {
                background-color: #00A1CB;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #008FB3;
            }
        """)
        self.set_work_speed_btn = QPushButton("Set")
        self.set_work_speed_btn.setFixedSize(35, 31)
        self.set_work_speed_btn.setStyleSheet("""
            QPushButton {
                background-color: #00A1CB;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #008FB3;
            }
        """)
        work_speed_layout.addWidget(self.work_speed_input)
        work_speed_layout.addWidget(self.query_work_speed_btn)
        work_speed_layout.addWidget(self.set_work_speed_btn)
        left_params_layout.addLayout(work_speed_layout)

        params_status_layout.addLayout(left_params_layout)

        # Right side - Motion parameters
        right_params_layout = QVBoxLayout()

        # Acceleration
        acceleration_layout = QHBoxLayout()
        acceleration_layout.addWidget(QLabel("Acceleration (ms):"))
        self.acceleration_input = QLineEdit("30")
        self.acceleration_input.setFixedWidth(80)
        self.query_acceleration_btn = QPushButton("?")
        self.query_acceleration_btn.setFixedSize(35, 31)
        self.query_acceleration_btn.setStyleSheet("""
            QPushButton {
                background-color: #00A1CB;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #008FB3;
            }
        """)
        self.set_acceleration_btn = QPushButton("Set")
        self.set_acceleration_btn.setFixedSize(35, 31)
        self.set_acceleration_btn.setStyleSheet("""
            QPushButton {
                background-color: #00A1CB;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #008FB3;
            }
        """)
        acceleration_layout.addWidget(self.acceleration_input)
        acceleration_layout.addWidget(self.query_acceleration_btn)
        acceleration_layout.addWidget(self.set_acceleration_btn)
        right_params_layout.addLayout(acceleration_layout)

        # Deceleration
        deceleration_layout = QHBoxLayout()
        deceleration_layout.addWidget(QLabel("Deceleration (ms):"))
        self.deceleration_input = QLineEdit("30")
        self.deceleration_input.setFixedWidth(80)
        self.query_deceleration_btn = QPushButton("?")
        self.query_deceleration_btn.setFixedSize(35, 31)
        self.query_deceleration_btn.setStyleSheet("""
            QPushButton {
                background-color: #00A1CB;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #008FB3;
            }
        """)
        self.set_deceleration_btn = QPushButton("Set")
        self.set_deceleration_btn.setFixedSize(35, 31)
        self.set_deceleration_btn.setStyleSheet("""
            QPushButton {
                background-color: #00A1CB;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #008FB3;
            }
        """)
        deceleration_layout.addWidget(self.deceleration_input)
        deceleration_layout.addWidget(self.query_deceleration_btn)
        deceleration_layout.addWidget(self.set_deceleration_btn)
        right_params_layout.addLayout(deceleration_layout)

        # Stop Speed
        stop_speed_layout = QHBoxLayout()
        stop_speed_layout.addWidget(QLabel("Stop Speed (RPM):"))
        self.stop_speed_input = QLineEdit("50")
        self.stop_speed_input.setFixedWidth(80)
        self.query_stop_speed_btn = QPushButton("?")
        self.query_stop_speed_btn.setFixedSize(35, 31)
        self.query_stop_speed_btn.setStyleSheet("""
            QPushButton {
                background-color: #00A1CB;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #008FB3;
            }
        """)
        self.set_stop_speed_btn = QPushButton("Set")
        self.set_stop_speed_btn.setFixedSize(35, 31)
        self.set_stop_speed_btn.setStyleSheet("""
            QPushButton {
                background-color: #00A1CB;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #008FB3;
            }
        """)
        stop_speed_layout.addWidget(self.stop_speed_input)
        stop_speed_layout.addWidget(self.query_stop_speed_btn)
        stop_speed_layout.addWidget(self.set_stop_speed_btn)
        right_params_layout.addLayout(stop_speed_layout)

        # Start Speed
        start_speed_layout = QHBoxLayout()
        start_speed_layout.addWidget(QLabel("Start Speed (RPM):"))
        self.start_speed_input = QLineEdit("100")
        self.start_speed_input.setFixedWidth(80)
        self.query_start_speed_btn = QPushButton("?")
        self.query_start_speed_btn.setFixedSize(35, 31)
        self.query_start_speed_btn.setStyleSheet("""
            QPushButton {
                background-color: #00A1CB;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #008FB3;
            }
        """)
        self.set_start_speed_btn = QPushButton("Set")
        self.set_start_speed_btn.setFixedSize(35, 31)
        self.set_start_speed_btn.setStyleSheet("""
            QPushButton {
                background-color: #00A1CB;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #008FB3;
            }
        """)
        start_speed_layout.addWidget(self.start_speed_input)
        start_speed_layout.addWidget(self.query_start_speed_btn)
        start_speed_layout.addWidget(self.set_start_speed_btn)
        right_params_layout.addLayout(start_speed_layout)

        # Position
        position_layout = QHBoxLayout()
        position_layout.addWidget(QLabel("Position (Pulses):"))
        self.position_input = QLineEdit("0")
        self.position_input.setFixedWidth(80)
        self.query_position_btn = QPushButton("?")
        self.query_position_btn.setFixedSize(35, 31)
        self.query_position_btn.setStyleSheet("""
            QPushButton {
                background-color: #00A1CB;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #008FB3;
            }
        """)
        self.set_position_btn = QPushButton("Set")
        self.set_position_btn.setFixedSize(35, 31)
        self.set_position_btn.setStyleSheet("""
            QPushButton {
                background-color: #00A1CB;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #008FB3;
            }
        """)
        position_layout.addWidget(self.position_input)
        position_layout.addWidget(self.query_position_btn)
        position_layout.addWidget(self.set_position_btn)
        right_params_layout.addLayout(position_layout)

        params_status_layout.addLayout(right_params_layout)
        params_status_group.setLayout(params_status_layout)
        layout.addWidget(params_status_group, 2)  # Give more stretch to parameters section

        # 3. Continuous Motion Section
        continuous_group = QGroupBox("Continuous Motion")
        continuous_layout = QHBoxLayout()
        self.forward_btn = QPushButton("Continuous Forward")
        self.forward_btn.setCheckable(True)
        self.forward_btn.setFixedHeight(31)  # Match parameter button height
        self.forward_btn.setStyleSheet("""
            QPushButton {
                background-color: #00A1CB;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #007A99;
            }
            QPushButton:checked {
                background-color: #008FB3;
            }
            QPushButton:checked:hover {
                background-color: #006A80;
            }
        """)
        self.backward_btn = QPushButton("Continuous Backward")
        self.backward_btn.setCheckable(True)
        self.backward_btn.setFixedHeight(31)  # Match parameter button height
        self.backward_btn.setStyleSheet("""
            QPushButton {
                background-color: #00A1CB;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #007A99;
            }
            QPushButton:checked {
                background-color: #008FB3;
            }
            QPushButton:checked:hover {
                background-color: #006A80;
            }
        """)
        self.decel_stop_btn = QPushButton("Decel Stop")
        self.decel_stop_btn.setFixedHeight(31)  # Match parameter button height
        self.decel_stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #00A1CB;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #007A99;
            }
        """)
        self.immed_stop_btn = QPushButton("Immed Stop")
        self.immed_stop_btn.setFixedHeight(31)  # Match parameter button height
        self.immed_stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #00A1CB;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #007A99;
            }
        """)

        continuous_layout.addWidget(self.forward_btn)
        continuous_layout.addWidget(self.backward_btn)
        continuous_layout.addWidget(self.decel_stop_btn)
        continuous_layout.addWidget(self.immed_stop_btn)
        continuous_group.setLayout(continuous_layout)
        layout.addWidget(continuous_group)

        # 4. Position Control Sections - Side by Side
        position_control_layout = QHBoxLayout()

        # Relative position control
        relative_group = QGroupBox("Relative Position Control")
        relative_layout = QVBoxLayout()

        self.relative_pulses_input = QLineEdit("0")
        self.relative_pulses_input.setValidator(QIntValidator(-2147483648, 2147483647))

        relative_btn_layout = QHBoxLayout()
        self.relative_wait_btn = QPushButton("Move - Wait")
        self.relative_wait_btn.setFixedHeight(31)  # Match parameter button height
        self.relative_wait_btn.setToolTip("Only executable when motor is stopped. Waits for completion.")
        self.relative_wait_btn.setStyleSheet("""
            QPushButton {
                background-color: #00A1CB;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #008FB3;
            }
        """)
        self.relative_immediate_btn = QPushButton("Move - Immediate")
        self.relative_immediate_btn.setFixedHeight(31)  # Match parameter button height
        self.relative_immediate_btn.setToolTip("Executable anytime. Interrupts current motion.")
        self.relative_immediate_btn.setStyleSheet("""
            QPushButton {
                background-color: #00A1CB;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #008FB3;
            }
        """)

        relative_btn_layout.addWidget(self.relative_wait_btn)
        relative_btn_layout.addWidget(self.relative_immediate_btn)

        relative_layout.addWidget(QLabel("Pulses:"))
        relative_layout.addWidget(self.relative_pulses_input)
        relative_layout.addLayout(relative_btn_layout)
        relative_group.setLayout(relative_layout)
        position_control_layout.addWidget(relative_group)

        # Absolute position control
        absolute_group = QGroupBox("Absolute Position Control")
        absolute_layout = QVBoxLayout()

        self.absolute_position_input = QLineEdit("0")
        self.absolute_position_input.setValidator(QIntValidator(-2147483648, 2147483647))

        absolute_btn_layout = QHBoxLayout()
        self.absolute_wait_btn = QPushButton("Move - Wait")
        self.absolute_wait_btn.setFixedHeight(31)  # Match parameter button height
        self.absolute_wait_btn.setToolTip("Only executable when motor is stopped. Moves to target position.")
        self.absolute_wait_btn.setStyleSheet("""
            QPushButton {
                background-color: #00A1CB;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #008FB3;
            }
        """)
        self.absolute_immediate_btn = QPushButton("Move - Immediate")
        self.absolute_immediate_btn.setFixedHeight(31)  # Match parameter button height
        self.absolute_immediate_btn.setToolTip("Executable anytime. Interrupts current motion.")
        self.absolute_immediate_btn.setStyleSheet("""
            QPushButton {
                background-color: #00A1CB;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #008FB3;
            }
        """)

        absolute_btn_layout.addWidget(self.absolute_wait_btn)
        absolute_btn_layout.addWidget(self.absolute_immediate_btn)

        absolute_layout.addWidget(QLabel("Target Position:"))
        absolute_layout.addWidget(self.absolute_position_input)
        absolute_layout.addLayout(absolute_btn_layout)
        absolute_group.setLayout(absolute_layout)
        position_control_layout.addWidget(absolute_group)

        layout.addLayout(position_control_layout)

        # 6. Hex Command Section
        hex_group = QGroupBox("Hex Command")
        hex_layout = QHBoxLayout()

        # Command input - take half the width
        self.hex_command_input = QLineEdit()
        self.hex_command_input.setPlaceholderText("Enter hex command")
        self.hex_command_input.setFont(QFont("Consolas", 10))

        # Buttons container - take the other half with proper spacing
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)  # Add spacing between buttons

        self.send_hex_btn = QPushButton("Send")
        self.send_hex_btn.setFixedHeight(31)
        self.send_hex_btn.setStyleSheet("""
            QPushButton {
                background-color: #00A1CB;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #008FB3;
            }
        """)

        self.send_hex_crc_btn = QPushButton("Send with CRC")
        self.send_hex_crc_btn.setFixedHeight(31)
        self.send_hex_crc_btn.setStyleSheet("""
            QPushButton {
                background-color: #00A1CB;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #008FB3;
            }
        """)

        self.clear_hex_btn = QPushButton("Clear")
        self.clear_hex_btn.setFixedHeight(31)
        self.clear_hex_btn.setStyleSheet("""
            QPushButton {
                background-color: #00A1CB;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #008FB3;
            }
        """)

        # Add buttons to buttons layout
        buttons_layout.addWidget(self.send_hex_btn)
        buttons_layout.addWidget(self.send_hex_crc_btn)
        buttons_layout.addWidget(self.clear_hex_btn)

        # Create widget for buttons layout to allow stretching
        buttons_widget = QWidget()
        buttons_widget.setLayout(buttons_layout)

        # Add input and buttons to main hex layout with stretch factors
        hex_layout.addWidget(self.hex_command_input, 1)  # Takes 1 part of available space
        hex_layout.addWidget(buttons_widget, 1)  # Takes 1 part of available space

        hex_group.setLayout(hex_layout)
        layout.addWidget(hex_group)

        # Add stretch to push content to the top
        layout.addStretch()

    def setup_log_tab(self, tab):
        """Setup the log tab"""
        layout = QVBoxLayout(tab)

        # Log display - takes most of the space
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 9))
        layout.addWidget(self.log_text, 1)  # Give log text area stretch factor of 1

        # Log controls - positioned at bottom
        log_control_layout = QHBoxLayout()

        # Clear Log button - bottom left
        self.clear_log_btn = QPushButton("Clear Log")
        self.clear_log_btn.setFixedHeight(31)  # Match Control page button height
        self.clear_log_btn.setStyleSheet("""
            QPushButton {
                background-color: #00A1CB;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #008FB3;
            }
        """)

        # Save Log button - bottom right
        self.save_log_btn = QPushButton("Save Log")
        self.save_log_btn.setFixedHeight(31)  # Match Control page button height
        self.save_log_btn.setStyleSheet("""
            QPushButton {
                background-color: #00A1CB;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #008FB3;
            }
        """)

        # Add Clear Log to left, Save Log to right with stretch in between
        log_control_layout.addWidget(self.clear_log_btn)
        log_control_layout.addStretch()
        log_control_layout.addWidget(self.save_log_btn)

        layout.addLayout(log_control_layout)

    def create_log_panel(self):
        """Create the right-side log panel"""
        # Create the log panel as a separate widget
        self.log_panel = QWidget()
        self.log_panel.setWindowFlags(Qt.Tool | Qt.WindowCloseButtonHint)
        self.log_panel.setWindowTitle("Logs")

        # Set initial size - will be updated when shown
        self.log_panel.setFixedWidth(400)

        # Position panel to the right of main window
        self.position_log_panel()

        # Setup log panel content
        panel_layout = QVBoxLayout(self.log_panel)
        panel_layout.setContentsMargins(8, 8, 8, 8)  # Add margins for better spacing

        # Log display - takes most of the space
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 9))
        panel_layout.addWidget(self.log_text, 1)

        # Log controls at bottom with proper button sizing
        log_control_layout = QHBoxLayout()
        log_control_layout.setSpacing(8)  # Space between buttons

        # Save Logs button - bottom left
        self.save_log_btn = QPushButton("Save Logs")
        self.save_log_btn.setFixedHeight(31)  # Slightly taller for better appearance
        self.save_log_btn.setMinimumWidth(120)  # Ensure adequate width
        self.save_log_btn.setStyleSheet("""
            QPushButton {
                background-color: #00A1CB;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                padding: 0 16px;  /* Add horizontal padding for text spacing */
            }
            QPushButton:hover {
                background-color: #008FB3;
            }
        """)

        # Clear Logs button - bottom right
        self.clear_log_btn = QPushButton("Clear Logs")
        self.clear_log_btn.setFixedHeight(31)  # Slightly taller for better appearance
        self.clear_log_btn.setMinimumWidth(120)  # Ensure adequate width
        self.clear_log_btn.setStyleSheet("""
            QPushButton {
                background-color: #00A1CB;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                padding: 0 16px;  /* Add horizontal padding for text spacing */
            }
            QPushButton:hover {
                background-color: #008FB3;
            }
        """)

        # Add Save Logs to left, Clear Logs to right
        log_control_layout.addWidget(self.save_log_btn)
        log_control_layout.addStretch()
        log_control_layout.addWidget(self.clear_log_btn)

        panel_layout.addLayout(log_control_layout)

        # Initially hide the panel
        self.log_panel.hide()

    def position_log_panel(self):
        """Position the log panel to the right of the main window with perfect alignment"""
        # Use frame geometry to get the complete window dimensions including borders
        main_frame_geometry = self.frameGeometry()
        main_client_geometry = self.geometry()

        # Calculate the panel position to align with the main window frame
        panel_x = main_frame_geometry.x() + main_frame_geometry.width()
        panel_y = main_frame_geometry.y()

        # Use the client area height (excluding title bar) for the panel
        panel_height = main_client_geometry.height()

        # Set panel dimensions and position
        self.log_panel.setFixedHeight(panel_height)
        self.log_panel.move(panel_x, panel_y)


    def toggle_log_panel(self):
        """Toggle the visibility of the log panel"""
        if self.log_panel.isVisible():
            self.log_panel.hide()
        else:
            self.position_log_panel()
            self.log_panel.show()
            self.log_panel.raise_()  # Bring to front

    def setup_connections(self):
        """Setup signal-slot connections"""
        # Serial setup
        self.serial_setup_btn.clicked.connect(self.show_serial_setup)

        # Connection controls
        self.connection_toggle_btn.clicked.connect(self.toggle_connection)
        self.enable_disable_btn.clicked.connect(self.toggle_enable_disable)
        self.restart_btn.clicked.connect(self.restart_motor)


        # Motion controls - Position Control
        self.relative_wait_btn.clicked.connect(self.on_relative_wait_clicked)
        self.relative_immediate_btn.clicked.connect(self.on_relative_immediate_clicked)
        self.absolute_wait_btn.clicked.connect(self.on_absolute_wait_clicked)
        self.absolute_immediate_btn.clicked.connect(self.on_absolute_immediate_clicked)

        # Continuous motion controls
        self.forward_btn.clicked.connect(self.on_forward_clicked)
        self.backward_btn.clicked.connect(self.on_backward_clicked)
        self.decel_stop_btn.clicked.connect(self.on_decel_stop_clicked)
        self.immed_stop_btn.clicked.connect(self.on_immed_stop_clicked)

        # Parameters & Status controls - Left side
        self.query_motor_id_btn.clicked.connect(self.on_query_motor_id_clicked)
        self.set_motor_id_param_btn.clicked.connect(self.on_set_motor_id_param_clicked)
        self.query_rated_current_btn.clicked.connect(self.on_query_rated_current_clicked)
        self.set_rated_current_btn.clicked.connect(self.on_set_rated_current_clicked)
        self.query_ppr_btn.clicked.connect(self.on_query_ppr_clicked)
        self.set_ppr_btn.clicked.connect(self.on_set_ppr_clicked)
        self.query_work_speed_btn.clicked.connect(self.on_query_work_speed_clicked)
        self.set_work_speed_btn.clicked.connect(self.on_set_work_speed_clicked)
        self.query_idle_current_btn.clicked.connect(self.on_query_idle_current_clicked)
        self.set_idle_current_btn.clicked.connect(self.on_set_idle_current_clicked)

        # Parameters & Status controls - Right side
        self.query_acceleration_btn.clicked.connect(self.on_query_acceleration_clicked)
        self.set_acceleration_btn.clicked.connect(self.on_set_acceleration_clicked)
        self.query_deceleration_btn.clicked.connect(self.on_query_deceleration_clicked)
        self.set_deceleration_btn.clicked.connect(self.on_set_deceleration_clicked)
        self.query_stop_speed_btn.clicked.connect(self.on_query_stop_speed_clicked)
        self.set_stop_speed_btn.clicked.connect(self.on_set_stop_speed_clicked)
        self.query_start_speed_btn.clicked.connect(self.on_query_start_speed_clicked)
        self.set_start_speed_btn.clicked.connect(self.on_set_start_speed_clicked)
        self.query_position_btn.clicked.connect(self.on_query_position_clicked)
        self.set_position_btn.clicked.connect(self.on_set_position_clicked)

        # Hex Command controls
        self.send_hex_btn.clicked.connect(self.on_send_hex_clicked)
        self.send_hex_crc_btn.clicked.connect(self.on_send_hex_crc_clicked)
        self.clear_hex_btn.clicked.connect(self.on_clear_hex_clicked)

        # Log controls
        self.clear_log_btn.clicked.connect(self.clear_log)
        self.save_log_btn.clicked.connect(self.save_log)

        # Logs button
        self.logs_button.clicked.connect(self.toggle_log_panel)


    def setup_status_timer(self):
        """Setup timer for status updates - disabled"""
        # Status timer disabled - no status display in current UI
        pass


    def load_serial_settings(self):
        """Return default serial settings (no file dependency)"""
        return {
            'port': None,
            'baudrate': DEFAULT_BAUDRATE,
            'bytesize': DEFAULT_BYTESIZE,
            'parity': DEFAULT_PARITY,
            'stopbits': DEFAULT_STOPBITS
        }


    def show_serial_setup(self):
        """Show serial setup dialog"""
        dialog = SerialSetupDialog(self)

        # Set current values in dialog
        if self.serial_settings['port']:
            # Find and set current port
            for i in range(dialog.port_combo.count()):
                if dialog.port_combo.itemData(i) == self.serial_settings['port']:
                    dialog.port_combo.setCurrentIndex(i)
                    break

        # Set current baud rate
        current_baud = str(self.serial_settings['baudrate'])
        index = dialog.baud_combo.findText(current_baud)
        if index >= 0:
            dialog.baud_combo.setCurrentIndex(index)

        # Set other values
        dialog.databits_combo.setCurrentText(str(self.serial_settings['bytesize']))
        dialog.parity_combo.setCurrentText(self.serial_settings['parity'])
        dialog.stopbits_combo.setCurrentText(str(self.serial_settings['stopbits']))

        if dialog.exec_() == QDialog.Accepted:
            settings = dialog.get_settings()
            if settings:
                self.serial_settings = settings
                # Don't save settings yet - only save after successful connection

    def toggle_connection(self):
        """Toggle between connect and disconnect states"""
        if self.controller.is_connected():
            self.disconnect_serial()
        else:
            self.connect_serial()

    def connect_serial(self):
        """Connect to serial port"""
        # Auto-detect available ports if none selected
        if not self.serial_settings['port']:
            available_ports = self.controller.scan_ports()
            if not available_ports:
                self.show_error("No COM ports found. Please connect a device and try again.")
                return

            # Use the first available port
            self.serial_settings['port'] = available_ports[0]
            self.handle_log_message(f"Auto-selected port: {self.serial_settings['port']}", "INFO")

        port = self.serial_settings['port']
        baudrate = self.serial_settings['baudrate']
        bytesize = self.serial_settings['bytesize']
        parity = self.serial_settings['parity']
        stopbits = self.serial_settings['stopbits']

        self.handle_log_message(f"Connecting to {port} at {baudrate} bps...", "INFO")
        success = self.controller.connect(port, baudrate, bytesize, parity, stopbits)
        if success:
            self.handle_log_message("Serial port connected successfully", "SUCCESS")
            self.connection_toggle_btn.setText("Disconnect")
            self.update_ui_state()
        else:
            self.show_error("Failed to connect to serial port. Please check:\n1. Device is connected\n2. Correct COM port is selected\n3. Device is powered on\n4. No other software is using the port")

    def disconnect_serial(self):
        """Disconnect from serial port"""
        self.controller.disconnect()
        self.handle_log_message("Serial port disconnected", "INFO")
        self.connection_toggle_btn.setText("Connect")
        self.version_number = None
        self.update_connection_title()
        self.update_ui_state()

    def toggle_enable_disable(self):
        """Toggle motor enable/disable state"""
        if not self.controller.is_connected():
            self.show_error("Please connect to serial port first")
            return

        try:
            if self.enable_disable_btn.text() == "Enable":
                # Enable motor (write 0 to register 0x00D4)
                success = self.controller.write_register_value(REG_ENABLE_DISABLE, 0)
                if success:
                    self.enable_disable_btn.setText("Disable")
                    self.handle_log_message("Motor enabled", "SUCCESS")
                else:
                    self.show_error("Failed to enable motor")
            else:
                # Disable motor (write 1 to register 0x00D4)
                success = self.controller.write_register_value(REG_ENABLE_DISABLE, 1)
                if success:
                    self.enable_disable_btn.setText("Enable")
                    self.handle_log_message("Motor disabled", "INFO")
                else:
                    self.show_error("Failed to disable motor")
        except Exception as e:
            self.show_error(f"Error toggling motor state: {str(e)}")

    def restart_motor(self):
        """Restart motor by writing 0x100 to register 0x00D4"""
        if not self.controller.is_connected():
            self.show_error("Please connect to serial port first")
            return

        try:
            # Restart motor (write 0x100 to register 0x00D4)
            success = self.controller.write_register_value(REG_ENABLE_DISABLE, 0x100)
            if success:
                self.handle_log_message("Motor restart command sent", "SUCCESS")
                # After restart, motor should be in disabled state
                self.enable_disable_btn.setText("Enable")
            else:
                self.show_error("Failed to restart motor")
        except Exception as e:
            self.show_error(f"Error restarting motor: {str(e)}")

    def set_motor_id(self):
        """Set motor ID"""
        try:
            motor_id = int(self.motor_id_input.text())
            success = self.controller.set_slave_address(motor_id)
            if success:
                self.handle_log_message(f"Motor ID set to {motor_id}", "SUCCESS")
            else:
                self.show_error("Failed to set motor ID")
        except ValueError:
            self.show_error("Invalid motor ID")

    def on_relative_wait_clicked(self):
        """Handle relative move wait button"""
        try:
            pulses = int(self.relative_pulses_input.text())
            success = self.controller.relative_move_wait(pulses)
            if success:
                self.handle_log_message(f"Relative move wait: {pulses} pulses", "SUCCESS")
            else:
                self.show_error("Failed to execute relative move wait")
        except ValueError:
            self.show_error("Invalid pulse value")

    def on_relative_immediate_clicked(self):
        """Handle relative move immediate button"""
        try:
            pulses = int(self.relative_pulses_input.text())
            success = self.controller.relative_move_immediate(pulses)
            if success:
                self.handle_log_message(f"Relative move immediate: {pulses} pulses", "SUCCESS")
            else:
                self.show_error("Failed to execute relative move immediate")
        except ValueError:
            self.show_error("Invalid pulse value")

    def on_absolute_wait_clicked(self):
        """Handle absolute move wait button"""
        try:
            position = int(self.absolute_position_input.text())
            success = self.controller.absolute_move_wait(position)
            if success:
                self.handle_log_message(f"Absolute move wait: position {position}", "SUCCESS")
            else:
                self.show_error("Failed to execute absolute move wait")
        except ValueError:
            self.show_error("Invalid position value")

    def on_absolute_immediate_clicked(self):
        """Handle absolute move immediate button"""
        try:
            position = int(self.absolute_position_input.text())
            success = self.controller.absolute_move_immediate(position)
            if success:
                self.handle_log_message(f"Absolute move immediate: position {position}", "SUCCESS")
            else:
                self.show_error("Failed to execute absolute move immediate")
        except ValueError:
            self.show_error("Invalid position value")


    def on_forward_clicked(self):
        """Handle continuous forward button"""
        if self.forward_btn.isChecked():
            success = self.controller.continuous_forward()
            if success:
                self.backward_btn.setEnabled(False)
                self.handle_log_message("Continuous forward started", "INFO")
            else:
                self.forward_btn.setChecked(False)
                self.show_error("Failed to start continuous forward")
        else:
            # When unchecking, use deceleration stop
            success = self.controller.decel_stop()
            if success:
                self.backward_btn.setEnabled(True)
                self.handle_log_message("Continuous motion stopped", "INFO")

    def on_backward_clicked(self):
        """Handle continuous backward button"""
        if self.backward_btn.isChecked():
            success = self.controller.continuous_backward()
            if success:
                self.forward_btn.setEnabled(False)
                self.handle_log_message("Continuous backward started", "INFO")
            else:
                self.backward_btn.setChecked(False)
                self.show_error("Failed to start continuous backward")
        else:
            # When unchecking, use deceleration stop
            success = self.controller.decel_stop()
            if success:
                self.forward_btn.setEnabled(True)
                self.handle_log_message("Continuous motion stopped", "INFO")

    def on_decel_stop_clicked(self):
        """Handle deceleration stop button"""
        success = self.controller.decel_stop()
        if success:
            self.forward_btn.setChecked(False)
            self.backward_btn.setChecked(False)
            self.forward_btn.setEnabled(True)
            self.backward_btn.setEnabled(True)
            self.handle_log_message("Deceleration stop activated", "INFO")
        else:
            self.show_error("Failed to execute deceleration stop")

    def on_immed_stop_clicked(self):
        """Handle immediate stop button"""
        success = self.controller.immed_stop()
        if success:
            self.forward_btn.setChecked(False)
            self.backward_btn.setChecked(False)
            self.forward_btn.setEnabled(True)
            self.backward_btn.setEnabled(True)
            self.handle_log_message("Immediate stop activated", "INFO")
        else:
            self.show_error("Failed to execute immediate stop")

    def on_query_acceleration_clicked(self):
        """Handle query acceleration button"""
        value = self.controller.read_register_value(REG_ACCELERATION)
        if value is not None:
            self.acceleration_input.setText(str(value))
            self.handle_log_message(f"Acceleration: {value} ms", "INFO")
        else:
            self.show_error("Failed to query acceleration")

    def on_query_deceleration_clicked(self):
        """Handle query deceleration button"""
        value = self.controller.read_register_value(REG_DECELERATION)
        if value is not None:
            self.deceleration_input.setText(str(value))
            self.handle_log_message(f"Deceleration: {value} ms", "INFO")
        else:
            self.show_error("Failed to query deceleration")

    def on_query_position_clicked(self):
        """Handle query position button"""
        # Read 32-bit position value using proper 32-bit register read
        position = self.controller.read_32bit_register(REG_POSITION_QUERY_LOW, REG_POSITION_QUERY_HIGH)
        if position is not None:
            # Handle signed 32-bit value
            if position >= 0x80000000:
                position -= 0x100000000
            self.position_input.setText(str(position))
            self.handle_log_message(f"Current Position: {position} pulses", "INFO")
        else:
            self.show_error("Failed to query position")

    def on_query_ppr_clicked(self):
        """Query PPR (Pulses Per Revolution)"""
        value = self.controller.read_32bit_register(REG_PPR_LOW, REG_PPR_HIGH)
        if value is not None:
            self.ppr_input.setText(str(value))
            self.handle_log_message(f"PPR: {value} pulses/rev", "INFO")
        else:
            self.show_error("Failed to query PPR")

    # Parameters & Status methods - Left side
    def on_query_motor_id_clicked(self):
        """Query motor ID - Note: Motor ID is not stored in a register, this is just for display"""
        current_id = self.controller.motor_id
        self.motor_id_param_input.setText(str(current_id))
        self.handle_log_message(f"Current Motor ID: {current_id}", "INFO")

    def on_set_motor_id_param_clicked(self):
        """Set motor ID parameter"""
        try:
            motor_id = int(self.motor_id_param_input.text())
            if not (1 <= motor_id <= 247):
                self.show_error("Motor ID must be between 1 and 247")
                return

            success = self.controller.set_slave_address(motor_id)
            if success:
                self.handle_log_message(f"Motor ID set to {motor_id}", "SUCCESS")
                # Requery version number with new motor ID
                if self.controller.is_connected():
                    QTimer.singleShot(300, self.query_version_number)
            else:
                self.show_error("Failed to set motor ID")
        except ValueError:
            self.show_error("Invalid motor ID value")

    # Alias methods for test compatibility
    def on_set_motor_id_clicked(self):
        """Alias for set motor ID - calls the parameter version"""
        return self.on_set_motor_id_param_clicked()

    def on_continuous_forward_clicked(self):
        """Alias for continuous forward - calls the forward button handler"""
        return self.on_forward_clicked()

    def on_continuous_backward_clicked(self):
        """Alias for continuous backward - calls the backward button handler"""
        return self.on_backward_clicked()

    def on_query_rated_current_clicked(self):
        """Query rated current"""
        value = self.controller.read_register_value(REG_CURRENT)
        if value is not None:
            self.rated_current_input.setText(str(value))
            self.handle_log_message(f"Rated Current: {value} cA", "INFO")
        else:
            self.show_error("Failed to query rated current")

    def on_set_rated_current_clicked(self):
        """Set rated current"""
        try:
            current = int(self.rated_current_input.text())
            success = self.controller.write_register_value(REG_CURRENT, current)
            if success:
                self.handle_log_message(f"Rated Current set to {current} cA", "SUCCESS")
            else:
                self.show_error("Failed to set rated current")
        except ValueError:
            self.show_error("Invalid current value")

    def on_set_ppr_clicked(self):
        """Set PPR"""
        try:
            ppr = int(self.ppr_input.text())
            # Set both low and high words for 32-bit value
            low_word = ppr & 0xFFFF
            high_word = (ppr >> 16) & 0xFFFF

            success1 = self.controller.write_register_value(REG_PPR_LOW, low_word)
            success2 = self.controller.write_register_value(REG_PPR_HIGH, high_word)

            if success1 and success2:
                self.handle_log_message(f"PPR set to {ppr} pulses/rev", "SUCCESS")
            else:
                self.show_error("Failed to set PPR")
        except ValueError:
            self.show_error("Invalid PPR value")

    def on_query_idle_current_clicked(self):
        """Query idle/standby current - uses special parsing for last 2 bytes before CRC"""
        value = self.controller.read_idle_current_value(REG_STANDBY_CURRENT)
        if value is not None:
            # Validate that the value is in the expected range (0-100)
            if 0 <= value <= 100:
                self.idle_current_input.setText(str(value))
                self.handle_log_message(f"Idle Current: {value}%", "INFO")
            else:
                self.show_error(f"Invalid idle current value received: {value}. Expected range: 0-100. Check connection.")
                self.handle_log_message(f"Invalid idle current value: {value}", "ERROR")
        else:
            self.show_error("Failed to query idle current - no response from device")

    def on_query_work_speed_clicked(self):
        """Query work speed using version-appropriate method"""
        # Pass current version number to controller for version-specific behavior
        version = getattr(self, 'version_number', None)
        value = self.controller.read_work_speed(version_number=version)
        if value is not None:
            self.work_speed_input.setText(str(value))
            self.handle_log_message(f"Work Speed: {value} RPM", "INFO")
        else:
            self.show_error("Failed to query work speed")

    def on_set_work_speed_clicked(self):
        """Set work speed using version-appropriate method"""
        try:
            speed_rpm = float(self.work_speed_input.text())  # Allow float input for precision
            if speed_rpm < 0:
                self.show_error("Work speed must be positive")
                return

            # Pass current version number to controller for version-specific behavior
            version = getattr(self, 'version_number', None)
            success = self.controller.write_work_speed(speed_rpm, version_number=version)
            if success:
                self.handle_log_message(f"Work Speed set to {speed_rpm} RPM", "SUCCESS")
            else:
                self.show_error("Failed to set work speed")
        except ValueError:
            self.show_error("Invalid work speed value")

    def on_set_idle_current_clicked(self):
        """Set idle current"""
        try:
            idle_current = int(self.idle_current_input.text())
            if not (0 <= idle_current <= 100):
                self.show_error("Idle current must be between 0 and 100")
                return

            success = self.controller.write_register_value(REG_STANDBY_CURRENT, idle_current)
            if success:
                self.handle_log_message(f"Idle Current set to {idle_current}%", "SUCCESS")
            else:
                self.show_error("Failed to set idle current")
        except ValueError:
            self.show_error("Invalid idle current value")

    # Parameters & Status methods - Right side
    def on_set_acceleration_clicked(self):
        """Set acceleration"""
        try:
            acceleration = int(self.acceleration_input.text())
            success = self.controller.write_register_value(REG_ACCELERATION, acceleration)
            if success:
                self.handle_log_message(f"Acceleration set to {acceleration} ms", "SUCCESS")
            else:
                self.show_error("Failed to set acceleration")
        except ValueError:
            self.show_error("Invalid acceleration value")

    def on_set_deceleration_clicked(self):
        """Set deceleration"""
        try:
            deceleration = int(self.deceleration_input.text())
            success = self.controller.write_register_value(REG_DECELERATION, deceleration)
            if success:
                self.handle_log_message(f"Deceleration set to {deceleration} ms", "SUCCESS")
            else:
                self.show_error("Failed to set deceleration")
        except ValueError:
            self.show_error("Invalid deceleration value")

    def on_query_stop_speed_clicked(self):
        """Query stop speed"""
        # Assuming stop speed is in a specific register
        value = self.controller.read_register_value(REG_STOP_SPEED)
        if value is not None:
            self.stop_speed_input.setText(str(value))
            self.handle_log_message(f"Stop Speed: {value}", "INFO")
        else:
            self.show_error("Failed to query stop speed")

    def on_set_stop_speed_clicked(self):
        """Set stop speed"""
        try:
            stop_speed = int(self.stop_speed_input.text())
            # Assuming stop speed register - adjust as needed
            success = self.controller.write_register_value(REG_STOP_SPEED, stop_speed)
            if success:
                self.handle_log_message(f"Stop Speed set to {stop_speed}", "SUCCESS")
            else:
                self.show_error("Failed to set stop speed")
        except ValueError:
            self.show_error("Invalid stop speed value")

    def on_query_start_speed_clicked(self):
        """Query start speed"""
        # Assuming start speed is in a specific register
        value = self.controller.read_register_value(REG_START_SPEED)
        if value is not None:
            self.start_speed_input.setText(str(value))
            self.handle_log_message(f"Start Speed: {value}", "INFO")
        else:
            self.show_error("Failed to query start speed")

    def on_set_start_speed_clicked(self):
        """Set start speed"""
        try:
            start_speed = int(self.start_speed_input.text())
            # Assuming start speed register - adjust as needed
            success = self.controller.write_register_value(REG_START_SPEED, start_speed)
            if success:
                self.handle_log_message(f"Start Speed set to {start_speed}", "SUCCESS")
            else:
                self.show_error("Failed to set start speed")
        except ValueError:
            self.show_error("Invalid start speed value")

    def on_set_position_clicked(self):
        """Set position"""
        try:
            position = int(self.position_input.text())
            # Set both low and high words for 32-bit value
            low_word = position & 0xFFFF
            high_word = (position >> 16) & 0xFFFF

            success1 = self.controller.write_register_value(REG_POSITION_LOW, low_word)
            success2 = self.controller.write_register_value(REG_POSITION_HIGH, high_word)

            if success1 and success2:
                self.handle_log_message(f"Position set to {position}", "SUCCESS")
            else:
                self.show_error("Failed to set position")
        except ValueError:
            self.show_error("Invalid position value")

    # Hex Command methods
    def on_send_hex_clicked(self):
        """Send hex command without CRC"""
        hex_command = self.hex_command_input.text().strip()
        if not hex_command:
            self.show_error("Please enter a hex command")
            return

        success = self.controller.send_hex_command(hex_command, add_crc=False)
        if not success:
            self.show_error("Failed to send hex command")

    def on_send_hex_crc_clicked(self):
        """Send hex command with CRC"""
        hex_command = self.hex_command_input.text().strip()
        if not hex_command:
            self.show_error("Please enter a hex command")
            return

        success = self.controller.send_hex_command(hex_command, add_crc=True)
        if not success:
            self.show_error("Failed to send hex command with CRC")

    def on_clear_hex_clicked(self):
        """Clear hex command input"""
        self.hex_command_input.clear()

    def update_status(self):
        """Update status display - disabled due to missing UI elements"""
        # Status update disabled - no status labels in current UI
        pass

    def update_connection_title(self):
        """Update connection group title with version number"""
        if self.version_number is not None:
            self.connection_group.setTitle(f"Connection - v.{self.version_number}")
        else:
            self.connection_group.setTitle("Connection")

    def query_version_number(self):
        """Query and update version number from device"""
        if not self.controller.is_connected():
            return

        try:
            version = self.controller.read_version_number()
            if version is not None:
                self.version_number = version
                self.handle_log_message(f"Device version: {version}", "SUCCESS")
                self.update_connection_title()
            else:
                self.handle_log_message("Failed to query version number", "WARNING")
                self.version_number = None
                self.update_connection_title()
        except Exception as e:
            self.handle_log_message(f"Error querying version: {str(e)}", "ERROR")
            self.version_number = None
            self.update_connection_title()

    def update_ui_state(self):
        """Update UI elements based on connection state"""
        connected = self.controller.is_connected()

        # Update connection toggle button text
        if connected:
            self.connection_toggle_btn.setText("Disconnect")
        else:
            self.connection_toggle_btn.setText("Connect")

        # Enable/disable controls based on connection state
        self.relative_wait_btn.setEnabled(connected)
        self.relative_immediate_btn.setEnabled(connected)
        self.absolute_wait_btn.setEnabled(connected)
        self.absolute_immediate_btn.setEnabled(connected)
        self.forward_btn.setEnabled(connected)
        self.backward_btn.setEnabled(connected)
        self.decel_stop_btn.setEnabled(connected)
        self.immed_stop_btn.setEnabled(connected)

        # Enable/disable motor control buttons
        self.enable_disable_btn.setEnabled(connected)
        self.restart_btn.setEnabled(connected)

        # If not connected, reset enable/disable button to "Enable"
        if not connected:
            self.enable_disable_btn.setText("Enable")

        # Query version number when connected
        if connected:
            # Use a single-shot timer to query version after connection is established
            QTimer.singleShot(500, self.query_version_number)
        else:
            # Clear version when disconnected
            self.version_number = None
            self.update_connection_title()

    def append_log(self, message: str, level: str = "INFO"):
        """Append message to log with color coding"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"

        # Color coding based on level
        color_map = {
            "INFO": Qt.black,
            "SUCCESS": Qt.darkGreen,  # Changed from Qt.green to softer Qt.darkGreen
            "WARNING": Qt.darkYellow,
            "ERROR": Qt.red,
            "TX": Qt.blue,
            "RX": Qt.darkMagenta
        }

        color = color_map.get(level, Qt.black)

        # Add to log display
        self.log_text.setTextColor(color)
        self.log_text.append(formatted_message)

        # Auto-scroll to bottom
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.End)
        self.log_text.setTextCursor(cursor)

    def clear_log(self):
        """Clear the log display"""
        self.log_text.clear()

    def save_log(self):
        """Save log to file"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Log", "", "Text Files (*.txt);;All Files (*)"
        )
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.toPlainText())
                self.handle_log_message(f"Log saved to {filename}", "SUCCESS")
            except Exception as e:
                self.show_error(f"Failed to save log: {str(e)}")

    def show_error(self, message: str):
        """Show error message dialog"""
        QMessageBox.critical(self, "Error", message)
        self.handle_log_message(f"Error: {message}", "ERROR")

    def closeEvent(self, event):
        """Handle window close event"""
        if self.controller.is_connected():
            reply = QMessageBox.question(
                self, 'Confirm Exit',
                "Serial port is connected. Do you want to disconnect before exiting?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )

            if reply == QMessageBox.Yes:
                self.disconnect_serial()
                event.accept()
            elif reply == QMessageBox.No:
                # Force disconnect even if user says no
                self.controller.disconnect()
                event.accept()
            else:
                event.ignore()
        else:
            # Ensure controller is properly disconnected
            self.controller.disconnect()
            # Close log panel when main window closes
            if hasattr(self, 'log_panel'):
                self.log_panel.close()
            event.accept()

    def moveEvent(self, event):
        """Handle main window move event to reposition log panel"""
        super().moveEvent(event)
        if hasattr(self, 'log_panel') and self.log_panel.isVisible():
            self.position_log_panel()

    def resizeEvent(self, event):
        """Handle main window resize event to reposition log panel"""
        super().resizeEvent(event)
        if hasattr(self, 'log_panel') and self.log_panel.isVisible():
            self.position_log_panel()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RS485StepperMotorGUI()
    window.show()
    sys.exit(app.exec_())