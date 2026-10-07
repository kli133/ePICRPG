# ePICRPG Executable Build Guide

## How to use the EXE

1. **Location**: The compiled executable is in the `dist/` folder:
   - `dist/ePICRPG.exe` — the main game executable

2. **Running the game**:
   - Double-click `ePICRPG.exe` to launch
   - Or run from command line: `ePICRPG.exe`

3. **Save files**:
   - Save slots will be created in the same directory as the EXE
   - Ensure you have write permissions in the folder

## Building/Rebuilding the EXE

To rebuild after making code changes:

```bash
python build_exe.py
```

This will:

1. Check for PyInstaller (install if missing)
2. Build the EXE from `ePICRPG.spec`
3. Output to `dist/ePICRPG.exe`


## What's included in the build

- All game modules (gui_main.py, player.py, items.py, etc.)
- Python runtime (no separate Python installation needed)
- All dependencies (tkinter is bundled)

## Version updates

When updating the game version:
1. Edit `version.py` and change the `VERSION` string
2. Rebuild with `python build_exe.py`
3. The new EXE will have the updated version in the title bar

## Troubleshooting

- **EXE doesn't run**: Ensure you're using a recent Windows version (Windows 7+ recommended)
- **Slow startup**: First run may be slow as Windows validates the executable; subsequent runs are faster
- **Antivirus warnings**: PyInstaller bundles may trigger antivirus warnings; this is normal for self-contained executables
