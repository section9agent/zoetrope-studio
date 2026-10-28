# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller spec file for Vinyl Zoetrope Designer
# Run:  pyinstaller vinyl_zoetrope.spec
#
import sys
import os
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None

# Collect all PyQt6 and Pillow data / plugins
added_files = []
added_files += collect_data_files('PIL')

hidden_imports = []
hidden_imports += collect_submodules('PIL')
hidden_imports += [
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'PyQt6.sip',
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
    excludes=[
        'tkinter', 'matplotlib', 'numpy', 'scipy',
        'pandas', 'IPython', 'jupyter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# ── One-folder build (reliable cross-platform) ──────────────────────────────
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ZoetropeStudio',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,          # no terminal window on Windows/macOS
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,              # add icon path here if you have one, e.g. 'icon.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ZoetropeStudio',
)

# ── macOS .app bundle ────────────────────────────────────────────────────────
if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='VinylZoetrope.app',
        icon=None,           # add 'icon.icns' here if you have one
        bundle_identifier='com.yourname.vinylzoetrope',
        info_plist={
            'CFBundleShortVersionString': '1.0.0',
            'CFBundleDisplayName': 'Vinyl Zoetrope Designer',
            'NSHighResolutionCapable': True,
            'NSRequiresAquaSystemAppearance': False,   # respect dark mode
        },
    )
