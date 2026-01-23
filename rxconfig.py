"""
Configuración de Reflex - Sistema de Gestión Inmobiliaria Velar
"""

import reflex as rx

config = rx.Config(
    # IMPORTANTE: app_name debe coincidir con la carpeta y archivo (inmobiliaria_velar/inmobiliaria_velar.py)
    app_name="inmobiliaria_velar",
    # Puertos para ejecución dual con Flet
    backend_port=8000,
    frontend_port=3000,
    # Configuración PostgreSQL
    db_url="postgresql://inmo_user:7323@localhost:5432/db_inmo_velar",
    # Entorno de desarrollo
    env=rx.Env.DEV,
    # Desactivar telemetría (opcional)
    telemetry_enabled=False,
)
