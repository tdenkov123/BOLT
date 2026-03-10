#!/bin/bash

set -e

VENV_DIR=".venv"
PYTHON_BIN="python3"

if [[ "$(uname -s)" =~ MINGW|MSYS|CYGWIN ]] || [[ "$OS" == "Windows_NT" ]]; then
    ACTIVATE_SCRIPT="$VENV_DIR/Scripts/activate"
else
    ACTIVATE_SCRIPT="$VENV_DIR/bin/activate"
fi

if [ ! -d "$VENV_DIR" ]; then
    echo "[INFO] Creating virtual environment in $VENV_DIR ..."
    $PYTHON_BIN -m venv "$VENV_DIR"
else
    echo "[INFO] Virtual environment already exists at $VENV_DIR."
fi

source "$ACTIVATE_SCRIPT"
echo "[INFO] Virtual environment activated."

pip install --upgrade pip

if [ -f "requirements.txt" ]; then
    echo "[INFO] Installing dependencies"
    pip install -r requirements.txt
else
    echo "[WARN] No requirements.txt found, skipping."
fi

echo "[INFO] Setup complete."
