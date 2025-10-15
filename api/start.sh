#!/usr/bin/env bash
set -e

# Optional: install model at build time; if missing, attempt download at start
if ! python -c "import importlib,sys; importlib.import_module('en_core_web_sm')" 2>/dev/null; then
  echo "en_core_web_sm not installed — attempting download..."
  python -m spacy download en_core_web_sm || true
fi

# Start uvicorn on 0.0.0.0: you can change workers as needed
exec uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 2
