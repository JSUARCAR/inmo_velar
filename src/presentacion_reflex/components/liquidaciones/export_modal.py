"""
Componente: Modal para exportación masiva de liquidaciones (estados de cuenta) por periodo.
"""

import reflex as rx
from src.presentacion_reflex import styles
from src.presentacion_reflex.state.liquidaciones_state import LiquidacionesState
from src.presentacion_reflex.components.neuro_elements import (
    neuro_button,
    neuro_input,
)


def modal_exportar_liquidaciones_periodo() -> rx.Component:
    """Modal para seleccionar período y exportar estados de cuenta como ZIP."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.hstack(
                    rx.icon("file-archive", size=20, color="#d97757"),  # Terracotta
                    rx.text("Exportar Estados de Cuenta"),
                    spacing="2",
                    align="center",
                ),
            ),
            rx.dialog.description(
                "Seleccione el período contable para generar y descargar "
                "todos los estados de cuenta consolidados en un archivo ZIP.",
                size="2",
                color="gray",
            ),
            rx.separator(margin_y="12px"),
            rx.vstack(
                rx.text("Período", size="2", weight="medium"),
                neuro_input(
                    type="month",
                    value=LiquidacionesState.filter_periodo,  # Reutilizamos el filtro para coherencia
                    on_change=LiquidacionesState.set_filter_periodo,
                    width="100%",
                    size="3",
                ),
                rx.text(
                    "Se generarán los estados de cuenta PDF consolidados por propietario.",
                    size="1",
                    color="gray",
                ),
                spacing="2",
                width="100%",
            ),
            rx.separator(margin_y="12px"),
            rx.flex(
                rx.dialog.close(
                    neuro_button(
                        rx.text("Cancelar"),
                        variant="soft",
                        color_scheme="gray",
                        on_click=LiquidacionesState.close_export_modal,
                    ),
                ),
                neuro_button(
                    rx.hstack(
                        rx.icon("download", size=16),
                        rx.text("Generar y Descargar ZIP"),
                    ),
                    on_click=LiquidacionesState.exportar_liquidaciones_periodo_zip,
                    loading=LiquidacionesState.exportando_periodo,
                    color_scheme="orange",  # Coral/Terracotta style
                ),
                spacing="3",
                justify="end",
                width="100%",
            ),
            max_width="450px",
            background=styles.BG_PANEL,
            style={
                "box_shadow": styles.NEU_SHADOW,
                "border": "none",
                "border_radius": "24px",
            },
        ),
        open=LiquidacionesState.show_export_modal,
        on_open_change=lambda open: rx.cond(
            open,
            LiquidacionesState.open_export_modal,
            LiquidacionesState.close_export_modal,
        ),
    )
