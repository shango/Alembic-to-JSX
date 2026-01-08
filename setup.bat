@echo off
REM Setup script for Windows
REM This creates a virtual environment and installs all dependencies

echo ====================================
echo Alembic to JSX Converter - Setup
echo ====================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo Checked Python version
python --version

REM Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created
) else (
    echo Virtual environment already exists
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install basic dependencies
echo Installing Python dependencies...
pip install numpy imath pyinstaller

REM Install Alembic
echo.
echo ====================================
echo Installing Alembic Python bindings
echo ====================================
echo.

REM Check if conda is available
where conda >nul 2>&1
if %errorlevel% equ 0 (
    echo Conda found, installing Alembic...
    conda install -c conda-forge alembic -y
) else (
    echo Conda not found. Attempting pip installation...
    pip install alembic
    if errorlevel 1 (
        echo.
        echo ================================================
        echo WARNING: Automatic Alembic installation failed
        echo ================================================
        echo.
        echo Please install Alembic manually using one of these methods:
        echo.
        echo 1. Using Conda ^(recommended^):
        echo    conda install -c conda-forge alembic
        echo.
        echo 2. Build from source:
        echo    https://github.com/alembic/alembic
        echo.
        pause
        exit /b 1
    )
)

echo.
echo ====================================
echo Setup Complete!
echo ====================================
echo.
echo To run the converter:
echo   1. Run: venv\Scripts\activate.bat
echo   2. Run: python a2j_gui.py
echo.
echo Or double-click: run.bat
echo.
pause
