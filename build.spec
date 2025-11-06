# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller build specification for GAM Admin Tool.

This file configures how PyInstaller packages the application into
a standalone executable.

To build the executable:
    pyinstaller build.spec

Output will be in the dist/ folder.
"""

import os
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# Determine if icon file exists
icon_file = 'assets/icon.ico'
icon_path = icon_file if os.path.exists(icon_file) else None

# Data files to include (only if they exist)
datas = []
if os.path.exists(icon_file):
    datas.append((icon_file, 'assets'))

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'tkinter.scrolledtext',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary modules to reduce size
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'IPython',
        'notebook',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='GAM_Admin_Tool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for GUI app (no console window)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path  # Will be None if icon doesn't exist
)

# For debugging, you can enable console mode temporarily:
# Change console=False to console=True above

# Notes:
# - The executable will be created in dist/GAM_Admin_Tool.exe (Windows)
# - GAM7 must be installed separately on the target system
# - The executable is self-contained but requires GAM7 in PATH
# - Icon is optional; default Python icon used if not provided
