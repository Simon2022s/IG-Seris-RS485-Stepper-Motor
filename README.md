# RS485 Stepper Motor Controller

A professional Python-based RS485 stepper motor control software with Modbus RTU protocol support. Features a modern PyQt5 GUI interface for precise motor control and monitoring.

> **Compatible Motor**: This software is optimized for the [NEMA34 Absolute Encoder Stepper Motor](https://www.adampower.de/nema34_absolute_encoder_stepper_motor) — a high-performance closed-loop stepper motor featuring RS485 Modbus RTU communication, 17-bit absolute encoder for precise position feedback, and integrated drive electronics. Perfect for applications requiring accurate positioning and reliable industrial communication.

## 🚀 Features

- **RS485 Communication**: Full Modbus RTU protocol support
- **Dual Motion Control**: Both relative and absolute positioning modes
- **Real-time Monitoring**: Live position, speed, and status updates
- **Emergency Controls**: Emergency stop and homing functions
- **Parameter Configuration**: Speed and acceleration settings
- **Comprehensive Logging**: Detailed operation logs with color coding
- **Multi-motor Support**: Configurable slave addresses for multiple motors
- **Cross-platform**: Works on Windows, Linux, and macOS

## 📋 System Requirements

- Python 3.8 or higher
- Windows 7+ / Linux / macOS
- USB to RS485 adapter
- Stepper motor driver supporting Modbus RTU protocol

## 🔧 Installation

### Method 1: Using pip (Recommended)

```bash
# Clone or download the project
cd newRS485

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Method 2: Manual Installation

```bash
pip install minimalmodbus pyserial PyQt5 pyinstaller
```

## 🎮 Usage

### Running the Application

```bash
python main.py
```

### Basic Operation Workflow

1. **Serial Connection**:
   - Select your COM port from the dropdown
   - Choose baud rate (default: 9600)
   - Click "Connect" to establish connection

2. **Motor Configuration**:
   - Set Motor ID (default: 1, range: 1-247)
   - Configure speed and acceleration parameters

3. **Motion Control**:
   - **Relative Position**: Move relative to current position
   - **Absolute Position**: Move to specific position relative to origin
   - **Continuous Motion**: Forward/reverse continuous movement
   - **Emergency Stop**: Immediate motor halt
   - **Return to Origin**: Home position routine

4. **Monitoring**:
   - Real-time position and speed display
   - Motor status indicators
   - Fault information display
   - Operation logs

### Control Modes

#### Relative Position Control
- **Wait Mode**: Only executable when motor is stopped, waits for completion
- **Immediate Mode**: Can interrupt current motion, executes immediately

#### Absolute Position Control
- **Wait Mode**: Only executable when stopped, moves to target position
- **Immediate Mode**: Can interrupt current motion, moves to target immediately

#### Continuous Motion
- **Forward/Reverse**: Continuous rotation in selected direction
- **Stop**: Halts continuous motion

## 📁 Project Structure

```
newRS485/
├── main.py                     # Application entry point
├── gui.py                     # PyQt5 GUI implementation
├── stepper_motor_controller.py # Core motor control logic
├── config.py                  # Configuration and constants
├── requirements.txt           # Python dependencies
├── README.md                  # This documentation
├── logs/                      # Log files directory
└── dist/                      # Generated EXE files
```

## 🔌 Hardware Setup

This software is designed for the [NEMA34 Absolute Encoder Stepper Motor](https://www.adampower. de/nema34_absolute_encoder_stepper_motor) with integrated RS485 Modbus RTU control, featuring 17-bit absolute encoder resolution and precise position tracking.

### RS485 Connection

Connect your USB-to-RS485 adapter to the stepper motor driver:

```
USB-RS485 Adapter    Stepper Driver
     A+      ----->     A+
     B-      ----->     B-
    GND      ----->    GND
```

### Motor Driver Configuration

1. Set the motor driver to Modbus RTU mode
2. Configure the slave address (default: 1)
3. Set communication parameters:
   - Baud rate: 9600 (or 19200, 57,600, 115200)
   - Data bits: 8
   - Stop bits: 1
   - Parity: None

## 📊 Register Map

### Motion Control Registers
- `0x00CE/0x00CF`: Relative Move Wait (32-bit)
- `0x00DE/0x00DF`: Relative Move Immediate (32-bit)
- `0x00D0/0x00D1`: Absolute Move Wait (32-bit)
- `0x00E8/0x00E9`: Absolute Move Immediate (32-bit)

### Parameter Registers
- `0x0040/0x0041`: Speed (32-bit)
- `0x0042/0x0043`: Acceleration (32-bit)

### Status Registers
- `0x0027/0x0028`: Current Position (32-bit)
- `0x0046`: Motor Status
- `0x0049`: Fault Information

### Control Registers
- `0x0046`: Control Mode
- `0x0047`: Return to Origin
- `0x0048`: Position Mode (Incremental/Absolute)

## 🛠 ?Development

### Code Standards

- Follow PEP 8 style guide
- Use type hints for function parameters
- Include comprehensive docstrings
- Implement proper error handling

### Adding New Features

1. **New Control Functions**: Add to `stepper_motor_controller.py`
2. **GUI Updates**: Modify `gui.py` for new interface elements
3. **Configuration**: Update `config.py` for new parameters
4. **Documentation**: Update this README.md file

### Testing

```bash
# Run basic functionality tests
python -c "from stepper_motor_controller import StepperMotorController; print('Import successful')"
```

## 📦 Creating Executable (EXE)

### Using PyInstaller

```bash
# Install PyInstaller
pip install pyinstaller

# Create executable
pyinstaller --onefile --windowed --name="RS485_Stepper_Controller" main.py

# Executable will be in dist/ directory
ls dist/
```

### Executable Features

- Single file distribution (no installation required)
- No Python environment needed on target machine
- Includes all dependencies
- Windows executable with custom icon (if provided)

## 📝 Troubleshooting

### Common Issues

#### Connection Problems
- **Issue**: "Failed to connect to serial port"
- **Solution**: 
  1. Check USB-RS485 adapter is properly connected
  2. Verify COM port selection
  3. Check driver installation for USB adapter
  4. Ensure no other application is using the port

#### Motor Not Responding
- **Issue**: Commands sent but motor doesn't move
- **Solution**:
  1. Verify motor power supply
  2. Check RS485 wiring (A+ to A+, B- to B-)
  3. Confirm motor ID matches driver setting
  4. Check baud rate configuration

#### Communication Errors
- **Issue**: "Communication error" in logs
- **Solution**:
  1. Check cable connections
  2. Verify baud rate settings
  3. Reduce cable length if too long
  4. Add RS485 termination resistor if needed

#### Position Reading Errors
- **Issue**: Incorrect position values
- **Solution**:
  1. Check register addresses match your driver
  2. Verify 32-bit value handling
  3. Ensure proper signed integer conversion

### Debug Mode

Enable detailed logging by modifying `config.py`:

```python
LOG_CONFIG = {
    'log_level': 'DEBUG',  # Change from INFO to DEBUG
    # ... other settings
}
```

## 📄 License

MIT License - See LICENSE file for details

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues and questions:
1. Check this documentation first
2. Review the troubleshooting section
3. Check application logs in the `logs/` directory
4. Create an issue with detailed information:
   - Operating system
   - Python version
   - Hardware setup
   - Error logs
   - Steps to reproduce

## 🙏 Acknowledgments

- **minimalmodbus**: Modbus communication library
- **PyQt5**: GUI framework
- **pyserial**: Serial communication
- **PyInstaller**: Executable packaging

---

**Note**: This software is designed for learning and testing purposes. Always test thoroughly in a safe environment before using in production applications.
