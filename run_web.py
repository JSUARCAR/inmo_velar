"""
Script para ejecutar InmoVelar en modo Web Local

Este script inicia la aplicación InmoVelar en modo web, 
abriendo automáticamente el navegador predeterminado.

Uso:
    python run_web.py
    
La aplicación estará disponible en: http://localhost:8080
"""

import os
import flet as ft
from dotenv import load_dotenv
from main import main

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    print("=" * 60)
    print("  InmoVelar - Sistema de Gestión Inmobiliaria")
    print("  Modo: Aplicación Web Local")
    print("=" * 60)
    print("\n🌐 Iniciando servidor web...")
    print("📍 URL: http://localhost:8080")
    print("🔄 El navegador se abrirá automáticamente...")
    print("\n💡 Presiona Ctrl+C para detener el servidor\n")
    
    # FLET_SECRET_KEY is required for generating signed upload URLs
    # Set it from SECRET_KEY env var or use a default for development
    if not os.getenv("FLET_SECRET_KEY"):
        os.environ["FLET_SECRET_KEY"] = os.getenv("SECRET_KEY", "inmovelar-dev-secret-key-2024")
    
    ft.app(
        target=main,
        view=ft.AppView.WEB_BROWSER,
        port=8080,
        upload_dir="uploads"
    )
