#!/usr/bin/env bash
set -x
echo "=== connectivity ==="
curl -I -m 15 https://github.com 2>&1 | head -8 || true
curl -I -m 15 https://pypi.org 2>&1 | head -5 || true
curl -I -m 15 http://archive.ubuntu.com 2>&1 | head -5 || true
curl -I -m 15 https://mirror.yandex.ru/ubuntu/ 2>&1 | head -5 || true
echo "=== tools ==="
command -v java || true
command -v javac || true
command -v pip3 || true
command -v python3 || true
command -v rsync || true
command -v unzip || true
command -v git || true
command -v buildozer || true
python3 --version || true
python3 -m pip --version || true
dpkg -l openjdk-17-jdk python3-pip unzip git zip 2>/dev/null | tail -20 || true
ls /usr/lib/jvm 2>/dev/null || true
echo NETCHECK_DONE
