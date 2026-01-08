@echo off
REM Run script for Windows
REM Activates venv and launches the GUI

if not exist "venv" (
    echo Virtual environment not found!
    echo Please run setup.bat first
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
python a2j_gui.py
