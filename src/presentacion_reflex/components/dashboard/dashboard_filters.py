"""
Filtros del Dashboard - Reflex
Barra de filtros para mes, año y asesor.
"""

import reflex as rx
from datetime import datetime
from src.presentacion_reflex.state.dashboard_state import DashboardState


def dashboard_filters() -> rx.Component:
    """
    Barra de filtros para el dashboard.
    
    Incluye dropdowns para:
    - Mes (Enero - Diciembre)
    - Año (5 años hacia atrás)
    - Asesor (cargado dinámicamente)
    
    Returns:
        rx.Component: Barra de filtros con botones Aplicar y Reiniciar
    """
    
    # Año actual
    anio_actual = datetime.now().year
    anios = [str(a) for a in range(anio_actual, anio_actual - 5, -1)]
    
    return rx.card(
        rx.hstack(
            rx.icon("filter", size=20, color="blue.9"),
            rx.text("Filtros:", weight="bold", size="3"),
            
            # Dropdown Mes
            rx.select(
                ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                 "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"],
                placeholder="Seleccionar Mes",
                value=DashboardState.selected_month_name,
                on_change=DashboardState.set_month,
                size="2",
            ),
            
            # Dropdown Año
            rx.select(
                anios,
                placeholder="Año",
                value=DashboardState.selected_year.to_string(),
                on_change=DashboardState.set_year,
                size="2",
            ),
            
            # Dropdown Asesor
            rx.select.root(
                rx.select.trigger(placeholder="Todos los asesores"),
                rx.select.content(
                    rx.select.group(
                        rx.select.item("Todos", value="todos_asesores"),
                        rx.foreach(
                            DashboardState.advisor_options,
                            lambda x: rx.select.item(x["label"], value=x["value"])
                        )
                    )
                ),
                value=DashboardState.selected_advisor_id.to_string(),
                on_change=DashboardState.set_advisor,
                size="2",
            ),
            
            # Botón Aplicar
            rx.button(
                rx.icon("check", size=16),
                "Aplicar",
                on_click=DashboardState.apply_filters,
                size="2",
            ),
            
            # Botón Reiniciar
            rx.icon_button(
                rx.icon("rotate_ccw", size=16),
                on_click=DashboardState.reset_filters,
                size="2",
                variant="soft",
            ),
            
            spacing="3",
            align="center",
            wrap="wrap",
        ),
        size="1",
        style={
            "box_shadow": "0 2px 8px rgba(0, 0, 0, 0.1)",
        },
    )
