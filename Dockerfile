# ---------- UI build stage ----------
FROM node:18-alpine AS ui-build
WORKDIR /app/ui
COPY ui/package*.json ui/yarn.lock* ./ 
RUN npm ci --no-audit --no-fund
COPY ui/ .
RUN npm run build

# ---------- API build stage ----------
FROM python:3.11-slim AS api-build
WORKDIR /app
# install system deps required for building some python packages (kept minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# copy requirements and install
COPY api/requirements.txt ./requirements.txt
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# ---------- Runtime stage ----------
FROM nginx:1.25-alpine AS runtime
# create app dir
RUN mkdir -p /app
WORKDIR /app

# copy built ui files to nginx served directory (assumes nginx serves /usr/share/nginx/html)
COPY --from=ui-build /app/ui/dist /usr/share/nginx/html

# copy python runtime from api-build
COPY --from=api-build /usr/local /usr/local
COPY --from=api-build /usr/lib /usr/lib

# copy your API code into /app/api
COPY api /app/api
# copy other required project files if any
COPY crawler /app/crawler
COPY extractor /app/extractor

# copy start.sh into /app and make executable
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# expose port matching nginx config (we will run nginx + background uvicorn via start.sh)
EXPOSE 8080

# default command runs start.sh which launches uvicorn (API) and nginx will serve frontend
CMD ["/app/start.sh"]
