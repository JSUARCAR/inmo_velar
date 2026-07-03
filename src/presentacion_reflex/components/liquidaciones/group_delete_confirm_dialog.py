"""
Modal de Confirmación para Eliminar Grupo de Liquidaciones
Muestra resumen del grupo y permite confirmar la eliminación masiva.
"""

import reflex as rx

from src.presentacion_reflex.state.liquidaciones_state import LiquidacionesState
from src.presentacion_reflex.styles import Z_MODAL


def info_row(label: str, value) -> rx.Component:
    """Fila de información (label: value)."""
    return rx.hstack(
        rx.text(label, weight="medium", color="gray.700"),
        rx.spacer(),
        rx.text(value, weight="bold"),
        width="100%",
        padding_y="0.3em",
    )


def group_delete_confirm_dialog() -> rx.Component:
    """Diálogo de confirmación para eliminar un grupo de liquidaciones"""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.hstack(
                    rx.icon("trash-2", size=24, color="red"),
                    "Eliminar Liquidaciones del Grupo",
                    spacing="2",
                )
            ),
            rx.dialog.description(
                rx.text(
                    "Esta acción eliminará todas las liquidaciones no pagadas de este propietario para el período seleccionado.",
                    color="red.600",
                    weight="medium",
                ),
            ),
            rx.cond(
                LiquidacionesState.liquidacion_actual,
                rx.vstack(
                    # Resumen del grupo
                    rx.heading("Resumen del Grupo", size="5", margin_top="0.8em", margin_bottom="0.4em"),
                    rx.box(
                        info_row(
                            "Propietario:",
                            LiquidacionesState.liquidacion_actual["propietario"],
                        ),
                        info_row(
                            "Documento:",
                            LiquidacionesState.liquidacion_actual.get("documento", "N/A"),
                        ),
                        info_row(
                            "Período:",
                            LiquidacionesState.liquidacion_actual["periodo"],
                        ),
                        info_row(
                            "Propiedades:",
                            LiquidacionesState.liquidacion_actual.get("cantidad_propiedades", 0),
                        ),
                        info_row(
                            "Neto Total:",
                            rx.cond(
                                LiquidacionesState.liquidacion_actual.get("neto"),
                                rx.text(f"${LiquidacionesState.liquidacion_actual['neto']:,.0f}"),
                                "$0"
                            ),
                        ),
                        info_row(
                            "Estado:",
                            LiquidacionesState.liquidacion_actual.get("estado", "N/A"),
                        ),
                        padding="1em",
                        background="gray.50",
                        border_radius="8px",
                    ),
                    # Advertencia
                    rx.callout(
                        "Las liquidaciones en estado 'Pagada' NO serán eliminadas. Solo se eliminarán las liquidaciones en estado 'En Proceso' o 'Aprobada'. Los documentos asociados serán desvinculados pero no eliminados.",
                        icon="triangle-alert",
                        color_scheme="orange",
                        size="1",
                        margin_top="1em",
                    ),
                    # Checkbox de confirmación
                    rx.checkbox(
                        "Confirmo que deseo eliminar todas las liquidaciones no pagadas de este grupo",
                        checked=LiquidacionesState.group_delete_confirmed,
                        on_change=LiquidacionesState.set_group_delete_confirmed,
                        size="3",
                        margin_top="1em",
                    ),
                    # Error display
                    rx.cond(
                        LiquidacionesState.error_message != "",
                        rx.callout(
                            LiquidacionesState.error_message,
                            icon="triangle-alert",
                            color_scheme="red",
                            size="1",
                        ),
                        rx.box(),
                    ),
                    # Botones de acción
                    rx.hstack(
                        rx.dialog.close(
                            rx.button(
                                "Cancelar",
                                variant="soft",
                                color_scheme="gray",
                                on_click=LiquidacionesState.close_group_delete_modal,
                            ),
                        ),
                        rx.spacer(),
                        rx.button(
                            rx.icon("trash-2"),
                            "Eliminar No Pagadas",
                            on_click=LiquidacionesState.confirmar_eliminar_agrupadas,
                            color_scheme="red",
                            loading=LiquidacionesState.is_loading,
                            disabled=~LiquidacionesState.group_delete_confirmed,
                        ),
                        width="100%",
                        padding_top="1em",
                    ),
                    spacing="2",
                    width="100%",
                ),
                rx.box(),
            ),
            max_width="500px",
            max_height="80vh",
            overflow_y="auto",
            pointer_events="auto",
            z_index=Z_MODAL,
        ),
        open=LiquidacionesState.show_group_delete_modal,
    )
