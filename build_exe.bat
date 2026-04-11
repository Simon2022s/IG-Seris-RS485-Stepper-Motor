@echo off
REM Build EXE for RS485 Stepper Motor Controller
REM This batch file creates a standalone executable with updated version query and work speed functionality

setlocal

echo Building RS485 Stepper Motor Controller executable...
echo =======================================================

REM Check if PyInstaller is available
pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo Error: PyInstaller is not installed or not in PATH
    echo Installing PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo Failed to install PyInstaller
        pause
        exit /b 1
    )
)

REM Verify required files exist
echo Checking required files...
if not exist "main.py" (
    echo Error: main.py not found
    pause
    exit /b 1
)
if not exist "RS485_Stepper_Controller.spec" (
    echo Error: RS485_Stepper_Controller.spec not found
    pause
    exit /b 1
)
if not exist "logo.ico" (
    echo Warning: logo.ico not found - executable will use default icon
) else (
    echo ✓ logo.ico found - will be included in executable
)

REM Clean previous build artifacts
echo Cleaning previous build...
if exist "build" rmdir /s /q "build"
if exist "__pycache__" rmdir /s /q "__pycache__"

REM Create dist directory if it doesn't exist
if not exist "dist" mkdir "dist"

REM Build the executable using spec file
echo Building executable with PyInstaller...
echo This may take a few minutes...
pyinstaller --clean RS485_Stepper_Controller.spec

if %errorlevel% equ 0 (
    echo.
    echo =======================================================
    echo BUILD SUCCESSFUL!
    echo =======================================================
    echo Executable created: dist\RS485_Stepper_Controller.exe
    echo.
    echo New features included in this build:
    echo - Automatic version number detection from device
    echo - Connection title shows version (Connection ~v.XXX)
    echo - Version-aware Work Speed register selection:
    echo   * Version >= 113: Uses register 0x00D8 (0.01 RPM units)
    echo   * Version  < 113: Uses register 0x009A (direct RPM)
    echo - Automatic version query on connect and motor ID change
    echo.
    echo The logo.ico has been included in the executable.
    echo You can now distribute this executable without requiring Python installation.
    echo =======================================================
) else (
    echo.
    echo =======================================================
    echo BUILD FAILED with error code %errorlevel%
    echo =======================================================
    echo Check the output above for details.
    echo Common issues:
    echo - Missing Python packages (install with: pip install -r requirements.txt)
    echo - Missing source files
    echo - PyInstaller configuration issues
    echo =======================================================
)

pause
endlocal