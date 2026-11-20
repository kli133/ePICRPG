#!/usr/bin/env bash
# Create a dedicated venv for Buildozer (PEP 668) and build debug APK.
set -euo pipefail

WIN_SRC="${WIN_SRC:-/mnt/c/Users/user/Desktop/rpg}"
WSL_DST="${WSL_DST:-$HOME/epicrpg}"
VENV="${HOME}/epicrpg-build-venv"

echo "==> Sync ${WIN_SRC} -> ${WSL_DST}"
mkdir -p "${WSL_DST}"
rsync -a --delete \
  --exclude '.venv/' --exclude 'venv/' --exclude '.git/' --exclude 'dist/' --exclude 'build/' \
  --exclude 'docs/' --exclude 'tests/' --exclude 'upx-*/' --exclude 'android/.data/' \
  --exclude 'android/.buildozer/' --exclude 'android/bin/' --exclude '__pycache__/' --exclude '*.pyc' \
  "${WIN_SRC}/" "${WSL_DST}/"

if [[ ! -x "${VENV}/bin/buildozer" ]]; then
  echo "==> Creating venv ${VENV}"
  python3 -m venv "${VENV}"
  # shellcheck disable=SC1091
  source "${VENV}/bin/activate"
  pip install -U pip wheel setuptools
  pip install 'buildozer' 'cython==0.29.37' 'virtualenv' \
    'appdirs' 'colorama>=0.3.3' 'jinja2' 'sh>=2,<3.0' \
    'meson' 'ninja' 'build' 'toml' 'packaging' 'wheel~=0.43.0'
else
  # shellcheck disable=SC1091
  source "${VENV}/bin/activate"
fi

export PATH="${VENV}/bin:${PATH}"
# Avoid host pip --user installs during buildozer platform setup
export PIP_BREAK_SYSTEM_PACKAGES=1

cd "${WSL_DST}/android"
echo "==> buildozer $($(command -v buildozer) --version 2>/dev/null || true)"
buildozer -v android debug

mkdir -p "${WIN_SRC}/android/bin"
cp -v bin/*.apk "${WIN_SRC}/android/bin/" 2>/dev/null || true
ls -la bin/*.apk "${WIN_SRC}/android/bin/" 2>/dev/null || true
echo BUILD_OK
