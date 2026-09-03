# ============================================================
# Dockerfile - Inmobiliaria Velar (Reflex App)
# ============================================================

# Stage 1: Build Custom Caddy with ratelimit
FROM caddy:2-builder AS caddy-builder
RUN xcaddy build --with github.com/mholt/caddy-ratelimit

# Stage 2: Final image
FROM python:3.11-slim

# Create non-root user
RUN groupadd -r appgroup && useradd -r -g appgroup -d /app -s /sbin/nologin appuser

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    unzip curl gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy Caddy from builder
COPY --from=caddy-builder /usr/bin/caddy /usr/local/bin/caddy

# Set working directory
WORKDIR /app

# Copy requirements first (Docker cache optimization)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Cache-busting ARG
ARG CACHEBUST=20260704_1045

# Copy ALL source code
COPY . .

# Limpiar cachés de Python compilado
RUN find /app -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true && \
    find /app -name "*.pyc" -delete 2>/dev/null || true

# Make entrypoint executable
RUN chmod +x /app/entrypoint.sh

# Check styles
RUN python -c "\
import sys, importlib; \
mod = importlib.import_module('src.presentacion_reflex.styles'); \
[sys.exit(f'Missing: {attr}') for attr in ['BASE_STYLE', 'BG_APP', 'BG_PANEL', 'TEXT_PRIMARY'] if not hasattr(mod, attr)]; \
print(' All required style symbols verified')"

# Build frontend
RUN rm -rf .web && RAILWAY_ENVIRONMENT=production DATABASE_URL=sqlite:///dummy_build.db reflex init
RUN RAILWAY_ENVIRONMENT=production DATABASE_URL=sqlite:///dummy_build.db reflex export --frontend-only --no-zip
RUN rm -f dummy_build.db

# Diagnostic
RUN echo "=== BUILD: Frontend file locations ===" && \
    find /app -name "index.html" -not -path "*/node_modules/*" -not -path "*/.web/pages/*" 2>/dev/null | head -10 && \
    echo "=== END BUILD DIAGNOSTIC ==="

# Set permissions for non-root user
RUN mkdir -p /data /config && chown -R appuser:appgroup /app /data /config

# Switch to non-root user
USER appuser

# Expose port (Railway sets $PORT)
EXPOSE 8080

# At RUNTIME: entrypoint handles DB init, backend start, and Caddy
CMD ["/bin/bash", "/app/entrypoint.sh"]
