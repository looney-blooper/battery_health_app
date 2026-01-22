#!/bin/bash
set -e

INSTALL_DIR="/opt/battery_health"

echo "[-] Uninstalling Battery Health Monitor..."

sudo systemctl stop battery-health.timer || true
sudo systemctl disable battery-health.timer || true

sudo rm -f /etc/systemd/system/battery-health.service
sudo rm -f /etc/systemd/system/battery-health.timer

sudo systemctl daemon-reexec
sudo systemctl daemon-reload

sudo rm -rf $INSTALL_DIR

echo "[✓] Battery Health Monitor removed."
