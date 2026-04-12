"""
Entry Point: Sistema de Gestión Inmobiliaria - Reflex
Versión web moderna. Fase 1: Core Architecture.
"""

import reflex as rx
from src.presentacion_reflex.pages import login
from src.presentacion_reflex.state.auth_state import AuthState
from src.presentacion_reflex import styles

# --- VISTAS DEL DASHBOARD (Protegidas) ---


@rx.page(route="/", on_load=AuthState.redirect_to_dashboard)
def index() -> rx.Component:
    """Página raíz: redirige automáticamente al dashboard."""
    return rx.center(
        rx.spinner(size="3"),
        height="100vh",
    )


# --- CONFIGURACIÓN DE LA APP ---

# Crear la app (toast provider incluido automáticamente)
app = rx.App(
    stylesheets=[
        "aurora.css",
        "custom_layout_v2.css",
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
        "https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;600;700&display=swap",
    ],
    html_lang="es",
    theme=rx.theme(
        appearance="light",
        has_background=True,
        radius="medium",
        accent_color="gray",
        panel_background="solid",
        font_family="Inter",
    ),
    head_components=[
        rx.script(src="/matrix.js?v=5"),
    ],
    style={
        "font_family": "var(--font-sans)",
        "font_size": styles.FONT_SIZE_SM,
        "background_color": styles.BG_APP,
        "color": styles.TEXT_PRIMARY,
        "&::selection": {
            "background_color": styles.ACCENT_BG_SOFT,
        },
        rx.card: {
            "background_color": styles.BG_PANEL,
            "border": f"1px solid {styles.BORDER_DEFAULT}",
            "box_shadow": "var(--shadow-whisper)",
            "border_radius": "16px",
            "font_size": styles.FONT_SIZE_SM,
        },
        rx.dialog.content: {
            "background_color": styles.BG_PANEL,
            "border": f"1px solid {styles.BORDER_DEFAULT}",
            "box_shadow": styles.SHADOW_MODAL_ELITE,
            "border_radius": "16px",
            "font_size": styles.FONT_SIZE_SM,
        },
        rx.table.root: {
            "background_color": styles.BG_PANEL,
            "border_radius": "16px",
            "box_shadow": "var(--shadow-whisper)",
            "overflow": "hidden",
            "border": f"1px solid {styles.BORDER_DEFAULT}",
            "font_size": styles.FONT_SIZE_SM,
        },
        rx.table.row: {
            "_hover": {
                "background_color": styles.BG_HOVER,
            },
        },
        rx.table.cell: {
            "border_bottom": f"1px solid {styles.BORDER_DEFAULT}",
            "font_size": styles.FONT_SIZE_SM,
        },
        rx.input: styles.NEU_INPUT_STYLE,
        rx.select.trigger: styles.NEU_SELECT_STYLE,
        rx.text_area: styles.NEU_INPUT_STYLE,
        rx.button: styles.NEU_BUTTON_STYLE,
    },
)


# Middleware de Seguridad (Headers) - Implementación ASGI pura para evitar conflictos con WebSockets
class SecurityHeadersMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                from starlette.datastructures import MutableHeaders

                # IMPORTANTE: Usar 'raw' asegura que manipulamos los bytes de los headers correctamente
                # El uso previo de 'scope' era incorrecto para mensajes individuales de respuesta
                headers = MutableHeaders(raw=message["headers"])
                headers.append("X-Frame-Options", "DENY")
                headers.append("X-Content-Type-Options", "nosniff")
                headers.append("X-XSS-Protection", "1; mode=block")
                headers.append("Referrer-Policy", "strict-origin-when-cross-origin")

            try:
                await send(message)
            except RuntimeError as e:
                if "already upgraded" in str(e):
                    # Ignorar errores si la conexión ya se actualizó a WebSockets
                    return
                raise e

        await self.app(scope, receive, send_wrapper)


# Registrar el middleware en la app subyacente de Starlette/FastAPI
app._api.add_middleware(SecurityHeadersMiddleware)

# Registrar API routes para descargas de PDF con nombres correctos
from src.presentacion_reflex.api.pdf_download_api import register_pdf_routes

register_pdf_routes(app)

# Registrar API routes para visualización y descarga de documentos (Imágenes/Archivos BD)
from src.presentacion_reflex.api.document_download_api import register_document_routes

register_document_routes(app)

# Importar el paquete de páginas para que los decoradores @rx.page se registren automáticamente
from src.presentacion_reflex import pages
