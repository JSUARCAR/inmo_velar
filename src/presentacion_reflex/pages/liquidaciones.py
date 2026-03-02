"""Página de Liquidaciones - Limpieza de Emergencia"""
import reflex as rx
from src.presentacion_reflex.components.layout.dashboard_layout import dashboard_layout
from src.presentacion_reflex.state.auth_state import AuthState

@rx.page(route="/liquidaciones", on_load=AuthState.require_login)
def liquidaciones():
    return dashboard_layout(rx.heading("Liquidaciones"))
