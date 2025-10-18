#!/bin/sh
set -e

# port uvicorn will listen on (nginx proxies to this)
UVICORN_PORT=${UVICORN_PORT:-8001}

echo "Starting nginx (serving UI) and uvicorn (API)..."
# start nginx (daemonized by default; on Debian nginx runs a master process and workers)
nginx

# small pause to let nginx initialize
sleep 0.5

echo "Starting uvicorn on 0.0.0.0:${UVICORN_PORT}"
# use python -m uvicorn so we use the interpreter from this image
exec python -m uvicorn api.main:app --host 0.0.0.0 --port "${UVICORN_PORT}" --proxy-headers --workers 1
