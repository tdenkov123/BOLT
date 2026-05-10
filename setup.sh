#!/bin/bash
set -e

echo "BOLT MQTT Setup"
echo ""

# Check for Avahi
if ! command -v avahi-daemon &> /dev/null; then
    echo "avahi-daemon not found"
    exit 1
fi

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "Docker not found"
    exit 1
fi

echo "Dependencies OK"
echo ""

if ! command -v avahi-publish-address &> /dev/null; then
    echo "avahi-publish-address not found"
    echo ""
fi

# Install Avahi service file for MQTT
echo "Installing mDNS service descriptor..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
sudo cp "$SCRIPT_DIR/docker/avahi-mqtt.service" /etc/avahi/services/mqtt.service
sudo install -m 755 "$SCRIPT_DIR/docker/bolt-avahi-mqtt-alias.sh" /usr/local/sbin/bolt-avahi-mqtt-alias
sudo cp "$SCRIPT_DIR/docker/bolt-avahi-mqtt-alias.service" /etc/systemd/system/bolt-avahi-mqtt-alias.service
sudo systemctl daemon-reload
sudo systemctl enable --now bolt-avahi-mqtt-alias.service || true
sudo systemctl reload avahi-daemon
echo ""

# Start Docker Compose
echo "Starting Docker Compose..."
cd "$SCRIPT_DIR"
docker compose up -d
echo "Mosquitto broker started"
echo ""
echo "Setup Complete"
