#!/usr/bin/env bash
# Run the PyChat GUI client and connect to a server (UNIX / WSL / macOS)
# Usage:
#   ./run-client.sh               # default server ws://162.43.92.97:8765
#   ./run-client.sh ws://host:8765

SERVER=${1:-ws://162.43.92.97:8765}
ROOT_DIR=$(cd "$(dirname "$0")" && pwd)
VENV_PY="$ROOT_DIR/.venv/bin/python"
if [ -x "$VENV_PY" ]; then
  "$VENV_PY" -m app.main --server "$SERVER"
else
  python -m app.main --server "$SERVER"
fi
