#!/usr/bin/env sh
set -e

# start uvicorn on localhost:8001
# Use --proxy-headers only if expecting reverse proxy headers
uvicorn api.main:app --host 127.0.0.1 --port 8001 --workers 2 &

# start nginx in foreground
nginx -g "daemon off;"
