#!/usr/bin/env bash
# Fix WSL DNS so apt/pip/buildozer can reach the network (common with VPN).
set -e
mkdir -p /etc
cp -a /etc/wsl.conf /etc/wsl.conf.bak 2>/dev/null || true
if ! grep -q 'generateResolvConf' /etc/wsl.conf 2>/dev/null; then
  cat >> /etc/wsl.conf <<'EOF'

[network]
generateResolvConf = false
EOF
fi
rm -f /etc/resolv.conf
cat > /etc/resolv.conf <<'EOF'
nameserver 8.8.8.8
nameserver 1.1.1.1
nameserver 9.9.9.9
options timeout:2 attempts:3
EOF
chmod 644 /etc/resolv.conf
echo "resolv.conf now:"
cat /etc/resolv.conf
echo DNS_FIXED
