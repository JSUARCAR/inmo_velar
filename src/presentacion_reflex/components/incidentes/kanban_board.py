from typing import Any, Dict, List

import reflex as rx

from src.presentacion_reflex.components.incidentes.incident_card import incident_card
from src.presentacion_reflex.state.incidentes_state import (
    IncidentesState,
    IncidenteDict,
)
from src.presentacion_reflex import styles


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
        opacity="0.6",
    )


def _skeleton_card() -> rx.Component:
    """Skeleton loader para simular una tarjeta de incidente durante carga."""
    return rx.vstack(
        rx.skeleton(height="14px", width="70%"),
        rx.skeleton(height="10px", width="100%"),
        rx.skeleton(height="10px", width="50%"),
        spacing="2",
        width="100%",
        padding="1rem",
        border_radius="12px",
        background="var(--gray-2)",
    )


def _skeleton_column() -> rx.Component:
    """Columna skeleton completa con 3 tarjetas placeholder."""
    return rx.vstack(
        _skeleton_card(),
        _skeleton_card(),
        _skeleton_card(),
        spacing="3",
        width="100%",
        padding_y="4px",
    )


def _kanban_column(title: str, items: Any, color_scheme: str) -> rx.Component:
    return rx.vstack(
        # --- Header ---
        rx.hstack(
            rx.hstack(
                rx.icon(_column_icon(title), size=18, color=f"var(--{color_scheme}-9)"),
                rx.text(title, weight="bold", size="3", color="var(--gray-12)"),
                spacing="2",
                align_items="center",
            ),
            rx.badge(
                items.length(),
                color_scheme=color_scheme,
                variant="soft",
                radius="full",
                padding_x="2",
            ),
            width="100%",
            justify="between",
            align_items="center",
            padding_bottom="0.75em",
            border_bottom=f"2px solid var(--{color_scheme}-4)",  # Borde más sutil
        ),
        # --- Content ---
        rx.scroll_area(
            rx.cond(
                IncidentesState.is_loading,
                _skeleton_column(),
                rx.cond(
                    items.length() > 0,
                    rx.vstack(
                        rx.foreach(items.to(list[IncidenteDict]), incident_card),
                        spacing="3",
                        width="100%",
                        padding_y="4px",
                        padding_x="2px",
                    ),
                    _empty_state(title),
                ),
            ),
            height="100%",
            width="100%",
            flex="1",
            type="always",
            scrollbars="vertical",
            style={
                "padding_bottom": "100px",
                "scrollbar_width": "thin",
                "scrollbar_color": "var(--border-default) transparent",
            },
        ),
        # --- Container Styles ---
        width="min(320px, 25vw)",
        height="calc(100vh - 280px)",
        min_height="400px",
        flex_shrink=0,
        padding="1rem",
        background_color="transparent",
        border="none",
        border_radius="lg",
        overflow="hidden",
    )


def kanban_board() -> rx.Component:
    """Tablero Kanban principal rediseñado."""
    return rx.scroll_area(
        rx.hstack(
            _kanban_column("Reportado", IncidentesState.incidentes_reportado, "red"),
            _kanban_column("Cotizado", IncidentesState.incidentes_cotizado, "orange"),
            _kanban_column("Aprobado", IncidentesState.incidentes_aprobado, "green"),
            _kanban_column(
                "En Reparación", IncidentesState.incidentes_en_reparacion, "blue"
            ),
            _kanban_column("Finalizado", IncidentesState.incidentes_finalizado, "gray"),
            spacing="4",
            width="auto",
            height="100%",
            flex="1",
            min_height="0",
            align_items="start",
            padding_bottom="5em",
            padding_right="1em",
        ),
        type="always",
        scrollbars="horizontal",
        width="100%",
        height="100%",
        style={"min_height": "500px"},
    )
