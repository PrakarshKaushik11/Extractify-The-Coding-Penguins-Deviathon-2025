#!/bin/sh
set -eu

cd /app || exit 1

# uvicorn port for the internal API service (nginx will proxy /api -> this port)
UVICORN_PORT="8001"
HOST="127.0.0.1"

# Start backend (uvicorn) in background listening on localhost:8001
python -m uvicorn api.main:app --host "$HOST" --port "$UVICORN_PORT" --workers 2 &

# Start nginx in foreground (will serve the built UI and proxy /api to uvicorn)
exec nginx -g "daemon off;"
