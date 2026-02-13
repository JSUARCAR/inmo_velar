# ============================================================
# Dockerfile - Inmobiliaria Velar (Reflex App)
# ============================================================
FROM python:3.11-slim

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    unzip curl gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (Docker cache optimization)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy ALL source code
COPY . .

# Initialize Reflex and build frontend (AFTER copy, so .web persists)
RUN reflex init
RUN reflex export --frontend-only --no-zip

# Expose port (Railway sets $PORT)
EXPOSE 8080

# Start: initialize DB, then run backend-only since frontend is pre-built
CMD reflex db init && reflex run --env prod --backend-only --backend-port ${PORT:-8080} --backend-host 0.0.0.0
