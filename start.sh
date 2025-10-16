#!/usr/bin/env bash
set -euo pipefail

# Change to app directory
cd /app

# PORT set by Render; fallback to 8000
PORT=${PORT:-8000}
HOST=0.0.0.0

# Start backend (uvicorn) in background
# Use --proxy-headers if nginx will proxy to uvicorn
python -m uvicorn api.main:app --host ${HOST} --port ${PORT} --workers 2 &

# Start nginx in foreground (nginx default in Alpine needs a conf file but default will serve /usr/share/nginx/html)
# Use daemon off to keep it in foreground
nginx -g "daemon off;"
