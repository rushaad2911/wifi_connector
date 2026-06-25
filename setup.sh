#!/bin/bash

set -e

echo "======================================="
echo "      BUX WiFi Connector Setup"
echo "======================================="

# Must be run as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run with sudo."
    echo
    echo "Example:"
    echo "sudo ./setup.sh"
    exit 1
fi

# Find project directory
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

# User who invoked sudo
REAL_USER=${SUDO_USER:-$(whoami)}

# Python path
PYTHON=$(which python3)

echo "Project Directory : $PROJECT_DIR"
echo "Python            : $PYTHON"
echo "User              : $REAL_USER"

echo
echo "Installing service..."

cat <<EOF >/etc/systemd/system/wifi-connector.service
[Unit]
Description=BUX WiFi Connector
After=NetworkManager.service network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$REAL_USER
Group=$REAL_USER
WorkingDirectory=$PROJECT_DIR
ExecStart=$PYTHON $PROJECT_DIR/main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo "Reloading systemd..."
systemctl daemon-reload

echo "Enabling service..."
systemctl enable wifi-connector.service

echo "Starting service..."
systemctl restart wifi-connector.service

echo
echo "======================================="
echo "Installation Complete!"
echo "======================================="
echo
echo "Useful commands:"
echo
echo "Status:"
echo "sudo systemctl status wifi-connector"
echo
echo "Logs:"
echo "journalctl -u wifi-connector -f"
echo
echo "Restart:"
echo "sudo systemctl restart wifi-connector"
echo
echo "Stop:"
echo "sudo systemctl stop wifi-connector"
echo
echo "Disable:"
echo "sudo systemctl disable wifi-connector"