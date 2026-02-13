"""
Entry Point: Sistema de Gestión Inmobiliaria - Reflex
Punto de entrada principal para la aplicación web.
"""

import reflex as rx
from pathlib import Path
from datetime import datetime

# Importar la app de Reflex
from inmobiliaria_velar.inmobiliaria_velar import app


def main():
    """Función principal para ejecutar la aplicación Reflex."""
    # Ejecutar la app de Reflex
    app.run()


if __name__ == "__main__":
    main()
