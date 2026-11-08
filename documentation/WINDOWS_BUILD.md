# VISIONFORGE X - Windows Build Guide

## Prerequisites
- Windows 10/11
- Python 3.11+
- PyInstaller

## Build Steps

1. Install dependencies:
```bash
pip install -r requirements.txt
pip install pyinstaller
```

2. Build with PyInstaller:
```bash
pyinstaller visionforge.spec
```

3. The executable will be in `dist/`

## PyInstaller Spec File

See `scripts/visionforge.spec` for the complete configuration including:
- Hidden imports for PySide6 plugins
- OpenCV data files
- Database initialization
- Resource path handling

## Running the Packaged App

```
dist/VISIONFORGE_X.exe
```

## Troubleshooting

- **Missing Qt plugins**: Ensure `--collect-all PySide6` is in the spec
- **OpenCV errors**: Include `cv2` data files in analysis
- **Database errors**: Initialize DB on first run in app data directory
