#!/usr/bin/env bash
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
export PATH="${HOME}/.local/bin:${PATH}"

echo "==> apt update"
apt-get update -y

echo "==> apt install build deps"
apt-get install -y \
  git zip unzip openjdk-17-jdk python3-pip python3-venv python3-setuptools \
  autoconf libtool pkg-config zlib1g-dev libncurses-dev cmake libffi-dev libssl-dev \
  rsync build-essential ccache libltdl-dev

java -version
python3 --version

echo "==> pip install buildozer"
pip3 install --break-system-packages --user 'buildozer' 'cython' 'virtualenv' \
  || pip3 install --user 'buildozer' 'cython' 'virtualenv'

buildozer --version

WIN_SRC=/mnt/c/Users/user/Desktop/rpg
WSL_DST="${HOME}/epicrpg"
mkdir -p "${WSL_DST}"
echo "==> rsync to ${WSL_DST}"
rsync -a --delete \
  --exclude '.venv/' --exclude 'venv/' --exclude '.git/' --exclude 'dist/' --exclude 'build/' \
  --exclude 'docs/' --exclude 'tests/' --exclude 'upx-*/' --exclude 'android/.data/' \
  --exclude 'android/.buildozer/' --exclude 'android/bin/' --exclude '__pycache__/' --exclude '*.pyc' \
  "${WIN_SRC}/" "${WSL_DST}/"

ls -la "${WSL_DST}/android/main.py" "${WSL_DST}/main.py"
echo TOOLCHAIN_OK
