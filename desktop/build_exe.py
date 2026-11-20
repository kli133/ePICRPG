#!/usr/bin/env python3
"""Build script for ePICRPG — creates a Windows EXE executable.
Usage (from repo root or desktop/): python desktop/build_exe.py
"""

import os
import shutil
import subprocess
import sys


def main():
    print("=" * 60)
    print("Building ePICRPG Executable...")
    print("=" * 60)

    desk = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(desk)
    os.chdir(desk)

    try:
        __import__("PyInstaller")
        print("[BUILD] PyInstaller found")
    except ImportError:
        print("[BUILD] PyInstaller not found. Installing...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "pyinstaller>=5.0"]
        )

    spec_file = os.path.join(desk, "ePICRPG.spec")
    if not os.path.exists(spec_file):
        print(f"✗ Error: {spec_file} not found!")
        return 1

    print(f"\nBuilding from spec file: {spec_file}")
    print("This may take a minute or two...\n")

    upx_dir = os.environ.get("UPX_DIR")
    upx_bin = shutil.which("upx", path=upx_dir) if upx_dir else shutil.which("upx")
    if not upx_bin:
        bundled_upx = os.path.join(root, "upx-5.1.0-win64", "upx.exe")
        if os.path.exists(bundled_upx):
            upx_bin = bundled_upx

    distpath = os.path.join(root, "dist")
    workpath = os.path.join(root, "build")
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        spec_file,
        f"--distpath={distpath}",
        f"--workpath={workpath}",
    ]
    if upx_bin:
        cmd.append(f"--upx-dir={os.path.dirname(upx_bin)}")
        print(f"[BUILD] UPX detected at: {upx_bin}")
    else:
        print(
            "[BUILD] UPX not found (optional). Set UPX_DIR or add to PATH to enable binary compression."
        )

    try:
        subprocess.run(cmd, check=True)
        print("\n" + "=" * 60)
        print("[BUILD] Build successful!")
        print("=" * 60)
        print("\nExecutable location:")
        print("  dist/ePICRPG.exe")
        print("\nYou can now run the game by double-clicking ePICRPG.exe")
        return 0
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 60)
        print(f"[BUILD] Build failed with error code {e.returncode}")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
