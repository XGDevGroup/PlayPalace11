# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path


CLIENT_DIR = Path(SPECPATH)

a = Analysis(
    [str(CLIENT_DIR / 'client.py')],
    pathex=[str(CLIENT_DIR)],
    binaries=[],
    datas=[(str(CLIENT_DIR / 'sounds'), 'sounds')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PlayPalace',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='PlayPalace',
)
app = BUNDLE(
    coll,
    name='PlayPalace.app',
    icon=str(CLIENT_DIR / 'assets' / 'playpalace.icns'),
    bundle_identifier='com.xgdevgroup.playpalace',
)
