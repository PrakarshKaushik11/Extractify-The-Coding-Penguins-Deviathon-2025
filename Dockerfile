# ---------- Build frontend ----------
FROM node:18-alpine AS ui-build
WORKDIR /app/ui
# copy only package files to leverage caching
COPY ui/package*.json ui/yarn.lock* ./ 
RUN npm ci
COPY ui/ ./
RUN npm run build

# ---------- Python backend + model ----------
FROM python:3.11-slim AS api-build
WORKDIR /app
# system deps for spacy and uvicorn
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git curl gcc libc6-dev libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# copy requirements and install
COPY api/requirements.txt ./requirements.txt
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model at build time to avoid runtime blocking
# Adjust the wheel URL to match the spacy + model version in requirements.txt
RUN python -m spacy download en_core_web_sm || true

# copy backend code
COPY api/ ./api/

# ---------- Final runtime image ----------
FROM nginx:1.25-alpine AS runtime
# Create app directories
WORKDIR /app

# Copy built frontend to nginx html dir
COPY --from=ui-build /app/ui/dist /usr/share/nginx/html

# Copy backend / python runtime from previous stage
# We copy the entire Python install used in api-build for uvicorn & packages
# Note: this is a pragmatic approach—if you prefer, install Python into final image
COPY --from=api-build /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=api-build /usr/local/bin /usr/local/bin
COPY --from=api-build /usr/bin /usr/bin
COPY --from=api-build /usr/lib /usr/lib
COPY --from=api-build /app/api /app/api

# Copy nginx conf and start script
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Expose port 8080 (Render expects this)
EXPOSE 8080

# Run start script which launches uvicorn & nginx
CMD ["/app/start.sh"]
