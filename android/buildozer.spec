[app]

# (str) Title of your application
title = ePICRPG

# (str) Package name
package.name = epicrpg

# (str) Package domain (needed for android/ios packaging)
package.domain = org.epicrpg

# (str) Source code where the main.py live — repo root (Buildozer entry: ../main.py)
source.dir = ..

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,json,ttf,otf,wav,ogg,mp3

# (list) List of inclusions using patterns matching directories
source.include_patterns = android/*,android/assets/*,android/assets/fonts/*,android/screens/*,core/*,*.py

# (list) List of directory to exclude
source.exclude_dirs = tests,docs,build,dist,.venv,venv,upx-5.1.0-win64,.git,__pycache__,android/.data,android/.buildozer,android/bin,.buildozer,desktop,node_modules,private

# (list) List of patterns to exclude (desktop-only / tooling)
source.exclude_patterns = license,images/*/*.jpg,**/gui_main.py,**/launcher.py,**/build_exe.py,**/ePICRPG.spec,**/__pycache__/*,**/*.pyc,android/_wsl_*.sh,android/bin_build_log.txt

# (str) Application versioning (method 1) — keep in sync with version.py when releasing
version = 2.2.9

# (list) Application requirements
requirements = python3,kivy

# (str) Presplash background color (used if no splash image)
android.presplash_color = #1E2026

# (str) Icon/presplash of the application (relative to this .spec location via source.dir)
icon.filename = %(source.dir)s/android/assets/icon.png
presplash.filename = %(source.dir)s/android/assets/presplash.png

# (str) Supported orientation
orientation = portrait

# (list) Permissions
android.permissions = INTERNET

# (int) Target Android API
android.api = 33

# (int) Minimum API
android.minapi = 21

# (bool) If True, allow network access to accept SDK licenses
android.accept_sdk_license = True

# First debug build: arm64 only (faster). Add armeabi-v7a later if needed.
android.archs = arm64-v8a

# Copy libraries instead of using big APK packaging quirks
android.copy_libs = 1

# Sideload / GitHub Releases need APK (default is aab for Play Store)
android.release_artifact = apk

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root (0 = allow root in WSL)
warn_on_root = 0

# (str) Path to build directory (relative to this .spec file = android/)
build_dir = ./.buildozer

# (str) Path to output directory
bin_dir = ./bin
