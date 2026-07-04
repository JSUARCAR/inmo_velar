"""
Modal de Confirmación para Eliminar Liquidación
Muestra resumen de la liquidación y desglose financiero antes de confirmar.
"""

import reflex as rx

from src.presentacion_reflex.state.liquidaciones_state import LiquidacionesState


def info_row(label: str, value) -> rx.Component:
    """Fila de información (label: value)."""
    return rx.hstack(
        rx.text(label, weight="medium", color="gray.700"),
        rx.spacer(),
        rx.text(value, weight="bold"),
        width="100%",
        padding_y="0.3em",
    )


def section_header(title: str) -> rx.Component:
    """Header de sección."""
    return rx.heading(
        title,
        size="5",
        margin_top="0.8em",
        margin_bottom="0.4em",
    )


def delete_confirm_dialog() -> rx.Component:
    """Diálogo de confirmación para eliminar una liquidación"""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.hstack(
                    rx.icon("trash-2", size=24, color="red"),
                    "Eliminar Liquidación",
                    spacing="2",
                )
            ),
            rx.dialog.description(
                rx.text(
                    "Esta acción es irreversible. La liquidación será eliminada permanentemente del sistema.",
                    color="red.600",
                    weight="medium",
                ),
            ),
            rx.cond(
                LiquidacionesState.liquidacion_actual,
                rx.vstack(
                    # Resumen de la liquidación
                    section_header("Resumen de la Liquidación"),
                    rx.box(
                        info_row(
                            "Propietario:",
                            LiquidacionesState.liquidacion_actual["propietario"],
                        ),
                        info_row(
                            "Propiedad:",
                            LiquidacionesState.liquidacion_actual["direccion"],
                        ),
                        info_row(
                            "Período:",
                            LiquidacionesState.liquidacion_actual["periodo"],
                        ),
                        info_row(
                            "Neto a Pagar:",
                            rx.cond(
                                LiquidacionesState.liquidacion_actual["neto"],
                                rx.text(
                                    f"${LiquidacionesState.liquidacion_actual['neto']:,.0f}"
                                ),
                                "$0",
                            ),
                        ),
                        info_row(
                            "Estado:",
                            LiquidacionesState.liquidacion_actual["estado"],
                        ),
                        padding="1em",
                        background="gray.50",
                        border_radius="8px",
                    ),
                    # Desglose Financiero
                    section_header("Desglose Financiero"),
                    rx.box(
                        info_row(
                            "Total Ingresos:",
                            rx.cond(
                                LiquidacionesState.liquidacion_actual["total_ingresos"],
                                rx.text(
                                    f"${LiquidacionesState.liquidacion_actual['total_ingresos']:,.0f}"
                                ),
                                "$0",
                            ),
                        ),
                        info_row(
                            "Comisión:",
                            rx.cond(
                                LiquidacionesState.liquidacion_actual["comision"],
                                rx.text(
                                    f"${LiquidacionesState.liquidacion_actual['comision']:,.0f}"
                                ),
                                "$0",
                            ),
                        ),
                        info_row(
                            "IVA:",
                            rx.cond(
                                LiquidacionesState.liquidacion_actual["iva"],
                                rx.text(
                                    f"${LiquidacionesState.liquidacion_actual['iva']:,.0f}"
                                ),
                                "$0",
                            ),
                        ),
                        info_row(
                            "Gastos Admin:",
                            rx.cond(
                                LiquidacionesState.liquidacion_actual["gastos_admin"],
                                rx.text(
                                    f"${LiquidacionesState.liquidacion_actual['gastos_admin']:,.0f}"
                                ),
                                "$0",
                            ),
                        ),
                        info_row(
                            "Gastos Servicios:",
                            rx.cond(
                                LiquidacionesState.liquidacion_actual[
                                    "gastos_servicios"
                                ],
                                rx.text(
                                    f"${LiquidacionesState.liquidacion_actual['gastos_servicios']:,.0f}"
                                ),
                                "$0",
                            ),
                        ),
                        info_row(
                            "Gastos Reparaciones:",
                            rx.cond(
                                LiquidacionesState.liquidacion_actual[
                                    "gastos_reparaciones"
                                ],
                                rx.text(
                                    f"${LiquidacionesState.liquidacion_actual['gastos_reparaciones']:,.0f}"
                                ),
                                "$0",
                            ),
                        ),
                        info_row(
                            "Pago Predial:",
                            rx.cond(
                                LiquidacionesState.liquidacion_actual["pago_predial"],
                                rx.text(
                                    f"${LiquidacionesState.liquidacion_actual['pago_predial']:,.0f}"
                                ),
                                "$0",
                            ),
                        ),
                        info_row(
                            "Otros Egresos:",
                            rx.cond(
                                LiquidacionesState.liquidacion_actual["otros_egresos"],
                                rx.text(
                                    f"${LiquidacionesState.liquidacion_actual['otros_egresos']:,.0f}"
                                ),
                                "$0",
                            ),
                        ),
                        info_row(
                            "Total Egresos:",
                            rx.cond(
                                LiquidacionesState.liquidacion_actual["total_egresos"],
                                rx.text(
                                    f"${LiquidacionesState.liquidacion_actual['total_egresos']:,.0f}"
                                ),
                                "$0",
                            ),
                        ),
                        padding="1em",
                        background="gray.50",
                        border_radius="8px",
                    ),
                    # Advertencia
                    rx.callout(
                        "Esta liquidación será eliminada permanentemente del sistema. Los documentos asociados serán desvinculados pero no eliminados.",
                        icon="triangle-alert",
                        color_scheme="red",
                        size="1",
                        margin_top="1em",
                    ),
                    # Checkbox de confirmación
                    rx.checkbox(
                        "Confirmo que deseo eliminar esta liquidación permanentemente",
                        checked=LiquidacionesState.delete_confirmed,
                        on_change=LiquidacionesState.set_delete_confirmed,
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
                                on_click=LiquidacionesState.close_delete_modal,
                            ),
                        ),
                        rx.spacer(),
                        rx.button(
                            rx.icon("trash-2"),
                            "Eliminar",
                            on_click=LiquidacionesState.confirmar_eliminar,
                            color_scheme="red",
                            loading=LiquidacionesState.is_loading,
                            disabled=~LiquidacionesState.delete_confirmed,
                        ),
                        width="100%",
                        padding_top="1em",
                    ),
                    spacing="2",
                    width="100%",
                ),
                rx.box(),
            ),
            max_width="600px",
            max_height="80vh",
            overflow_y="auto",
        ),
        open=LiquidacionesState.show_delete_modal,
    )
