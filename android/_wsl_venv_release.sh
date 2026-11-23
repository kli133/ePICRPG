#!/usr/bin/env bash
# Sync project to WSL ext4, ensure release keystore, buildozer android release.
set -euo pipefail

WIN_SRC="${WIN_SRC:-/mnt/c/Users/user/Desktop/rpg}"
WSL_DST="${WSL_DST:-$HOME/epicrpg}"
VENV="${HOME}/epicrpg-build-venv"
KEY_DIR="${HOME}/epicrpg-release-keys"
KEYSTORE="${KEY_DIR}/epicrpg-release.keystore"
ALIAS="epicrpg"
# Local-only passwords for this project's release key (not for Play Store reuse).
STOREPASS="${EPICRPG_KEYSTORE_PASS:-epicrpg-release-local}"
KEYPASS="${EPICRPG_KEY_PASS:-epicrpg-release-local}"

echo "==> Sync ${WIN_SRC} -> ${WSL_DST}"
mkdir -p "${WSL_DST}"
rsync -a --delete \
  --exclude '.venv/' --exclude 'venv/' --exclude '.git/' --exclude 'dist/' --exclude 'build/' \
  --exclude 'docs/' --exclude 'tests/' --exclude 'upx-*/' --exclude 'android/.data/' \
  --exclude 'android/.buildozer/' --exclude 'android/bin/' --exclude '__pycache__/' --exclude '*.pyc' \
  --exclude 'node_modules/' --exclude 'desktop/' \
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
export PIP_BREAK_SYSTEM_PACKAGES=1

mkdir -p "${KEY_DIR}"
if [[ ! -f "${KEYSTORE}" ]]; then
  echo "==> Generating release keystore (once) at ${KEYSTORE}"
  keytool -genkeypair -v \
    -keystore "${KEYSTORE}" \
    -alias "${ALIAS}" \
    -keyalg RSA -keysize 2048 -validity 10000 \
    -storepass "${STOREPASS}" -keypass "${KEYPASS}" \
    -dname "CN=ePICRPG, OU=Games, O=ePICRPG, L=Local, S=Local, C=RU"
fi

export P4A_RELEASE_KEYSTORE="${KEYSTORE}"
export P4A_RELEASE_KEYSTORE_PASSWD="${STOREPASS}"
export P4A_RELEASE_KEYALIAS="${ALIAS}"
export P4A_RELEASE_KEYALIAS_PASSWD="${KEYPASS}"

cd "${WSL_DST}/android"

echo "==> buildozer android release (artifact=apk)"
buildozer -v android release

mkdir -p "${WIN_SRC}/android/bin"
shopt -s nullglob
found=0
for f in bin/*-release*.apk bin/*release*.apk; do
  [[ -f "$f" ]] || continue
  found=1
  cp -v "$f" "${WIN_SRC}/android/bin/"
  cp -v "$f" "${WIN_SRC}/android/bin/ePICRPG-2.5.6b-arm64.apk"
done
if [[ "$found" -eq 0 ]]; then
  echo "ERROR: no release APK in bin/ (got AAB instead?)"
  ls -la bin/ || true
  exit 1
fi
ls -la "${WIN_SRC}/android/bin/"*release* "${WIN_SRC}/android/bin/ePICRPG-2.5.6b-arm64.apk" 2>/dev/null || true
echo BUILD_RELEASE_OK
