set -e

INSTALL_DIR="/opt/battery_health"

echo "[+] Installing Battery Health Monitor..."

sudo mkdir -p $INSTALL_DIR
sudo cp -r battery_health_app/* $INSTALL_DIR/

sudo cp $INSTALL_DIR/systemd/battery_health.service /etc/systemd/system/
sudo cp $INSTALL_DIR/systemd/battery_health.timer /etc/systemd/system/

sudo systemctl daemon-reexec
sudo systemctl daemon-reload

sudo systemctl enable battery_health.timer
sudo systemctl start battery_health.timer

echo "[✓] Installation complete. Battery Health Monitor is now running."