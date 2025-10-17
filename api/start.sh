#!/usr/bin/env bash
set -euo pipefail

# Use PORT from environment (Render sets $PORT); default to 8000 locally.
PORT="${PORT:-8000}"

# Optional: print env for debugging
echo "Starting app on 0.0.0.0:${PORT}"
echo "PYTHONPATH=${PYTHONPATH:-.}"
env | grep -Ei 'port|python' || true

# Run uvicorn
exec uvicorn api.main:app --host 0.0.0.0 --port "${PORT}" --proxy-headers
