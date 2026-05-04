"""
Configuración de Reflex - Sistema de Gestión Inmobiliaria Velar
"""

import reflex as rx
import os
from dotenv import load_dotenv

load_dotenv()

# Determinar si estamos en producción (Railway)
IS_PROD = os.getenv("RAILWAY_ENVIRONMENT") == "production"

# URL del backend para descargas de PDF y APIs
# En desarrollo: apunta al backend en puerto 8000
# En producción: usa la URL de Railway
api_url = os.getenv("API_URL")
if not api_url:
    if not IS_PROD:
        api_url = "http://localhost:8000"
    else:
        api_url = "https://inmovelar-production.up.railway.app"

# Railway provides DATABASE_URL automatically when a Postgres plugin is attached.
# Compatibility: Replace 'postgres://' with 'postgresql://' for SQLAlchemy
_db_url = os.getenv("DATABASE_URL")
if _db_url and _db_url.startswith("postgres://"):
    _db_url = _db_url.replace("postgres://", "postgresql://", 1)

if not _db_url:
    _db_url = (
        f"postgresql://{os.getenv('DB_USER') or 'inmo_user'}"
        f":{os.getenv('DB_PASSWORD') or '7323'}"
        f"@{os.getenv('DB_HOST') or 'localhost'}"
        f":{os.getenv('DB_PORT') or '5432'}"
        f"/{os.getenv('DB_NAME') or 'db_inmo_velar'}"
    )

config = rx.Config(
    # IMPORTANTE: app_name debe coincidir con la carpeta y archivo (inmobiliaria_velar/inmobiliaria_velar.py)
    app_name="inmobiliaria_velar",
    # Puertos para ejecución (se comentan para evitar conflictos en producción con --backend-only)
    # backend_port=8000,
    # frontend_port=3000,
    # Configuración PostgreSQL
    db_url=_db_url,
    # Entorno de desarrollo
    env=rx.Env.DEV,
    # Desactivar telemetría (opcional)
    telemetry_enabled=False,
    # Permitir orígenes cruzados en producción (evita WS error en Railway)
    cors_allowed_origins=[
        "*",
        "http://localhost:3000",
        "https://inmovelar-production.up.railway.app",
    ],
    # Desactivar plugins internos que generan advertencias no deseadas
    disable_plugins=[rx.plugins.sitemap.SitemapPlugin],
)

# Inyectar api_url en el módulo para que pdf_state.py pueda accederlo
import sys

_current_module = sys.modules[__name__]
_current_module.api_url = api_url
