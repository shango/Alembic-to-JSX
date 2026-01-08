#!/bin/bash
# Build standalone executable for macOS/Linux

set -e

echo "===================================="
echo "Building Standalone Executable"
echo "===================================="
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "ERROR: Virtual environment not found!"
    echo "Please run ./setup.sh first"
    exit 1
fi

# Activate venv
source venv/bin/activate

# Check if PyInstaller is installed
if ! python -c "import PyInstaller" &> /dev/null; then
    echo "Installing PyInstaller..."
    pip install pyinstaller
fi

# Run build script
python build_executable.py

echo ""
echo "Build complete! Executable is in the 'dist' folder"
