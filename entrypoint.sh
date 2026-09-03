#!/bin/bash
set -e

echo "============================================"
echo "  ENTRYPOINT: Inmobiliaria Velar"
echo "============================================"

# ── Step 1: Find frontend files ───────────────────────────
echo ""
echo "=== Step 1: Locating frontend files ==="
FRONTEND_DIR=""
for dir in /app/frontend /app/.web/_static /app/.web/build/client; do
    if [ -f "$dir/index.html" ]; then
        FRONTEND_DIR="$dir"
        echo "  ✅ Found frontend at: $FRONTEND_DIR"
        break
    fi
done

if [ -z "$FRONTEND_DIR" ]; then
    echo "  ⚠ No frontend directory found in expected locations"
    echo "  Searching for index.html..."
    FOUND=$(find /app -name "index.html" -not -path "*/node_modules/*" -not -path "*/.web/pages/*" 2>/dev/null | head -1)
    if [ -n "$FOUND" ]; then
        FRONTEND_DIR=$(dirname "$FOUND")
        echo "  ✅ Found frontend at: $FRONTEND_DIR"
    else
        echo "  ❌ No index.html found anywhere!"
        find /app -maxdepth 3 -type d 2>/dev/null | head -20
        FRONTEND_DIR="/app/frontend"
    fi
fi

# ── Step 2: Generate Caddyfile with correct path ──────────
echo ""
echo "=== Step 2: Generating Caddyfile ==="
cat > /app/Caddyfile.runtime <<EOF
{
    order rate_limit before basicauth
}

:${PORT:-8080}

rate_limit {
    zone login_limit {
        key {client_ip}
        window 15m
        events 5
        match {
            path /api/login* /api/auth* /_event/auth_state.login* /_event/estado_autenticacion.iniciar_sesion*
        }
    }
}

header {
    Strict-Transport-Security "max-age=31536000; includeSubDomains"
    X-Frame-Options "DENY"
    X-Content-Type-Options "nosniff"
    Referrer-Policy "strict-origin-when-cross-origin"
    -Server
}

@backend {
    path /_event
    path /_event/*
    path /api/*
    path /upload
    path /upload/*
    path /_upload
    path /_upload/*
    path /ping
}

handle @backend {
    reverse_proxy localhost:8081 {
        header_up X-Forwarded-Proto https
        flush_interval -1
    }
}

handle {
    root * ${FRONTEND_DIR}
    try_files {path} /index.html
    file_server
    encode gzip
    
    # Disable cache for HTML files to ensure updates are seen immediately
    @html {
        path *.html
    }
    header @html Cache-Control "no-cache, no-store, must-revalidate"
}

handle_errors {
    @429 {
        expression {http.error.status_code} == 429
    }
    handle @429 {
        header Content-Type application/json
        respond "{\"detail\": \"Demasiados intentos de inicio de sesión\"}" 429
    }
    handle {
        header Content-Type application/json
        respond "{\"error\": \"Error interno del servidor\"}" 500
    }
}
EOF
echo "  ✅ Caddyfile generated (frontend: $FRONTEND_DIR)"

# ── Step 3: Run Database Migrations ──────────────────────
echo ""
echo "=== Step 3: Running Database Migrations ==="
if [ -n "$DATABASE_URL" ]; then
    echo "  ✅ DATABASE_URL is set"
    
    # Ejecutar migraciones de base de datos
    echo "  📦 Running database migrations..."
    python /app/scripts/run_pg_migrations.py || echo "  ⚠ Database migrations had issues (non-fatal)"
    
    # Configurar permisos
    echo "  🔐 Setting up permissions..."
    python /app/scripts/setup_permissions.py || echo "  ⚠ Permission setup had issues (non-fatal)"
    
    echo "  ✅ Database setup completed"
else
    echo "  ⚠ DATABASE_URL not set, skipping migrations"
    echo "  ⚠ This is expected for local development with SQLite"
fi

# ── Step 4: Start backend ────────────────────────────────
echo ""
echo "=== Step 4: Starting Reflex backend on port 8081 ==="
reflex run --env prod --backend-only --backend-port 8081 --backend-host 0.0.0.0 &
BACKEND_PID=$!

# ── Step 5: Start Caddy ──────────────────────────────────
echo ""
echo "=== Step 5: Waiting for backend on port 8081, then starting Caddy on port ${PORT:-8080} ==="
for i in $(seq 1 30); do
    if curl -s http://localhost:8081 > /dev/null 2>&1; then
        echo "  ✅ Backend ready on port 8081"
        break
    fi
    echo "  ⏳ Waiting for backend... ($i/30)"
    sleep 1
done
echo "  ✅ Starting Caddy..."
caddy run --config /app/Caddyfile.runtime --adapter caddyfile
