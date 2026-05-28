"""
Entry Point: Sistema de Gestión Inmobiliaria - Reflex
Versión web moderna. Fase 1: Core Architecture.
"""

import reflex as rx
from src.presentacion_reflex.state.auth_state import AuthState

@rx.page(route="/", on_load=AuthState.redirect_to_dashboard)
def index() -> rx.Component:
    return rx.center(rx.spinner(), height="100vh")

app = rx.App(
    html_lang="es",
    theme=rx.theme(appearance="light"),
)

from src.presentacion_reflex import pages
