#!/usr/bin/env bash
set -e
python -m uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 2
