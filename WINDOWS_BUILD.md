# Windows Build Instructions

Complete guide for building MultiConverter v2.5.0 on Windows.

## Prerequisites

### Required Software

1. **Python 3.11 or 3.12**
   - Download: https://www.python.org/downloads/
   - ✅ **IMPORTANT**: Check "Add Python to PATH" during installation
   - Verify: Open Command Prompt and run `python --version`

2. **Microsoft Visual C++ Redistributable 2015-2022**
   - Download: https://aka.ms/vs/17/release/vc_redist.x64.exe
   - Required for PyAlembic to work

3. **Internet Connection**
   - Needed to download Python packages

## Quick Start (2 Steps)

### Step 1: Run Setup

```cmd
setup.bat
```

This will:
- ✅ Check Python version
- ✅ Create virtual environment
- ✅ Download and install PyAlembic wheel
- ✅ Install NumPy, PyInstaller, and sv_ttk theme
- ✅ Optionally install USD library for multi-format export

### Step 2: Build the Executable

```cmd
build.bat
```

This creates: **`dist\MultiConverter.exe`** - a single standalone executable

## What Gets Built

After running `build.bat`, you'll have:

```
dist/
  └── MultiConverter.exe   (~100-150 MB single file)
```

This single file contains:
- Python runtime
- PyAlembic and all dependencies
- USD library (if installed during setup)
- GUI application with Sun Valley dark theme
- Everything needed to run!

## Distribution

### For End Users

**Package for distribution:**
1. Copy `dist\MultiConverter.exe`
2. Include Visual C++ Redistributable link: https://aka.ms/vs/17/release/vc_redist.x64.exe

**Users need to:**
1. Install Visual C++ Redistributable (if not already installed)
2. Run `MultiConverter.exe`
3. Use the GUI to convert to After Effects, USD, or Maya!

No Python installation needed for end users!

## Troubleshooting

### "Python not found"

**Solution:** Install Python 3.11 or 3.12 and check "Add Python to PATH"

Verify with:
```cmd
python --version
```

### "ModuleNotFoundError: No module named 'alembic'"

**Cause:** PyAlembic not installed

**Solution:** Run `setup.bat` to install all dependencies

### "The code execution cannot proceed because VCRUNTIME140.dll was not found"

**Solution:** Install Visual C++ Redistributable:
https://aka.ms/vs/17/release/vc_redist.x64.exe

## Build Customization

### Change Exe Icon

1. Create or download an `.ico` file (e.g., `icon.ico`)
2. Edit `build.bat` and add after `--windowed`:
   ```batch
   --icon=icon.ico ^
   ```

### Debug Mode

To see console output during execution, change in `build.bat`:
```batch
--windowed ^
```
to:
```batch
--console ^
```

## USD Library Installation

The setup script (`setup.bat`) will prompt you to install USD for multi-format export support.

**Recommended:** Install `usd-core` via pip (Option 3 in setup)
```cmd
pip install usd-core
```

**If USD is not installed:** The converter will still work for After Effects export only. USD and Maya export options will be unavailable.

## Support

For issues with:
- **PyAlembic wheel**: https://github.com/cgohlke/pyalembic-wheels/issues
- **This converter**: Check the main README.md
- **PyInstaller**: https://pyinstaller.org/en/stable/
