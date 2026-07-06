"""
Modal de Confirmación para Reversar Pago de Liquidación
"""

import reflex as rx

from src.presentacion_reflex.state.liquidaciones_state import LiquidacionesState
from src.presentacion_reflex.components.neuro_elements import neuro_text_area


def reverse_pago_confirm_dialog() -> rx.Component:
    """Diálogo de confirmación para reversar el pago de una liquidación (Pagada → Aprobada)."""
    return rx.alert_dialog.root(
        rx.alert_dialog.content(
            rx.alert_dialog.title("Reversar Pago"),
            rx.alert_dialog.description(
                rx.vstack(
                    rx.text(
                        "¿Está seguro que desea reversar el pago de esta liquidación?",
                        size="3",
                    ),
                    rx.text(
                        "La liquidación volverá al estado 'Aprobada' y se eliminarán los datos de pago.",
                        size="2",
                        color="gray",
                    ),
                    rx.cond(
                        LiquidacionesState.liquidacion_actual,
                        rx.box(
                            rx.text(
                                "Propietario: ",
                                LiquidacionesState.liquidacion_actual.get(
                                    "propietario", "N/A"
                                ),
                                weight="bold",
                            ),
                            rx.text(
                                "Dirección: ",
                                LiquidacionesState.liquidacion_actual.get(
                                    "propiedad", "N/A"
                                ),
                                weight="bold",
                            ),
                            rx.text(
                                "Período: ",
                                LiquidacionesState.liquidacion_actual.get(
                                    "periodo", "N/A"
                                ),
                                weight="bold",
                            ),
                            spacing="1",
                            padding="0.75em",
                            background="gray.50",
                            border_radius="8px",
                            margin_top="0.5em",
                        ),
                        rx.box(),
                    ),
                    rx.vstack(
                        rx.text(
                            "Motivo de reversión (requerido, mínimo 10 caracteres):",
                            size="2",
                            weight="medium",
                        ),
                        neuro_text_area(
                            placeholder="Ingrese el motivo de la reversión del pago...",
                            value=LiquidacionesState.reverse_pago_motivo,
                            on_change=LiquidacionesState.set_reverse_pago_motivo,
                            min_height="80px",
                            width="100%",
                        ),
                        spacing="2",
                        align="start",
                        width="100%",
                    ),
                    spacing="2",
                    align="start",
                ),
            ),
            rx.alert_dialog.action(
                rx.hstack(
                    rx.alert_dialog.cancel(
                        rx.tooltip(
                            rx.button(
                                "Cancelar",
                                variant="soft",
                                color_scheme="gray",
                                on_click=LiquidacionesState.close_reverse_pago_confirm,
                            ),
                            content="Cerrar sin reversar el pago",
                        ),
                    ),
                    rx.alert_dialog.action(
                        rx.tooltip(
                            rx.button(
                                rx.icon("rotate_ccw"),
                                "Confirmar Reversión",
                                on_click=LiquidacionesState.confirmar_reversar_pago,
                                color_scheme="orange",
                                loading=LiquidacionesState.is_loading,
                            ),
                            content="Revertir el pago y volver al estado Aprobada",
                        ),
                    ),
                    spacing="3",
                ),
            ),
        ),
        open=LiquidacionesState.show_reverse_pago_confirm,
    )
