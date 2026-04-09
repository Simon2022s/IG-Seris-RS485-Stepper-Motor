@echo off
REM Build EXE for RS485 Stepper Motor Controller
REM This batch file creates a standalone executable

setlocal

echo Building RS485 Stepper Motor Controller executable...

REM Check if PyInstaller is installed
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing PyInstaller...
    pip install pyinstaller
    if %errorlevel% neq 0 (
        echo Failed to install PyInstaller
        pause
        exit /b 1
    )
)

REM Create dist directory if it doesn't exist
if not exist "dist" mkdir "dist"

REM Build the executable using spec file
echo Running PyInstaller with spec file...
pyinstaller --clean RS485_Stepper_Controller.spec

if %errorlevel% equ 0 (
    echo.
    echo Build successful!
    echo Executable created: dist\RS485_Stepper_Controller.exe
    echo.
    echo You can now distribute this executable without requiring Python installation.
) else (
    echo Build failed with error code %errorlevel%
    echo Check the output above for details.
)

pause
endlocal