# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for ePICRPG

a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('version.py', '.'),
        ('locales.py', '.'),
        ('classes.py', '.'),
        ('player.py', '.'),
        ('items.py', '.'),
        ('inventory.py', '.'),
        ('combat.py', '.'),
        ('save_system.py', '.'),
        ('ui.py', '.'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.scrolledtext',
        'tkinter.messagebox',
        'tkinter.simpledialog',
        'json',
        'random',
        'os',
        'datetime',
        'uuid',
        'decimal',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ePICRPG',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
