#!/usr/bin/env bash
set -euo pipefail
PORT="${1:-/dev/ttyACM0}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PROBE="$REPO_ROOT/tests/mp_debug_esp_device.py"

echo "=== mpremote $PORT run $PROBE ==="
mpremote connect "$PORT" run "$PROBE"
