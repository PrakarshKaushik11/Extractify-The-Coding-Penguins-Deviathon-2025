#!/bin/sh
set -eu

cd /app || exit 1

PORT="${PORT:-8000}"
HOST="0.0.0.0"

# start backend (uvicorn) in background
python -m uvicorn api.main:app --host "$HOST" --port "$PORT" --workers 2 &

# start nginx in foreground
exec nginx -g "daemon off;"
