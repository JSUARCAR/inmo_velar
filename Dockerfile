# ============================================================
# Dockerfile - Inmobiliaria Velar (Reflex App)
# ============================================================
FROM python:3.11-slim

# System dependencies + Caddy (single binary download)
RUN apt-get update && apt-get install -y --no-install-recommends \
    unzip curl gcc libpq-dev && \
    curl -L "https://caddyserver.com/api/download?os=linux&arch=amd64" -o /usr/local/bin/caddy && \
    chmod +x /usr/local/bin/caddy && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (Docker cache optimization)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy ALL source code
COPY . .

# Make entrypoint executable
RUN chmod +x /app/entrypoint.sh

# Initialize Reflex and build frontend at BUILD time.
# Railway env vars (DATABASE_URL) are NOT available during docker build,
# so we pass a dummy SQLite URL inline — it does NOT persist in the image.
RUN DATABASE_URL=sqlite:///dummy_build.db reflex init
RUN DATABASE_URL=sqlite:///dummy_build.db reflex export --frontend-only --no-zip
RUN rm -f dummy_build.db

# Diagnostic: show where the frontend files ended up
RUN echo "=== BUILD: Frontend file locations ===" && \
    find /app -name "index.html" -not -path "*/node_modules/*" -not -path "*/.web/pages/*" 2>/dev/null | head -10 && \
    echo "=== END BUILD DIAGNOSTIC ==="

# Expose port (Railway sets $PORT)
EXPOSE 8080

# At RUNTIME: entrypoint handles DB init, backend start, and Caddy
CMD ["/bin/bash", "/app/entrypoint.sh"]

