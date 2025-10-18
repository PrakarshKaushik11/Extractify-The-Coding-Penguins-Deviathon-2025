#!/bin/sh
set -e

# Use PORT env var if provided for local dev; default 8000
PORT="${PORT:-8000}"

echo "Starting api (uvicorn) on 0.0.0.0:${PORT}"
exec python -m uvicorn api.main:app --host 0.0.0.0 --port "${PORT}" --proxy-headers
