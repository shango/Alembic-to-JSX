@echo off
REM ==============================================================================
REM Alembic to JSX Converter - Windows Build Script
REM Creates a standalone .exe file using PyInstaller
REM ==============================================================================

echo ====================================
echo Building Windows Executable
echo ====================================
echo.

REM Check if venv exists
if not exist "venv" (
    echo ERROR: Virtual environment not found!
    echo Please run setup_windows.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if PyInstaller is installed
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    python -m pip install pyinstaller
)

REM Try to run pyinstaller - if not found, use python -m PyInstaller
where pyinstaller >nul 2>&1
if errorlevel 1 (
    echo.
    echo Note: Using 'python -m PyInstaller' instead of 'pyinstaller' command
    set PYINSTALLER_CMD=python -m PyInstaller
) else (
    set PYINSTALLER_CMD=pyinstaller
)

REM Clean previous builds
if exist "build" (
    echo Cleaning previous build...
    rmdir /s /q build
)
if exist "dist" (
    rmdir /s /q dist
)
if exist "AlembicToJSX.spec" (
    del AlembicToJSX.spec
)

echo.
echo ====================================
echo Running PyInstaller...
echo ====================================
echo.

REM Build the executable
%PYINSTALLER_CMD% ^
    --name=AlembicToJSX ^
    --onefile ^
    --windowed ^
    --clean ^
    --noconfirm ^
    --hidden-import=alembic ^
    --hidden-import=alembic.Abc ^
    --hidden-import=alembic.AbcGeom ^
    --hidden-import=alembic.AbcCoreAbstract ^
    --hidden-import=imath ^
    --hidden-import=imathnumpy ^
    --hidden-import=numpy ^
    --hidden-import=tkinter ^
    --collect-all=alembic ^
    --collect-all=imath ^
    --add-data="README.md;." ^
    a2j_gui.py

if errorlevel 1 (
    echo.
    echo ====================================
    echo Build Failed!
    echo ====================================
    pause
    exit /b 1
)

echo.
echo ====================================
echo Build Complete!
echo ====================================
echo.
echo Executable location: dist\AlembicToJSX.exe
echo.
echo File size:
dir dist\AlembicToJSX.exe | find "AlembicToJSX.exe"
echo.
echo You can now distribute dist\AlembicToJSX.exe to users!
echo.
echo Users will also need:
echo   - Microsoft Visual C++ Redistributable 2015-2022
echo     Download: https://aka.ms/vs/17/release/vc_redist.x64.exe
echo.
pause
