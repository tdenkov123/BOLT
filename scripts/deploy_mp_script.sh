#!/bin/bash

set -e

PORT="/dev/ttyACM0"
SRC_DIR="$(dirname "$0")/../BOLT_mp/BOLT_mp"

echo "[INFO] Deploying to $PORT from $SRC_DIR ..."

mpremote connect "$PORT" soft-reset >/dev/null 2>&1 || true
mpremote connect "$PORT" soft-reset >/dev/null 2>&1 || true
mpremote connect "$PORT" cp "$SRC_DIR/config.py" :config.py
mpremote connect "$PORT" cp "$SRC_DIR/bolt_net.py" :bolt_net.py
mpremote connect "$PORT" cp "$SRC_DIR/boot.py" :boot.py
mpremote connect "$PORT" cp "$SRC_DIR/mqtt_client.py" :mqtt_client.py
mpremote connect "$PORT" cp "$SRC_DIR/mdns_discovery.py" :mdns_discovery.py
mpremote connect "$PORT" cp "$SRC_DIR/main.py" :main.py

echo "[INFO] Resetting device ..."
mpremote connect "$PORT" reset

echo "[INFO] Deploy complete."
