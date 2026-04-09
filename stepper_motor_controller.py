"""Stepper Motor Controller - Core RS485 Modbus RTU Communication"""

import serial
import serial.tools.list_ports
import time
import logging
from config import *

# CRC16 Modbus calculation
def calc_crc(hex_string):
    """Calculate CRC16 Modbus checksum - matching reference project"""
    data = bytearray.fromhex(hex_string)
    crc = 0xFFFF
    for pos in data:
        crc ^= pos
        for i in range(8):
            if (crc & 1) != 0:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    # Use reference project's byte order (little endian)
    crc_0 = crc & 0xff
    crc_1 = crc >> 8
    str_crc_0 = '{:02x}'.format(crc_0).upper()
    str_crc_1 = '{:02x}'.format(crc_1).upper()
    return str_crc_0 + str_crc_1

class StepperMotorController:
    """Core controller for RS485 stepper motor via Modbus RTU"""
    
    def __init__(self):
        self.serial_port = None
        self.motor_id = DEFAULT_MOTOR_ID
        self.connected = False
        self.running = False
        self.log_callback = None
        
    def set_log_callback(self, callback):
        """Set logging callback for GUI updates"""
        self.log_callback = callback
        
    def log(self, message, level="INFO"):
        """Log message"""
        if self.log_callback:
            self.log_callback(message, level)
        logging.info(message)
        
    # ==================== Serial Port Functions ====================
    
    def scan_ports(self):
        """Scan and return available COM ports"""
        ports = list(serial.tools.list_ports.comports())
        return [p.device for p in ports]
        
    def connect(self, port, baudrate=DEFAULT_BAUDRATE, bytesize=None, parity=None, stopbits=None, timeout=DEFAULT_TIMEOUT):
        """Connect to serial port and verify communication"""
        try:
            if self.connected:
                self.disconnect()

            # Convert bytesize
            if bytesize == 7:
                ser_bytesize = serial.SEVENBITS
            elif bytesize == 8:
                ser_bytesize = serial.EIGHTBITS
            else:
                ser_bytesize = serial.EIGHTBITS

            # Convert parity
            if parity == 'E':
                ser_parity = serial.PARITY_EVEN
            elif parity == 'O':
                ser_parity = serial.PARITY_ODD
            else:
                ser_parity = serial.PARITY_NONE

            # Convert stopbits
            if stopbits == 2:
                ser_stopbits = serial.STOPBITS_TWO
            else:
                ser_stopbits = serial.STOPBITS_ONE

            self.serial_port = serial.Serial(
                port=port,
                baudrate=baudrate,
                bytesize=ser_bytesize,
                stopbits=ser_stopbits,
                parity=ser_parity,
                timeout=0.1  # Use shorter timeout like reference project
            )

            # Port opened successfully - set connected flag
            # We'll test actual communication when commands are sent
            self.connected = True
            self.log(f"Connected to {port} at {baudrate} bps", "SUCCESS")
            return True

        except serial.SerialException as e:
            self.log(f"Serial port error: {str(e)}", "ERROR")
            return False
        except Exception as e:
            self.log(f"Unexpected connection error: {str(e)}", "ERROR")
            return False

    def _test_basic_communication(self):
        """Test if device responds to a basic query"""
        try:
            # Try to read motor status register (0x0006)
            response = self.read_register(REG_STATUS, 1)

            # If we got a response that's not None and not an echo, communication works
            if response is not None:
                self.log(f"Device communication test successful", "INFO")
                return True
            else:
                self.log(f"Device communication test failed - no response", "WARNING")
                return False
        except Exception as e:
            self.log(f"Communication test error: {str(e)}", "ERROR")
            return False

    def test_device_id(self, test_id):
        """Test if a specific device ID responds"""
        original_id = self.motor_id
        self.motor_id = test_id

        try:
            # Try a simple status query
            response = self.read_register(REG_STATUS, 1)
            return response is not None
        except:
            return False
        finally:
            self.motor_id = original_id

    def test_baud_rate(self, port, test_baud, bytesize=8, parity='N', stopbits=1):
        """Test if device responds at a specific baud rate"""
        original_connected = self.connected

        try:
            # Temporarily connect with test settings
            success = self.connect(port, test_baud, bytesize, parity, stopbits)
            if success:
                # Test communication
                response = self.read_register(REG_STATUS, 1)
                self.disconnect()
                return response is not None
            return False
        except:
            return False
        finally:
            if original_connected:
                # Restore original connection if it was connected
                pass

            
    def disconnect(self):
        """Disconnect from serial port"""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        self.connected = False
        self.log("Disconnected", "INFO")
        
    def is_connected(self):
        """Check if connected"""
        return self.connected and self.serial_port and self.serial_port.is_open
        
    # ==================== Modbus Communication ====================
    
    def send_command(self, hex_command):
        """Send Modbus command and return response - using reference project approach"""
        if not self.is_connected():
            return None

        try:
            # Convert hex string to bytes
            data = bytes.fromhex(hex_command)

            # Send command
            self.serial_port.write(data)

            # Wait for response (reference project uses 0.1s)
            time.sleep(0.1)

            # Check for response
            if self.serial_port.in_waiting:
                response = self.serial_port.read(self.serial_port.in_waiting)
                # Clear any remaining input (like reference project's flushInput)
                self.serial_port.reset_input_buffer()
                response_hex = response.hex().upper()

                # Debug: Log raw byte counts
                self.log(f"DEBUG: Sent {len(data)} bytes, received {len(response)} bytes", "DEBUG")

                # Check if response starts with the sent command (partial echo)
                if response_hex.startswith(hex_command):
                    # Remove the echoed command from the beginning
                    clean_response = response_hex[len(hex_command):]
                    if clean_response:
                        self.log(f"RX: {clean_response}", "RX")
                        return clean_response
                    else:
                        self.log(f"Echo detected - no actual response data: {response_hex}", "WARNING")
                        return None

                # Check if response is just an echo of what we sent (complete loopback)
                if response_hex == hex_command:
                    self.log(f"Echo detected - no device response: {response_hex}", "WARNING")
                    return None

                # Check if response is too short to be valid Modbus
                if len(response_hex) < 4:  # Minimum: address + function + CRC
                    self.log(f"Response too short: {response_hex}", "WARNING")
                    return None

                return response_hex
            else:
                self.log(f"No response received for command: {hex_command}", "WARNING")
                return None

        except Exception as e:
            self.log(f"Communication error: {str(e)}", "ERROR")
            return None
            
    def write_register(self, address, value):
        """Write single register (function code 0x06)"""
        value_hex = format(value & 0xFFFF, '04X')
        addr_hex = format(address, '04X')
        command = f"{self.motor_id:02X}06{addr_hex}{value_hex}"
        command += calc_crc(command)
        self.log(f"TX: {command}", "TX")
        response = self.send_command(command)
        if response:
            self.log(f"RX: {response}", "RX")
        return response

    def write_register_value(self, address, value):
        """Write single register value and return success boolean"""
        response = self.write_register(address, value)
        return response is not None
        
    def read_register(self, address, count=1):
        """Read register(s) (function code 0x03)"""
        count_hex = format(count, '04X')
        addr_hex = format(address, '04X')
        command = f"{self.motor_id:02X}03{addr_hex}{count_hex}"
        command += calc_crc(command)
        self.log(f"TX: {command}", "TX")
        response = self.send_command(command)
        # Note: send_command already logs the RX response, so no need to log again
        return response
        
    def write_multiple_registers(self, start_addr, values):
        """Write multiple consecutive registers (function code 0x10)"""
        if isinstance(values, int):
            values = [values]

        # Build command: slave_id + func(0x10) + start_addr + reg_count + byte_count + values
        reg_count = len(values)
        byte_count = reg_count * 2
        addr_hex = format(start_addr, '04X')
        count_hex = format(reg_count, '04X')
        byte_hex = format(byte_count, '02X')

        # Convert values to hex
        values_hex = ''.join([format(val & 0xFFFF, '04X') for val in values])

        command = f"{self.motor_id:02X}10{addr_hex}{count_hex}{byte_hex}{values_hex}"
        command += calc_crc(command)

        self.log(f"TX: {command}", "TX")
        response = self.send_command(command)
        if response:
            self.log(f"RX: {response}", "RX")
        return response

    def write_32bit_register(self, low_addr, high_addr, value):
        """Write 32-bit value to two consecutive registers using single command"""
        low_word = value & 0xFFFF
        high_word = (value >> 16) & 0xFFFF
        # Write low word first to low_addr, then high word to high_addr
        return self.write_multiple_registers(low_addr, [low_word, high_word])
        
    def read_32bit_register(self, low_addr, high_addr):
        """Read 32-bit value from two consecutive registers in a single command"""
        # Read 2 consecutive registers starting from low_addr
        resp = self.read_register(low_addr, 2)

        if resp and len(resp) >= 12:  # Expected: slave_id(2) + func(2) + bytes(2) + data(8) + crc(4) = min 16, but we check for 12 to get the data
            try:
                # Extract the data portion (skip slave_id, func, bytes, crc)
                data_hex = resp[6:-4] if len(resp) >= 16 else resp[6:]  # Remove header and CRC
                if len(data_hex) >= 8:
                    low_val = int(data_hex[0:4], 16)  # Low word (first register)
                    high_val = int(data_hex[4:8], 16)  # High word (second register)
                    return (high_val << 16) | low_val
            except:
                pass
        return None
        
    # ==================== Motion Control Functions ====================
    
    def relative_move_wait(self, pulses):
        """Relative position control - wait for completion (Register 0x00CE/0x00CF)"""
        if self.running:
            self.log("Motor is running, cannot execute", "WARNING")
            return False
            
        self.log(f"Relative Move Wait: {pulses} pulses", "INFO")
        self.running = True
        result = self.write_32bit_register(REG_RELATIVE_MOVE_WAIT, REG_RELATIVE_MOVE_WAIT_HIGH, pulses)
        self.running = False
        return result is not None
        
    def relative_move_immediate(self, pulses):
        """Relative position control - immediate execution (Register 0x00DE/0x00DF)"""
        self.log(f"Relative Move Immediate: {pulses} pulses (interrupt current action)", "INFO")
        self.running = True
        result = self.write_32bit_register(REG_RELATIVE_MOVE_IMM_LOW, REG_RELATIVE_MOVE_IMM_HIGH, pulses)
        self.running = True  # Keep running until stopped
        return result is not None
        
    def absolute_move_wait(self, position):
        """Absolute position control - wait for completion (Register 0x00D0/0x00D1)"""
        if self.running:
            self.log("Motor is running, cannot execute", "WARNING")
            return False
            
        self.log(f"Absolute Move Wait: position {position}", "INFO")
        self.running = True
        result = self.write_32bit_register(REG_ABSOLUTE_MOVE_WAIT, REG_ABSOLUTE_MOVE_WAIT_HIGH, position)
        self.running = False
        return result is not None
        
    def absolute_move_immediate(self, position):
        """Absolute position control - immediate execution (Register 0x00E8/0x00E9)"""
        self.log(f"Absolute Move Immediate: position {position} (interrupt current action)", "INFO")
        self.running = True
        result = self.write_32bit_register(REG_ABSOLUTE_MOVE_IMM_LOW, REG_ABSOLUTE_MOVE_IMM_HIGH, position)
        self.running = True
        return result is not None
        
    def emergency_stop(self):
        """Emergency stop - immediately stop motor"""
        self.log("Emergency stop sent", "WARNING")
        self.running = False
        return self.write_register(REG_CONTROL_MODE, CONTROL_STOP)
        
    def return_origin(self):
        """Return to origin (zero position)"""
        self.log("Returning to origin...", "INFO")
        self.running = True
        result = self.write_register(REG_RETURN_HOME, 1)
        self.running = False
        self.log("Returned to origin", "SUCCESS")
        return result is not None
        
    def continuous_forward(self, speed=None):
        """Continuous forward motion using register 0x00C8"""
        if speed:
            self.set_speed(speed)
        self.log("Continuous Forward started", "INFO")
        self.running = True
        return self.write_register(REG_CONTINUOUS_MOTION, CONTINUOUS_FORWARD)

    def continuous_backward(self, speed=None):
        """Continuous backward motion using register 0x00C8"""
        if speed:
            self.set_speed(speed)
        self.log("Continuous Backward started", "INFO")
        self.running = True
        return self.write_register(REG_CONTINUOUS_MOTION, CONTINUOUS_BACKWARD)

    def decel_stop(self):
        """Deceleration stop using register 0x00C8"""
        self.log("Deceleration stop activated", "INFO")
        self.running = False
        return self.write_register(REG_CONTINUOUS_MOTION, CONTINUOUS_DECEL_STOP)

    def immed_stop(self):
        """Immediate stop using register 0x00C8"""
        self.log("Immediate stop activated", "INFO")
        self.running = False
        return self.write_register(REG_CONTINUOUS_MOTION, CONTINUOUS_IMMED_STOP)

    def stop_motion(self):
        """Stop motor motion"""
        self.log("Motor stopped", "INFO")
        self.running = False
        return self.write_register(REG_CONTROL_MODE, CONTROL_STOP)
        
    # ==================== Parameter Setting ====================
    
    def set_speed(self, speed):
        """Set motor speed (pulses/second)"""
        if speed < 0:
            speed = abs(speed)
        self.log(f"Setting speed: {speed} pulses/sec", "INFO")
        return self.write_32bit_register(REG_SPEED_LOW, REG_SPEED_HIGH, speed)
        
    def set_acceleration(self, acceleration):
        """Set acceleration"""
        if acceleration < 0:
            acceleration = abs(acceleration)
        self.log(f"Setting acceleration: {acceleration}", "INFO")
        return self.write_32bit_register(REG_ACCEL_LOW, REG_ACCEL_HIGH, acceleration)
        
    def set_slave_address(self, address):
        """Set motor ID (slave address)"""
        if 1 <= address <= 247:
            old_id = self.motor_id
            self.motor_id = address
            self.log(f"Motor ID changed: {old_id} -> {address}", "SUCCESS")
            return True
        self.log("Invalid motor ID (1-247)", "ERROR")
        return False
        
    # ==================== Status Reading ====================
    
    def read_current_position(self):
        """Read current absolute position"""
        pos = self.read_32bit_register(REG_POSITION_QUERY_LOW, REG_POSITION_QUERY_HIGH)
        if pos is not None and pos >= 0x80000000:
            pos -= 0x100000000
        return pos
        
    def read_current_speed(self):
        """Read current speed"""
        return self.read_32bit_register(REG_SPEED_LOW, REG_SPEED_HIGH)
        
    def read_motor_status(self):
        """Read motor status"""
        resp = self.read_register(REG_STATUS, 1)
        if resp and len(resp) >= 8:
            try:
                status = int(resp[-4:], 16)
                return STATUS_MAPPING.get(status, f"Unknown({status})")
            except:
                pass
        return "Unknown"
        
    def read_fault_info(self):
        """Read fault information"""
        resp = self.read_register(REG_FAULT, 1)
        if resp and len(resp) >= 8:
            try:
                fault = int(resp[-4:], 16)
                return FAULT_MAPPING.get(fault, f"Unknown({fault})")
            except:
                pass
        return "No Fault"
        
    def read_register_value(self, address):
        """Read specific register value"""
        resp = self.read_register(address, 1)
        if resp and len(resp) >= 8:
            try:
                # Parse Modbus response format: SlaveID(2) + Func(2) + DataLen(2) + Data(4) + CRC(4)
                # Example: 0103020064B9AF -> Data is 0064
                if len(resp) >= 10:  # Minimum valid response
                    data_part = resp[6:-4]  # Extract data between length byte and CRC
                    if len(data_part) >= 4:  # At least 2 bytes of data
                        return int(data_part[:4], 16)  # Take first 2 bytes as the value
            except Exception as e:
                self.log(f"Error parsing register value: {e}", "ERROR")
                pass
        return None

    def read_idle_current_value(self, address):
        """Read idle current value - special parsing for last 2 bytes before CRC"""
        resp = self.read_register(address, 1)
        if resp and len(resp) >= 8:
            try:
                # For Idle Current, take the last 2 bytes before CRC
                # Example: 010302190AXXXX -> value is 0A (last 2 chars before CRC)
                if len(resp) >= 8:
                    value_hex = resp[-6:-4]  # Last 2 bytes before CRC
                    return int(value_hex, 16)
            except Exception as e:
                self.log(f"Error parsing idle current value: {e}", "ERROR")
                pass
        return None

    def send_hex_command(self, hex_command, add_crc=True):
        """Send hex command string and return success boolean"""
        if not self.is_connected():
            self.log("Cannot send command: Not connected to serial port", "ERROR")
            return False

        try:
            # Remove spaces and convert to uppercase
            hex_command = hex_command.replace(' ', '').upper()

            # Validate hex string
            if not hex_command:
                self.log("Empty hex command", "ERROR")
                return False

            # Check if hex string has even length (each byte needs 2 hex chars)
            if len(hex_command) % 2 != 0:
                self.log(f"Invalid hex command length: {hex_command}", "ERROR")
                return False

            # Validate that all characters are valid hex
            try:
                int(hex_command, 16)
            except ValueError:
                self.log(f"Invalid hex characters in command: {hex_command}", "ERROR")
                return False

            # Add CRC if requested
            if add_crc:
                crc = calc_crc(hex_command)
                if not hex_command.endswith(crc):
                    hex_command += crc

            # Send command
            data = bytes.fromhex(hex_command)
            self.serial_port.write(data)
            time.sleep(0.1)

            # Read response if available
            if self.serial_port.in_waiting:
                response = self.serial_port.read(self.serial_port.in_waiting)
                self.log(f"RX: {response.hex().upper()}", "RX")

            self.log(f"TX: {hex_command}", "TX")
            return True

        except Exception as e:
            self.log(f"Error sending hex command: {str(e)}", "ERROR")
            return False


if __name__ == "__main__":
    # Test basic functionality
    controller = StepperMotorController()
    ports = controller.scan_ports()
    print(f"Available ports: {ports}")
