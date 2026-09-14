"""
Configuración de Reflex - Sistema de Gestión Inmobiliaria Velar

NOTA Task 5 (Reorden Raíz + SOLID, decisión "Raíz canónica"):
Archivo LEGADO de referencia en config/ — NO es el canónico.
Fuente canónica: /rxconfig.py (Reflex lo exige en raíz).
No editar aquí para cambios de producción; difiere de raíz
(puertos dual-Flet 8000/3000, env DEV fijo, sin IS_PROD/api_url/DATABASE_URL).
"""

import reflex as rx
import os
from dotenv import load_dotenv

load_dotenv()

config = rx.Config(
    # IMPORTANTE: app_name debe coincidir con la carpeta y archivo (inmobiliaria_velar/inmobiliaria_velar.py)
    app_name="inmobiliaria_velar",
    # Puertos para ejecución dual con Flet
    backend_port=8000,
    frontend_port=3000,
    # Configuración PostgreSQL
    db_url=f"postgresql://{os.getenv('DB_USER', 'inmo_user')}:{os.getenv('DB_PASSWORD', '7323')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME', 'db_inmo_velar')}",
    # Entorno de desarrollo
    env=rx.Env.DEV,
    # Desactivar telemetría (opcional)
    telemetry_enabled=False,
)
