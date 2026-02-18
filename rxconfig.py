"""
Configuración de Reflex - Sistema de Gestión Inmobiliaria Velar
"""

import reflex as rx
import os
from dotenv import load_dotenv

load_dotenv()

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
    # Puertos para ejecución dual con Flet
    backend_port=8000,
    frontend_port=3000,
    # Configuración PostgreSQL
    db_url=_db_url,
    # Entorno de desarrollo
    env=rx.Env.PROD,
    # Desactivar telemetría (opcional)
    telemetry_enabled=False,
    # Desactivar plugins internos que generan advertencias no deseadas
    disable_plugins=['reflex.plugins.sitemap.SitemapPlugin'],
)
