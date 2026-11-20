# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for ePICRPG (run from desktop/ or via build_exe.py)

import os

_SPECDIR = os.path.dirname(os.path.abspath(SPEC))
_ROOT = os.path.dirname(_SPECDIR)
_CORE = os.path.join(_ROOT, "core")

a = Analysis(
    [os.path.join(_SPECDIR, "launcher.py")],
    pathex=[_SPECDIR, _CORE, _ROOT],
    binaries=[],
    datas=[
        (os.path.join(_ROOT, "version.py"), "."),
        (os.path.join(_CORE, "locales.py"), "."),
        (os.path.join(_CORE, "classes.py"), "."),
        (os.path.join(_CORE, "player.py"), "."),
        (os.path.join(_CORE, "items.py"), "."),
        (os.path.join(_CORE, "inventory.py"), "."),
        (os.path.join(_CORE, "combat.py"), "."),
        (os.path.join(_CORE, "save_system.py"), "."),
        (os.path.join(_CORE, "ui.py"), "."),
        (os.path.join(_CORE, "events.py"), "."),
        (os.path.join(_CORE, "events_data.py"), "."),
        (os.path.join(_CORE, "skills.py"), "."),
    ],
    hiddenimports=[
        "tkinter",
        "tkinter.ttk",
        "tkinter.scrolledtext",
        "tkinter.messagebox",
        "tkinter.simpledialog",
        "json",
        "random",
        "os",
        "datetime",
        "uuid",
        "decimal",
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
    name="ePICRPG",
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
