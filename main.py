"""
Entry Point: Sistema de Gestión Inmobiliaria - Reflex
Punto de entrada principal para la aplicación web.
"""

import signal
import sys
import reflex as rx
from pathlib import Path
from datetime import datetime

# Importar la app de Reflex
from inmobiliaria_velar.inmobiliaria_velar import app


def signal_handler(sig, frame):
    """Maneja señales de terminación gracefulmente."""
    sig_name = "SIGINT" if sig == signal.SIGINT else "SIGTERM"
    print(f"\n🛑 Recibida {sig_name}. Cerrando aplicación gracefully...")
    sys.exit(0)


# Registrar manejo de señales
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def main():
    """Función principal para ejecutar la aplicación Reflex."""
    # Ejecutar la app de Reflex
    app.run()


if __name__ == "__main__":
    main()
