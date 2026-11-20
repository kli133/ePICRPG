#!/usr/bin/env bash
# Build ePICRPG debug APK inside WSL on ext4 (not /mnt/c).
# Usage:
#   wsl -d Ubuntu -- bash /mnt/c/Users/user/Desktop/rpg/android/wsl_build.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Prefer Windows-tree helper if present, else same-dir after rsync
HELPER="${SCRIPT_DIR}/_wsl_venv_build.sh"
if [[ ! -f "${HELPER}" ]]; then
  HELPER="/mnt/c/Users/user/Desktop/rpg/android/_wsl_venv_build.sh"
fi
sed -i 's/\r$//' "${HELPER}" 2>/dev/null || true
exec bash "${HELPER}"
