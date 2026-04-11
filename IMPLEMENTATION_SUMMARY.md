# RS485 Stepper Motor Controller - Version Query & Work Speed Implementation

## Overview
This implementation adds version-aware functionality to the RS485 Stepper Motor Controller, enabling automatic detection of device firmware version and appropriate register selection for Work Speed operations.

## Features Implemented

### 1. Automatic Version Detection
- **Register**: 0x0002-0x0003 (Driver Software Version Number)
- **Query Command**: `01 03 00 02 00 02 65 CB` (for station 1)
- **Response Format**: ASCII-encoded version string converted to numeric value
- **Trigger**: Automatically queries version when:
  - Connection is established
  - Motor ID (station) is changed

### 2. Connection Title Update
- **Before**: "Connection"
- **After**: "Connection ~v.{version_number}"
- **Example**: "Connection ~v.113"
- **Behavior**: Updates dynamically based on detected version

### 3. Version-Aware Work Speed Control

#### For Version >= 113:
- **Register**: 0x00D8-0x00D9 (32-bit)
- **Units**: 0.01 RPM
- **Query Command**: `01 03 00 D8 00 02` + CRC
- **Example Response**: `01 03 04 75 30 00 00` + CRC
- **Data Extraction**: 0x7530 = 30000 → 30000 × 0.01 = 300 RPM
- **Write Process**: Input RPM × 100 → Convert to hex → Split into low/high words

#### For Version < 113:
- **Register**: 0x009A (16-bit)
- **Units**: Direct RPM
- **Query Command**: `01 03 00 9A 00 01` + CRC
- **Example Response**: `01 03 02 01 2C` + CRC
- **Data Extraction**: 0x012C = 300 RPM (direct value)
- **Write Process**: Input RPM → Convert directly to hex

## Files Modified

### 1. `stepper_motor_controller.py`
- **Added**: `read_version_number()` method
  - Reads registers 0x0002-0x0003
  - Parses ASCII-encoded version data
  - Extracts numeric version for comparison

- **Added**: `get_work_speed_register_strategy()` method
  - Determines appropriate register based on version
  - Returns strategy ("32bit" or "16bit") and version number

- **Added**: `read_work_speed()` method
  - Uses version-appropriate register for reading
  - Handles unit conversion (0.01 RPM vs direct RPM)

- **Added**: `write_work_speed()` method
  - Uses version-appropriate register for writing
  - Handles value scaling and register splitting

### 2. `gui.py`
- **Added**: `version_number` instance variable
- **Added**: `connection_group` reference for title updates
- **Added**: `update_connection_title()` method
- **Added**: `query_version_number()` method
- **Modified**: `update_ui_state()` to query version on connection
- **Modified**: `on_set_motor_id_param_clicked()` to requery version
- **Replaced**: Work Speed query/set methods with version-aware versions

### 3. `build_exe.bat`
- **Updated**: Enhanced build script with better error handling
- **Added**: Feature summary in build completion message
- **Verified**: logo.ico inclusion in executable

## Usage Examples

### Version Query
```python
controller = StepperMotorController()
controller.connect("COM3", 9600)
version = controller.read_version_number()
print(f"Device version: {version}")  # e.g., 113
```

### Work Speed Operations
```python
# Reading work speed (automatic register selection)
speed = controller.read_work_speed()
print(f"Current speed: {speed} RPM")

# Setting work speed (automatic register selection)
controller.write_work_speed(200)  # Sets 200 RPM
```

### GUI Behavior
1. Click "Connect" → Version automatically queried → Title updates to "Connection ~v.113"
2. Change Motor ID → Version requeried with new station → Title updates if version differs
3. Click "?" on Work Speed → Appropriate register used based on version
4. Click "Set" on Work Speed → Appropriate register used with correct scaling

## Technical Details

### Version Detection Algorithm
1. Send Modbus command: `[station] 03 00 02 00 02` + CRC
2. Parse response: Extract 4 bytes of version data
3. Convert hex to ASCII string
4. Extract first numeric value found
5. Return integer version for comparison

### Register Strategy Selection
```python
if version >= 113:
    use_register_0x00D8_32bit()
else:
    use_register_0x009A_16bit()
```

### Error Handling
- Version query failures default to 32-bit strategy (newer version)
- Graceful fallback if device doesn't respond to version query
- Connection state verification before version queries

## Testing
Run `test_version_functionality.py` to verify:
- CRC calculation for version query command
- Register strategy selection logic
- Command format matches UserManual.pdf specification

## Build Instructions
1. Ensure all source files are updated
2. Run `build_exe.bat` to create executable
3. Executable includes logo.ico and all new functionality
4. Output: `dist\RS485_Stepper_Controller.exe`

## Compatibility
- **Backward Compatible**: Works with devices of any version
- **Forward Compatible**: Newer versions automatically use optimal registers
- **Fallback**: Version detection failures default to newer version behavior