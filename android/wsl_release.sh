#!/usr/bin/env bash
# Build signed *release* APK (installable like a normal game APK).
# Usage:
#   wsl -d Ubuntu -- bash /mnt/c/Users/user/Desktop/rpg/android/wsl_release.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
sed -i 's/\r$//' "${SCRIPT_DIR}/_wsl_venv_release.sh" 2>/dev/null || true
exec bash "${SCRIPT_DIR}/_wsl_venv_release.sh"
