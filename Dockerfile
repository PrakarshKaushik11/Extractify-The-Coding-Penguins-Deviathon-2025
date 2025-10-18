# ---------- UI build stage ----------
FROM node:18-alpine AS ui-build
WORKDIR /app/ui
COPY ui/package*.json ui/yarn.lock* ./
RUN npm ci --no-audit --no-fund
COPY ui/ .
RUN npm run build

# ---------- API build stage (used to build deps if you like) ----------
FROM python:3.11-slim AS api-build
WORKDIR /app
# install system deps required for building some python packages (kept minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# copy requirements and install (in api-build to cache on separate stage)
COPY api/requirements.txt ./requirements.txt
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# ---------- Runtime stage (python + nginx) ----------
FROM python:3.11-slim AS runtime
WORKDIR /app

# install nginx (Debian package) and small extras
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx && \
    rm -rf /var/lib/apt/lists/*

# Copy static UI files produced by ui-build into nginx web root
COPY --from=ui-build /app/ui/dist /usr/share/nginx/html

# Copy app code
COPY api /app/api
COPY crawler /app/crawler
COPY extractor /app/extractor

# Copy requirements (from filesystem) and install into runtime (keeps runtime self-contained)
COPY api/requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# Use your nginx conf (ensure it proxies to 127.0.0.1:8001 as in your logs)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy start script and make it executable
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Expose the ports (nginx listens on 8080 in your config; uvicorn on 8001)
EXPOSE 8080 8001

# Default command will start nginx and uvicorn
CMD ["/app/start.sh"]
