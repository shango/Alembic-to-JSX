#!/bin/bash
# Run script for macOS/Linux
# Activates venv and launches the GUI

if [ ! -d "venv" ]; then
    echo "Virtual environment not found!"
    echo "Please run ./setup.sh first"
    exit 1
fi

source venv/bin/activate
python a2j_gui.py
