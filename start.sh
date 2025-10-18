#!/bin/sh
set -e

UVICORN_PORT=${UVICORN_PORT:-8001}

echo "Starting nginx (serving UI) and uvicorn (API)..."
# Start nginx (master process). This starts workers as configured in your nginx.conf
nginx

# short pause to let nginx start
sleep 0.5

echo "Starting uvicorn on 0.0.0.0:${UVICORN_PORT}"
# Use python -m uvicorn so we use the interpreter from the image
exec python -m uvicorn api.main:app --host 0.0.0.0 --port "${UVICORN_PORT}" --proxy-headers --workers 1
