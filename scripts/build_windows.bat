@echo off
REM VISIONFORGE X - Windows Build Script
echo ========================================
echo VISIONFORGE X - Windows Build
echo ========================================

REM Check Python
python --version
if errorlevel 1 (
    echo Python not found. Please install Python 3.11+
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
pip install -r desktop_app\requirements.txt
pip install pyinstaller

REM Run tests
echo Running tests...
cd desktop_app
pytest tests/ -v
if errorlevel 1 (
    echo Tests failed. Fix issues before building.
    cd ..
    exit /b 1
)
cd ..

REM Build with PyInstaller
echo Building executable...
pyinstaller scripts\visionforge.spec

echo ========================================
echo Build complete!
echo Executable: dist\VISIONFORGE_X.exe
echo ========================================
