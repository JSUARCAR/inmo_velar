"""
Entry Point: Sistema de Gestión Inmobiliaria - Reflex
Versión web moderna. Fase 1: Core Architecture.
"""

import reflex as rx
from src.presentacion_reflex.state.auth_state import AuthState
from src.presentacion_reflex import styles

@rx.page(route="/", on_load=AuthState.redirect_to_dashboard)
def index() -> rx.Component:
    return rx.center(rx.spinner(size="3"), height="100vh")

app = rx.App(
    html_lang="es",
    theme=rx.theme(
        appearance="light",
        accent_color="gray",
        gray_color="slate",
        radius="large",
    ),
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Inter:wght@400;500;600;700&display=swap",
        "/aurora.css",
        "/custom_layout_v2.css",
    ],
    head_components=[
        rx.el.meta(name="viewport", content="width=device-width, initial-scale=1"),
        rx.el.meta(name="description", content="Sistema integral de gestión inmobiliaria."),
        rx.script(src="/matrix.js?v=5"),
    ],
    style=styles.BASE_STYLE,
)

from src.presentacion_reflex import pages
