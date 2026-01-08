#!/bin/bash
# Setup script for macOS/Linux
# This creates a virtual environment and installs all dependencies

set -e

echo "===================================="
echo "Alembic to JSX Converter - Setup"
echo "===================================="
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
echo "✓ Found Python $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install basic dependencies
echo "Installing Python dependencies..."
pip install numpy imath pyinstaller

# Install Alembic
echo ""
echo "===================================="
echo "Installing Alembic Python bindings"
echo "===================================="
echo ""
echo "Attempting to install via conda-forge..."
echo ""

# Check if conda is available
if command -v conda &> /dev/null; then
    echo "✓ Conda found, installing Alembic..."
    conda install -c conda-forge alembic -y
else
    echo "⚠ Conda not found. Attempting pip installation..."

    # Try pip (may not work on all systems)
    pip install alembic || {
        echo ""
        echo "================================================"
        echo "WARNING: Automatic Alembic installation failed"
        echo "================================================"
        echo ""
        echo "Please install Alembic manually using one of these methods:"
        echo ""
        echo "1. Using Conda (recommended):"
        echo "   conda install -c conda-forge alembic"
        echo ""
        echo "2. Build from source:"
        echo "   https://github.com/alembic/alembic"
        echo ""
        echo "3. System package manager:"
        echo "   - Ubuntu/Debian: sudo apt-get install libalembic-dev python3-alembic"
        echo "   - macOS (Homebrew): brew install alembic"
        echo ""
        exit 1
    }
fi

echo ""
echo "===================================="
echo "Setup Complete!"
echo "===================================="
echo ""
echo "To run the converter:"
echo "  1. Activate the environment: source venv/bin/activate"
echo "  2. Run the GUI: python a2j_gui.py"
echo ""
echo "Or use the run script: ./run.sh"
echo ""
