"""
Entry Point: Sistema de Gestión Inmobiliaria - Reflex
Versión web moderna. Fase 1: Core Architecture.
"""

import reflex as rx
from src.presentacion_reflex.pages import login
from src.presentacion_reflex.state.auth_state import AuthState

# --- VISTAS DEL DASHBOARD (Protegidas) ---

from src.presentacion_reflex.components.layout.dashboard_layout import dashboard_layout

@rx.page(on_load=AuthState.require_login)
def index() -> rx.Component:
    """Dashboard Principal (Protegido)."""
    return dashboard_layout(
        rx.vstack(
            rx.heading("Bienvenido al Sistema", size="8", color="#111827"),
            rx.text(f"Hola, {AuthState.user_info['nombre_usuario']}", size="4", color="gray"),
            
            rx.divider(margin_y="4"),
            
            # Estadísticas de Migración
            rx.heading("Estado de la Migración", size="6", margin_bottom="4"),
            
            rx.grid(
                rx.card(
                    rx.vstack(
                        rx.icon("circle_check", color="green", size=32),
                        rx.text("Fase 0: Preparación", weight="bold", size="4"),
                        rx.badge("Completado", color_scheme="green"),
                        align="center",
                        spacing="2",
                    ),
                ),
                rx.card(
                    rx.vstack(
                        rx.icon("check_check", color="green", size=32),
                        rx.text("Fase 1: Autenticación", weight="bold", size="4"),
                        rx.badge("Completado", color_scheme="green"),
                        align="center",
                        spacing="2",
                    ),
                ),
                rx.card(
                    rx.vstack(
                        rx.icon("layout-template", color="green", size=32),
                        rx.text("Fase 2: Layout Base", weight="bold", size="4"),
                        rx.badge("Completado", color_scheme="green"),
                        align="center",
                        spacing="2",
                    ),
                ),
                columns="3",
                spacing="4",
                width="100%",
            ),
            
            padding="8",
            width="100%",
        )
    )


# --- CONFIGURACIÓN DE LA APP ---

# Crear la app (toast provider incluido automáticamente)
# Crear la app (toast provider incluido automáticamente)
app = rx.App(
    theme=rx.theme(
        appearance="light",
        has_background=True,
        radius="large",
        accent_color="blue",
    )
)

# Middleware de Seguridad (Headers)
from fastapi import Request

@app._api.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    # Skip middleware for WebSocket upgrades to avoid "Connection already upgraded" errors
    if request.headers.get("upgrade", "").lower() == "websocket":
        return await call_next(request)
        
    # Procesar request normal
    response = await call_next(request)
    
    # Añadir headers de seguridad solo si no es un websocket
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    # Note: HSTS handled by host/proxy usually, but can be added here if HTTPS enforced
    return response

# Registrar API routes para descargas de PDF con nombres correctos
from src.presentacion_reflex.api.pdf_download_api import register_pdf_routes
register_pdf_routes(app)

# Registrar API routes para visualización y descarga de documentos (Imágenes/Archivos BD)
from src.presentacion_reflex.api.document_download_api import register_document_routes
register_document_routes(app)

# 1. Login (Pública)
app.add_page(login.login_page, route="/login", title="Login - Inmobiliaria Velar")

# 2. Home/Dashboard (Protegida)
# 2. Home/Dashboard (Protegida)
from src.presentacion_reflex.pages import personas
# app.add_page(personas.personas_page, route="/personas", title="Personas - Inmobiliaria Velar")

# 4. Dashboard (Protegida)
from src.presentacion_reflex.pages import dashboard
# app.add_page(dashboard.dashboard, route="/dashboard", title="Dashboard - Inmobiliaria Velar")

# 5. Propiedades (Protegida)
from src.presentacion_reflex.pages import propiedades
# app.add_page(propiedades.propiedades, route="/propiedades", title="Propiedades - Inmobiliaria Velar")

# 6. Contratos (Protegida)
from src.presentacion_reflex.pages import contratos
# app.add_page(contratos.contratos, route="/contratos", title="Contratos - Inmobiliaria Velar")

# 7. Liquidaciones (Protegida)
from src.presentacion_reflex.pages import liquidaciones
# app.add_page(liquidaciones.liquidaciones, route="/liquidaciones", title="Liquidaciones - Inmobiliaria Velar")

# 8. Desocupaciones (Protegida)
from src.presentacion_reflex.pages import desocupaciones
# app.add_page(desocupaciones.desocupaciones, route="/desocupaciones", title="Desocupaciones - Inmobiliaria Velar")

# 9. Incidentes (Protegida)
from src.presentacion_reflex.pages import incidentes
# app.add_page(incidentes.incidentes, route="/incidentes", title="Incidentes - Inmobiliaria Velar")

# 10. Seguros (Placeholder)
from src.presentacion_reflex.pages import seguros
# app.add_page(seguros.seguros, route="/seguros", title="Seguros - Inmobiliaria Velar")

# 11. Recaudos - Uses @rx.page decorator in file, auto-registers on import via __init__.py

# 12. Liquidación Asesores
from src.presentacion_reflex.pages import liquidacion_asesores
# app.add_page(liquidacion_asesores.liquidacion_asesores_page, route="/liquidacion-asesores", title="Liquidación Asesores - Inmobiliaria Velar")

# 13. Proveedores
from src.presentacion_reflex.pages import proveedores
# app.add_page(proveedores.proveedores_page, route="/proveedores", title="Proveedores - Inmobiliaria Velar")

# 14. Reportes
from src.presentacion_reflex.pages import reportes
# app.add_page(reportes.reportes_page, route="/reportes", title="Reportes - Inmobiliaria Velar")
