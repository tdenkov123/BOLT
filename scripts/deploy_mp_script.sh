#!/bin/bash

set -e

PORT="/dev/ttyACM0"
SRC_DIR="$(dirname "$0")/../BOLT_mp/BOLT_mp"

echo "[INFO] Deploying to $PORT from $SRC_DIR ..."

mpremote connect "$PORT" cp "$SRC_DIR/boot.py" :boot.py
mpremote connect "$PORT" cp "$SRC_DIR/mqtt_client.py" :mqtt_client.py
mpremote connect "$PORT" cp "$SRC_DIR/main.py" :main.py
mpremote connect "$PORT" cp "$SRC_DIR/config.py" :config.py

echo "[INFO] Resetting device ..."
mpremote connect "$PORT" reset

echo "[INFO] Deploy complete."
