#!/bin/bash
set -e

echo "BOLT MQTT Setup"
echo ""

# Check for avahi-daemon binary
if ! command -v avahi-daemon &> /dev/null; then
    echo "ERROR: avahi-daemon not found"
    exit 1
fi

# Check for avahi-publish-address
if ! command -v avahi-publish-address &> /dev/null; then
    echo "ERROR: avahi-publish-address not found"
    exit 1
fi

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker not found"
    exit 1
fi

echo "Dependencies OK"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Ensure avahi-daemon is running
echo "Starting avahi-daemon ..."
sudo systemctl enable avahi-daemon
sudo systemctl start avahi-daemon
echo "  avahi-daemon: $(systemctl is-active avahi-daemon)"
echo ""

# Install Avahi service type record (_mqtt._tcp)
echo "Installing mDNS service type descriptor ..."
sudo cp "$SCRIPT_DIR/docker/avahi-mqtt.service" /etc/avahi/services/mqtt.service
sudo systemctl reload avahi-daemon
echo "  avahi service file: /etc/avahi/services/mqtt.service"

echo ""
echo "Installing bolt-avahi-mqtt-alias (mqtt.local → LAN IP) ..."
sudo install -m 755 "$SCRIPT_DIR/docker/bolt-avahi-mqtt-alias.sh" /usr/local/sbin/bolt-avahi-mqtt-alias
sudo cp "$SCRIPT_DIR/docker/bolt-avahi-mqtt-alias.service" /etc/systemd/system/bolt-avahi-mqtt-alias.service
sudo systemctl daemon-reload
sudo systemctl enable bolt-avahi-mqtt-alias.service
sudo systemctl restart bolt-avahi-mqtt-alias.service
echo "  bolt-avahi-mqtt-alias: $(systemctl is-active bolt-avahi-mqtt-alias)"
echo ""

echo "Verifying mqtt.local resolves (waiting up to 5 s) ..."
sleep 2
if avahi-resolve-host-name -4 mqtt.local 2>/dev/null; then
    echo "  mqtt.local OK"
else
    echo "  WARNING: mqtt.local did not resolve yet — Avahi may still be starting."
    echo "  Check:  sudo systemctl status bolt-avahi-mqtt-alias"
    echo "  Retry:  avahi-resolve-host-name -4 mqtt.local"
fi
echo ""

# Start Docker Compose
echo "Starting Docker Compose ..."
cd "$SCRIPT_DIR"
docker compose up -d
echo "Mosquitto broker started"
echo ""
echo "Setup Complete"
