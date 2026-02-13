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

# Initialize Reflex and build frontend at BUILD time.
# Railway env vars (DATABASE_URL) are NOT available during docker build,
# so we pass a dummy SQLite URL inline — it does NOT persist in the image.
RUN DATABASE_URL=sqlite:///dummy_build.db reflex init
RUN DATABASE_URL=sqlite:///dummy_build.db reflex export --frontend-only --no-zip
RUN rm -f dummy_build.db

# Expose port (Railway sets $PORT)
EXPOSE 8080

# At RUNTIME, Railway injects the real DATABASE_URL env var.
# Initialize the real DB, then start the backend.
CMD reflex db init && reflex run --env prod --backend-only --backend-port ${PORT:-8080} --backend-host 0.0.0.0

