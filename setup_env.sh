#!/usr/bin/env bash
# setup_env.sh
# Create and activate Python virtual environment, then install all requirements
set -e

VENV_DIR="venv-enhanced"
PYTHON_BIN="python3.13"

# 1. Create venv if not exists
if [ ! -d "$VENV_DIR" ]; then
  echo "[SETUP] Creating virtual environment in $VENV_DIR..."
  $PYTHON_BIN -m venv "$VENV_DIR"
else
  echo "[SETUP] Virtual environment already exists: $VENV_DIR"
fi

# 2. Activate venv
source "$VENV_DIR/bin/activate"
echo "[SETUP] Activated virtual environment."

# 3. Upgrade pip
pip install --upgrade pip

# 4. Install requirements
if [ -f requirements.txt ]; then
  echo "[SETUP] Installing requirements.txt..."
  pip install -r requirements.txt
else
  echo "[ERROR] requirements.txt not found!"
  exit 1
fi

# 5. Install dev requirements if present
if [ -f requirements-dev.txt ]; then
  echo "[SETUP] Installing requirements-dev.txt..."
  pip install -r requirements-dev.txt
fi

echo "[SETUP] Environment ready. To activate later: source $VENV_DIR/bin/activate"
