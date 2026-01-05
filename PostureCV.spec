# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all
import sys
import os

# -------------------------------------------------------------------------
# THE NUCLEAR OPTION: Force Collect MediaPipe
# This grabs every binary, data file, and dependency MediaPipe has.
# -------------------------------------------------------------------------
tmp_ret = collect_all('mediapipe')
datas = tmp_ret[0]
binaries = tmp_ret[1]
hiddenimports = tmp_ret[2]

# Add our own assets manually
datas += [('assets', 'assets')]

# Add other libraries we know we need
hiddenimports += ['rumps', 'cv2', 'numpy', 'requests', 'packaging', 'certifi', 'mediapipe.python._framework_bindings']

block_cipher = None

a = Analysis(
    ['posture_app.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PostureCV',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# -------------------------------------------------------------------------
# APP BUNDLE SETTINGS (Icon, Camera, High Res)
# -------------------------------------------------------------------------
app = BUNDLE(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='PostureCV.app',
    icon='icon.icns',
    bundle_identifier='com.richardli.posturecv',
    info_plist={
        'NSCameraUsageDescription': 'PostureCV needs access to your camera to monitor your posture in real-time.',
        'LSUIElement': True, 
        'CFBundleName': 'PostureCV',
        'CFBundleDisplayName': 'PostureCV',
        'CFBundleShortVersionString': '1.0.1',
        'CFBundleVersion': '1.0.1',
        'NSHighResolutionCapable': True,
    },
)