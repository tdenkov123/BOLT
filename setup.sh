#!/bin/bash
set -e

echo "=== BOLT MQTT Setup ==="
echo ""

# Check for Avahi
if ! command -v avahi-daemon &> /dev/null; then
    echo "❌ avahi-daemon not found. Installing..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y avahi-daemon
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y avahi
    else
        echo "❌ Could not install avahi-daemon. Please install manually and re-run."
        exit 1
    fi
fi

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker and re-run."
    exit 1
fi

echo "✓ Dependencies OK"
echo ""

# Install Avahi service file for MQTT
echo "Installing mDNS service descriptor..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
sudo cp "$SCRIPT_DIR/docker/avahi-mqtt.service" /etc/avahi/services/mqtt.service
sudo systemctl reload avahi-daemon
echo "✓ mDNS service registered"
echo ""

# Start Docker Compose
echo "Starting Docker Compose..."
cd "$SCRIPT_DIR"
docker compose up -d
echo "✓ Mosquitto broker started"
echo ""

echo "=== Setup Complete ==="
echo "Broker is now discoverable as 'mqtt.local' on the local network."
echo ""
echo "To stop: docker compose down"
echo "To remove mDNS registration: sudo rm /etc/avahi/services/mqtt.service && sudo systemctl reload avahi-daemon"
