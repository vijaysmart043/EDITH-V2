# -*- mode: python ; coding: utf-8 -*-
# PyInstaller specification for EDITH — Windows Desktop AI Assistant
# Developed by G.Vijay Raj (vijay smart)

import os
import sys
from PyInstaller.utils.hooks import collect_all, collect_submodules

block_cipher = None

# Collect submodules and data
added_files = [
    ('assets', 'assets'),
    ('app', 'app'),
    ('LICENSE', '.'),
]

hidden_imports = [
    'PySide6',
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'sqlite3',
    'psutil',
    'ctypes',
    'sounddevice',
    'numpy',
    'speech_recognition',
    'pyttsx3',
    'google.genai',
    'google.generativeai',
]

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=added_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'scipy', 'pandas', 'IPython'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher,
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='EDITH',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for native Windows GUI/tray app (no cmd window)
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icons/edith.ico' if os.path.exists('assets/icons/edith.ico') else None,
    version_info=None,
)
