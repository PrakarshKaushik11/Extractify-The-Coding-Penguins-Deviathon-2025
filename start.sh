#!/bin/sh
set -euo pipefail

# Internal port where uvicorn runs (nginx proxies to this)
UVICORN_PORT=8001

echo "Starting nginx (serving UI) and uvicorn (API)."
echo "NGINX config: /etc/nginx/conf.d/default.conf"
echo "Starting nginx..."
nginx

# Print a small pause to let nginx come up (optional)
sleep 0.5

echo "Starting uvicorn on 0.0.0.0:${UVICORN_PORT}"
# uvicorn binary is installed into /usr/local/bin by the python image + pip install
# Run uvicorn in foreground (exec) so container PID is the uvicorn process
exec uvicorn api.main:app --host 0.0.0.0 --port "${UVICORN_PORT}" --proxy-headers --workers 1
