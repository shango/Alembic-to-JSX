# Windows Build Instructions

Complete guide for building the Alembic to JSX Converter on Windows.

## Prerequisites

### Required Software (Install Before Building)

1. **Python 3.11 or 3.12**
   - Download: https://www.python.org/downloads/
   - ✅ **IMPORTANT**: Check "Add Python to PATH" during installation
   - Verify: Open Command Prompt and run `python --version`

2. **PyAlembic**
   - **⚠️ MUST BE INSTALLED FIRST**
   - Follow official installation instructions for Windows: https://github.com/alembic/alembic
   - Verify installation: `python -c "from alembic.Abc import IArchive; print('OK')"`

3. **Microsoft Visual C++ Redistributable 2015-2022**
   - Download: https://aka.ms/vs/17/release/vc_redist.x64.exe
   - Required for PyAlembic to work
   - Install before running the setup script

4. **Internet Connection**
   - Needed to download NumPy and other Python packages

## Quick Start (2 Steps)

### Step 1: Run Setup

**⚠️ Make sure PyAlembic is installed first!**

```cmd
setup_windows.bat
```

This will:
- ✅ Check Python version
- ✅ Create virtual environment
- ✅ Install NumPy, imath, and other dependencies
- ✅ Verify PyAlembic installation

**Time:** ~1-2 minutes

### Step 2: Build the Executable

```cmd
build_windows.bat
```

This creates: **`dist\AlembicToJSX.exe`**

**Time:** ~5-10 minutes (PyInstaller bundling)

## What Gets Built

After running `build_windows.bat`, you'll have:

```
dist/
  └── AlembicToJSX.exe    (~50-80 MB standalone executable)
```

This **single .exe file** contains:
- Python runtime
- PyAlembic and all dependencies
- Your GUI application
- Everything needed to run!

## Distribution

### For End Users

Distribute these files:
1. **`AlembicToJSX.exe`** - The converter application
2. **Visual C++ Redistributable** - Download link: https://aka.ms/vs/17/release/vc_redist.x64.exe

Users just need to:
1. Install Visual C++ Redistributable (if not already installed)
2. Double-click `AlembicToJSX.exe`
3. Use the GUI to convert files!

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

**Solution:** Install PyAlembic according to the official documentation before running setup:
- https://github.com/alembic/alembic

Verify installation:
```cmd
python -c "from alembic.Abc import IArchive; print('PyAlembic installed successfully')"
```

### Build exe is too large

The .exe will be 50-80 MB because it includes:
- Python runtime (~15 MB)
- NumPy (~20 MB)
- PyAlembic (~15 MB)
- Other dependencies

This is normal for PyInstaller bundles. **No way to make it smaller** without breaking functionality.

### "The code execution cannot proceed because VCRUNTIME140.dll was not found"

**Solution:** Install Visual C++ Redistributable:
https://aka.ms/vs/17/release/vc_redist.x64.exe

## Build Customization

### Change Exe Icon

1. Create or download an `.ico` file (e.g., `icon.ico`)
2. Edit `build_windows.bat` and add:
   ```batch
   --icon=icon.ico ^
   ```
   After the `--windowed` line

### Add Version Information

Edit `build_windows.bat` and add:
```batch
--version-file=version.txt ^
```

Then create `version.txt` with version info.

### Debug Mode

To see console output during execution, change in `build_windows.bat`:
```batch
--windowed ^
```
to:
```batch
--console ^
```

## File Structure After Build

```
alembic_to_jsx/
├── venv/                       # Virtual environment (don't distribute)
├── build/                      # PyInstaller temp files (don't distribute)
├── dist/
│   └── AlembicToJSX.exe       # ✅ DISTRIBUTE THIS
├── setup_windows.bat          # Setup script
├── build_windows.bat          # Build script
└── README.md                  # Documentation
```

## Architecture Support

| Platform | Python 3.11 | Python 3.12 | Status |
|----------|------------|------------|--------|
| Windows x64 (64-bit) | ✅ | ✅ | Fully Supported |
| Windows x86 (32-bit) | ✅ | ✅ | Supported |
| Windows ARM64 | ✅ | ✅ | Supported |

**Note:** Most users have 64-bit Windows. Build with Python 3.11 or 3.12 x64 for maximum compatibility.

## Advanced: Building Portable ZIP

Instead of a single .exe, you can create a folder distribution:

In `build_windows.bat`, change:
```batch
--onefile ^
```
to:
```batch
--onedir ^
```

This creates `dist/AlembicToJSX/` folder with all files. Faster to build, but multiple files to distribute.

## Next Steps

After building:
1. Test the .exe on a clean Windows machine (no Python installed)
2. Create a release on GitHub with the .exe
3. Write user documentation
4. Share with your team!

## Support

For issues with:
- **PyAlembic wheel**: https://github.com/cgohlke/pyalembic-wheels/issues
- **This converter**: Check the main README.md
- **PyInstaller**: https://pyinstaller.org/en/stable/

## Build Time Summary

| Step | Time | Output |
|------|------|--------|
| Setup (first time) | ~2-3 min | venv + packages |
| Build exe | ~5-10 min | dist/AlembicToJSX.exe |
| **Total** | **~7-13 min** | **Ready to distribute!** |

Subsequent builds are faster (~3-5 min) since dependencies are cached.
