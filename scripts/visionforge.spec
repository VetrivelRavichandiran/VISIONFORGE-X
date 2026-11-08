# VISIONFORGE X - PyInstaller Spec File

import sys
from PySide6.QtCore import QCoreApplication

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config/', 'config/'),
        ('storage/', 'storage/'),
        ('logs/', 'logs/'),
    ],
    hiddenimports=[
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'PySide6.QtCore',
        'cv2',
        'numpy',
        'PIL',
        'reportlab',
        'pydantic',
        'pytest',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='VISIONFORGE_X',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here
)
