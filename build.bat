@echo off
REM Build standalone executable for Windows

echo ====================================
echo Building Standalone Executable
echo ====================================
echo.

REM Check if venv exists
if not exist "venv" (
    echo ERROR: Virtual environment not found!
    echo Please run setup.bat first
    pause
    exit /b 1
)

REM Activate venv
call venv\Scripts\activate.bat

REM Check if PyInstaller is installed
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

REM Run build script
python build_executable.py

echo.
echo Build complete! Executable is in the 'dist' folder
pause
