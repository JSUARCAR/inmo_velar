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
:${PORT:-8080}

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
    reverse_proxy localhost:8081
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
    
    # Cache static assets (JS, CSS, Images) for a long time, but with versioning check
    # Reflex uses hashed filenames, so long cache is fine, but index.html MUST be no-cache.
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
echo "=== Step 5: Waiting 3s then starting Caddy on port ${PORT:-8080} ==="
sleep 3
echo "  ✅ Starting Caddy..."
caddy run --config /app/Caddyfile.runtime --adapter caddyfile
