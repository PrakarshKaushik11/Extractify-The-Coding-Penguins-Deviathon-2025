# ---------- UI build stage ----------
FROM node:18-alpine AS ui-build
WORKDIR /app/ui
COPY ui/package*.json ui/yarn.lock* ./
RUN npm ci --no-audit --no-fund
COPY ui/ .
RUN npm run build

# ---------- API build stage (build and install heavy Python deps) ----------
FROM python:3.11-slim AS api-build
WORKDIR /app

# Minimal build deps for compiling wheels if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# copy requirements and install (in api-build to cache)
COPY api/requirements.txt ./requirements.txt
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Install spaCy English small model at build time (avoids runtime downloads)
RUN python -m pip install --no-cache-dir "https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl"

# ---------- Runtime stage (python + nginx) ----------
FROM python:3.11-slim AS runtime
WORKDIR /app

# install nginx (Debian) and small extras
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx && \
    rm -rf /var/lib/apt/lists/*

# Copy static UI files produced by ui-build into nginx web root
COPY --from=ui-build /app/ui/dist /usr/share/nginx/html

# Copy Python runtime/site-packages from api-build
COPY --from=api-build /usr/local /usr/local
COPY --from=api-build /usr/lib /usr/lib

# Copy app code
COPY api /app/api
COPY crawler /app/crawler
COPY extractor /app/extractor

# Copy nginx config (you already have one)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy start script and make it executable
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Expose ports (informational)
EXPOSE 8080 8001 80

# Default command will start nginx and uvicorn
CMD ["/app/start.sh"]
