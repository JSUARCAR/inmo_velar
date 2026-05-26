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
        rx.el.meta(name="og:title", content="Inmobiliaria Velar | Gestión Profesional"),
        rx.el.meta(
            name="og:description",
            content="Sistema integral de gestión inmobiliaria, contratos, liquidaciones y recaudos en la nube.",
        ),
        rx.el.meta(name="og:image", content="/favicon.ico"),
        rx.el.meta(name="og:type", content="website"),
        rx.el.meta(name="twitter:card", content="summary_large_image"),
        rx.script(src="/matrix.js?v=5"),
        rx.script(
            """
            window.addEventListener('error', function(event) {
                console.error("Frontend Global Error Caught:", event.error);
                if (event.error && event.error.name === 'TypeError') {
                    console.log("TypeError detected. Soft reloading in 3s...");
                    setTimeout(() => { window.location.reload(); }, 3000);
                }
            });
            """
        ),
        rx.script(
            """window.__REFLEX_HYDRATION_DELAY = 300;"""
        ),
        rx.script(
            """
            // ErrorBoundary: Captura errores de renderizado React y muestra fallback amigable
            window.addEventListener('DOMContentLoaded', function() {
                var observer = new MutationObserver(function(mutations) {
                    var dashEl = document.querySelector('[data-page="/dashboard"]');
                    if (dashEl && dashEl.innerHTML.trim() === '') {
                        dashEl.innerHTML = '<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:80vh;gap:16px;font-family:Inter,sans-serif;">'
                            + '<svg width="48" height="48" fill="none" stroke="#c96442" stroke-width="2" viewBox="0 0 24 24"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>'
                            + '<h2 style="color:#141413;font-size:1.5rem;margin:0;">Error al cargar métricas</h2>'
                            + '<p style="color:#5e5d59;text-align:center;max-width:400px;">Redirigiendo a Contratos en 10 segundos...</p>'
                            + '<a href="/contratos" style="padding:8px 24px;background:#c96442;color:white;border-radius:8px;text-decoration:none;">Ir a Contratos</a>'
                            + '</div>';
                        setTimeout(function() { window.location.href = '/contratos'; }, 10000);
                        observer.disconnect();
                    }
                });
                observer.observe(document.body, { childList: true, subtree: true });
                // Auto-cleanup después de 30s
                setTimeout(function() { observer.disconnect(); }, 30000);
            });
            """
        ),
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
                headers.append("Content-Security-Policy", "upgrade-insecure-requests")

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

# Middleware de Idempotencia para API REST (Idempotency-Key header)
from src.presentacion_reflex.api.idempotency_middleware import IdempotencyMiddleware

app._api.add_middleware(IdempotencyMiddleware)

# Registrar API routes para descargas de PDF con nombres correctos
from src.presentacion_reflex.api.pdf_download_api import register_pdf_routes

register_pdf_routes(app)

# Registrar API routes para visualización y descarga de documentos (Imágenes/Archivos BD)
from src.presentacion_reflex.api.document_download_api import register_document_routes

register_document_routes(app)

# Importar el paquete de páginas para que los decoradores @rx.page se registren automáticamente
from src.presentacion_reflex import pages
