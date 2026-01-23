import reflex as rx
from typing import List, Dict, Any
from src.presentacion_reflex.state.incidentes_state import IncidentesState
from src.presentacion_reflex.components.incidentes.incident_card import incident_card

def _column_icon(title: str) -> str:
    """Retorna el icono asociado al estado."""
    return {
        "Reportado": "clipboard-list",
        "Cotizado": "calculator",
        "Aprobado": "thumbs-up",
        "En Reparación": "wrench",
        "Finalizado": "flag",
    }.get(title, "circle")

def _empty_state(title: str) -> rx.Component:
    """Estado vacío elegante."""
    return rx.vstack(
        rx.icon(_column_icon(title), size=32, color="var(--gray-7)"),
        rx.text("Sin incidentes", size="2", color="var(--gray-9)", weight="medium"),
        width="100%",
        height="200px",
        justify="center",
        align_items="center",
        opacity="0.6"
    )

def _kanban_column(title: str, items: List[Dict[str, Any]], color_scheme: str) -> rx.Component:
    return rx.vstack(
        # --- Header ---
        rx.hstack(
            rx.hstack(
                rx.icon(_column_icon(title), size=18, color=f"var(--{color_scheme}-9)"),
                rx.text(title, weight="bold", size="3", color="var(--gray-12)"),
                spacing="2",
                align_items="center"
            ),
            rx.badge(
                items.length(), 
                color_scheme=color_scheme, 
                variant="soft", 
                radius="full",
                padding_x="2"
            ),
            width="100%",
            justify="between",
            align_items="center",
            padding_bottom="0.75em",
            border_bottom=f"2px solid var(--{color_scheme}-4)" # Borde más sutil
        ),
        
        # --- Content ---
        rx.scroll_area(
            rx.cond(
                items.length() > 0,
                rx.vstack(
                    rx.foreach(
                        items,
                        incident_card
                    ),
                    spacing="3",
                    width="100%",
                    padding_y="4px",
                    padding_x="2px" # Espacio para el glow del hover
                ),
                _empty_state(title)
            ),
            type="hover",
            scrollbars="vertical",
            style={"height": "calc(100vh - 280px)"} # Ajuste fino
        ),
        
        # --- Container Styles ---
        width="320px", # Un poco más ancho para mejor lectura
        height="100%",
        padding="1rem",
        background_color="var(--gray-2)", # Fondo sutil
        border="1px solid var(--gray-3)",
        border_radius="lg",
        flex_shrink=0,
        box_shadow="0 2px 4px rgba(0,0,0,0.02)" # Sombra muy sutil
    )

def kanban_board() -> rx.Component:
    """Tablero Kanban principal rediseñado."""
    return rx.scroll_area(
        rx.hstack(
            _kanban_column(
                "Reportado", 
                IncidentesState.incidentes_reportado, 
                "red"
            ),
            _kanban_column(
                "Cotizado", 
                IncidentesState.incidentes_cotizado, 
                "orange"
            ),
            _kanban_column(
                "Aprobado", 
                IncidentesState.incidentes_aprobado, 
                "green"
            ),
            _kanban_column(
                "En Reparación", 
                IncidentesState.incidentes_en_reparacion, 
                "blue"
            ),
            _kanban_column(
                "Finalizado", 
                IncidentesState.incidentes_finalizado, 
                "gray"
            ),
            spacing="4",
            width="100%", # Scroll content width
            height="100%",
            align_items="start",
            padding_bottom="1em",
            padding_right="1em"
        ),
        type="auto",
        scrollbars="horizontal",
        style={"width": "100%", "height": "100%"}
    )
