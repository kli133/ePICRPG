#!/usr/bin/env bash
set -euo pipefail
APK="${1:-/root/epicrpg/android/bin/epicrpg-2.2.9-arm64-v8a-debug.apk}"
TMP=/tmp/epicrpg-apk-inspect
rm -rf "$TMP"
mkdir -p "$TMP/private"
cd "$TMP"
unzip -q -o "$APK" "assets/private.tar"
tar -xf assets/private.tar -C private
echo "=== top ==="
ls -la private | head -50
echo "=== android? ==="
ls -la private/android 2>&1 | head -30 || true
echo "=== main.py files ==="
find private -name 'main.py' -print
echo "=== game_session ==="
find private -name 'game_session.py' -print
echo DONE
