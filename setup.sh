#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$ROOT_DIR"

echo "[setup] Checking Python..."
PYTHON_BIN=""
if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN=python3
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN=python
else
  echo "Error: Python not found. Install Python 3.10+ and try again."
  exit 1
fi

echo "[setup] Using $PYTHON_BIN"

if [ ! -d ".venv" ]; then
  echo "[setup] Creating virtual environment .venv..."
  $PYTHON_BIN -m venv .venv
else
  echo "[setup] Virtual environment .venv already exists"
fi

if [ ! -f ".venv/bin/activate" ]; then
  echo "Error: virtual environment activation file not found"
  exit 1
fi

echo "[setup] Activating virtual environment..."
# shellcheck source=/dev/null
. .venv/bin/activate

echo "[setup] Upgrading pip..."
pip install --upgrade pip

if [ ! -f "requirements.txt" ]; then
  echo "Error: requirements.txt not found"
  exit 1
fi

echo "[setup] Installing dependencies..."
pip install -r requirements.txt

echo "[setup] Completed!"
echo "Use the following commands to start the project:"
echo "  source .venv/bin/activate"
echo "  python main.py"
