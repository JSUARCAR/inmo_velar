"""
Punto de entrada principal para la aplicacion Flet.
Ejecutar: python main_ui.py
"""

import sys
from pathlib import Path

# Agregar el directorio del proyecto al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Ahora importar la app
import flet as ft
from src.presentacion.app import main

if __name__ == "__main__":
    ft.app(target=main)
