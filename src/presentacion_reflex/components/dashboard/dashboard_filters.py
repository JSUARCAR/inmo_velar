"""
Filtros del Dashboard - Reflex
Barra de filtros para mes, año y asesor.
"""

from datetime import datetime

import reflex as rx

from src.presentacion_reflex.state.dashboard_state import DashboardState


from src.presentacion_reflex.components.neuro_elements import (
    neuro_panel,
    neuro_button,
    neuro_floating_select,
    neuro_icon_action_button,
    neuro_tooltip,
)
from src.presentacion_reflex import styles


def dashboard_filters() -> rx.Component:
    """
    Barra de filtros para el dashboard.
    """
    anio_actual = datetime.now().year
    anios = [str(a) for a in range(anio_actual, anio_actual - 5, -1)]
    meses = [
        "Enero",
        "Febrero",
        "Marzo",
        "Abril",
        "Mayo",
        "Junio",
        "Julio",
        "Agosto",
        "Septiembre",
        "Octubre",
        "Noviembre",
        "Diciembre",
    ]

    return neuro_panel(
        rx.flex(
            rx.hstack(
                rx.icon("filter", size=20, color="blue.9"),
                rx.text("Filtros:", weight="bold", size="3", color=styles.TEXT_PRIMARY),
                width="100%",
                padding_bottom=rx.breakpoints(initial="3", sm="0"),
                padding_right="4",
            ),
            # Dropdown Mes
            neuro_floating_select(
                label="Mes",
                value=DashboardState.selected_month_name,
                on_change=DashboardState.set_month,
                options=[{"label": m, "value": m} for m in meses],
                width=rx.breakpoints(initial="100%", sm="auto"),
            ),
            # Dropdown Año
            neuro_floating_select(
                label="Año",
                value=DashboardState.selected_year.to_string(),
                on_change=DashboardState.set_year,
                options=[{"label": a, "value": a} for a in anios],
                width=rx.breakpoints(initial="100%", sm="auto"),
            ),
            # Dropdown Asesor
            neuro_floating_select(
                label="Asesor",
                value=DashboardState.selected_advisor_value,
                on_change=DashboardState.set_advisor,
                options=DashboardState.advisor_options,
                width=rx.breakpoints(initial="100%", sm="auto"),
            ),
            # Botón Aplicar
            neuro_tooltip(
                neuro_button(
                    rx.icon("check", size=16),
                    "Aplicar",
                    on_click=DashboardState.apply_filters,
                    size="3",
                    padding_x="4",
                    width=rx.breakpoints(initial="100%", sm="auto"),
                ),
                text="Aplicar filtros",
            ),
            # Botón Reiniciar
            neuro_icon_action_button(
                "rotate_ccw",
                color_scheme="gray",
                size="3",
                tooltip_content="Limpiar filtros",
                on_click=DashboardState.reset_filters,
                width=rx.breakpoints(initial="100%", sm="auto"),
            ),
            spacing="5",
            align=rx.breakpoints(initial="start", sm="center"),
            width="100%",
            flex_direction=rx.breakpoints(initial="column", sm="row"),
            flex_wrap="wrap",
        ),
        padding="1rem 1.5rem",
    )
