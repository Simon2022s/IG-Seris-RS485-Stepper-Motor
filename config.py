"""Configuration for RS485 Stepper Motor Controller"""

import os
from PyQt5.QtGui import QFont

# ==================== Communication Parameters ====================
DEFAULT_BAUDRATE = 9600
BAUDRATE_OPTIONS = [4800, 9600, 19200, 25600, 28800, 38400, 57600, 115200]
DEFAULT_BYTESIZE = 8
DEFAULT_STOPBITS = 1
DEFAULT_PARITY = 'N'  # None
DEFAULT_TIMEOUT = 3000  # ms

# ==================== Register Addresses (from Manual) ====================
# Motion Control Registers (32-bit)
REG_RELATIVE_MOVE_WAIT = 0x00CE        # 0x00CE/0x00CF: Relative move, wait for completion
REG_RELATIVE_MOVE_WAIT_LOW = 0x00CE
REG_RELATIVE_MOVE_WAIT_HIGH = 0x00CF
REG_RELATIVE_MOVE_IMM_LOW = 0x00DE     # 0x00DE/0x00DF: Relative move, immediate execution
REG_RELATIVE_MOVE_IMM_HIGH = 0x00DF

REG_ABSOLUTE_MOVE_WAIT = 0x00D0       # 0x00D0/0x00D1: Absolute move, wait for completion
REG_ABSOLUTE_MOVE_WAIT_LOW = 0x00D0
REG_ABSOLUTE_MOVE_WAIT_HIGH = 0x00D1
REG_ABSOLUTE_MOVE_IMM_LOW = 0x00E8     # 0x00E8/0x00E9: Absolute move, immediate execution
REG_ABSOLUTE_MOVE_IMM_HIGH = 0x00E9


# Position Registers (Updated according to reference manual)
REG_POSITION_QUERY_LOW = 0x0004     # Query position (low) - for ? button
REG_POSITION_QUERY_HIGH = 0x0005    # Query position (high) - for ? button
REG_POSITION_LOW = 0x00D2          # Set position (low) - for Set button
REG_POSITION_HIGH = 0x00D3         # Set position (high) - for Set button

# Motor Parameters (Query Registers - ? buttons)
REG_CURRENT = 0x000D              # Rated Current (cA) - query
REG_PPR_LOW = 0x0024                  # Pulses per revolution - query(low 16 bits)
REG_PPR_HIGH = 0x0025                  # Pulses per revolution - query(high 16 bits)
REG_STANDBY_CURRENT = 0x000E      # (Bit 0-7 ), Standby/Idle current % - query

REG_WORK_SPEED_16 = 0x009A        # Work Speed(RPM) - 16-bit version
REG_WORK_SPEED_LOW = 0x00D8        # Work Speed(0.01 RPM)- query(low 16bits)
REG_WORK_SPEED_HIGH = 0x00D9        # Work Speed(0.01 RPM)- query(high 16bits)

REG_PEAK_CURRENT = 0x0013         # Peak current % - query
REG_ACCELERATION_QUERY = 0x0098   # Acceleration(ms) - query
REG_DECELERATION_QUERY = 0x0099   # Deceleration(ms) - query
REG_START_SPEED_QUERY = 0x0096    # Start speed - query
REG_STOP_SPEED_QUERY = 0x0097     # Stop speed - query

# Motor Parameters (Set Registers - Set buttons)
REG_CURRENT_SET = 0x000D              # Rated Current (cA) - set
REG_PPR_LOW_SET = 0x0024                  # Pulses per revolution - set(low 16 bits)
REG_PPR_HIGH_SET = 0x0025                  # Pulses per revolution - set(high 16 bits)
REG_STANDBY_CURRENT_SET = 0x000E      # (Bit 0-7), Standby/Idle current % - set

REG_WORK_SPEED_LOW_SET = 0x00D8        # Work Speed(0.01 RPM)- set (low 16bits)
REG_WORK_SPEED_HIGH_SET = 0x00D9        # Work Speed(0.01 RPM)- set(high 16bits)
REG_WORK_SPEED_16_SET = 0x009A        # Work Speed(RPM) - 16-bit version set

REG_PEAK_CURRENT_SET = 0x0013         # Peak current % - set
REG_ACCELERATION_SET = 0x0098         # Acceleration(ms) - set
REG_DECELERATION_SET = 0x0099         # Deceleration(ms) - set
REG_START_SPEED_SET = 0x0096          # Start speed - set
REG_STOP_SPEED_SET = 0x0097           # Stop speed - set


# Enable/Disable Control Register
REG_ENABLE_DISABLE = 0x00D4  # 0=Enable, 1=Disable, 0x100=Restart

# Additional Control Registers
REG_CONTROL_MODE = 0x00C0  # Control mode register
CONTROL_STOP = 0x0000     # Stop control value
REG_RETURN_HOME = 0x00C1  # Return to home register

# Status and Fault Registers
REG_STATUS = 0x0006       # Motor status register
REG_FAULT = 0x0007        # Fault information register

# Speed and Acceleration Registers (32-bit)
REG_SPEED_LOW = 0x0008    # Current speed low word
REG_SPEED_HIGH = 0x0009   # Current speed high word
REG_ACCEL_LOW = 0x0010    # Acceleration low word
REG_ACCEL_HIGH = 0x0011   # Acceleration high word
REG_DECEL_LOW = 0x0012    # Deceleration low word
REG_DECEL_HIGH = 0x0013   # Deceleration high word

# Status and Fault Mappings
STATUS_MAPPING = {
    0: "Stopped",
    1: "Running",
    2: "Fault",
    3: "Homing"
}

FAULT_MAPPING = {
    0: "No Fault",
    1: "Over Current",
    2: "Over Voltage",
    3: "Under Voltage",
    4: "Over Temperature",
    5: "Motor Blocked",
    6: "Encoder Error"
}


REG_CONTINUOUS_MOTION = 0x00C8
# Continuous Motion Control Values (Register 0x00C8)
CONTINUOUS_FORWARD = 0x0001      # 1: Continuous Forward
CONTINUOUS_BACKWARD = 0x0101     # 257: Continuous Backward
CONTINUOUS_DECEL_STOP = 0x0000   # 0: Deceleration Stop
CONTINUOUS_IMMED_STOP = 0x0100   # 256: Immediate Stop



# ==================== Default Parameters ====================
DEFAULT_MOTOR_ID = 1
DEFAULT_SPEED = 50
DEFAULT_ACCELERATION = 120
DEFAULT_DECELERATION = 120

# ==================== UI Settings ====================
WINDOW_TITLE = "RS485 Stepper Motor Controller"
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 800
WINDOW_MIN_WIDTH = 800
WINDOW_MIN_HEIGHT = 600
DEFAULT_FONT_FAMILY = "Segoe UI"
DEFAULT_FONT_SIZE = 10

# ==================== Logging ====================
LOG_CONFIG = {
    'log_level': 'INFO',
    'log_format': '%(asctime)s - %(levelname)s - %(message)s'
}

# Paths
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(PROJECT_DIR, "logs")
ICON_PATH = os.path.join(PROJECT_DIR, "logo.ico")