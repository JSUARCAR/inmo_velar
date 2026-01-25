"""
Modal de Confirmación para Reversar Liquidación
"""

import reflex as rx

from src.presentacion_reflex.state.liquidaciones_state import LiquidacionesState


def reverse_confirm_dialog() -> rx.Component:
    """Diálogo de confirmación para reversar una liquidación"""
    return rx.alert_dialog.root(
        rx.alert_dialog.content(
            rx.alert_dialog.title("Confirmar Reversión"),
            rx.alert_dialog.description(
                rx.vstack(
                    rx.text(
                        "¿Está seguro que desea reversar esta liquidación?",
                        size="3",
                    ),
                    rx.text(
                        "La liquidación volverá al estado 'En Proceso' y se eliminarán los datos de aprobación.",
                        size="2",
                        color="gray",
                    ),
                    spacing="2",
                    align="start",
                ),
            ),
            rx.alert_dialog.action(
                rx.hstack(
                    rx.alert_dialog.cancel(
                        rx.button(
                            "Cancelar",
                            variant="soft",
                            color_scheme="gray",
                            on_click=LiquidacionesState.close_reverse_confirm,
                        ),
                    ),
                    rx.alert_dialog.action(
                        rx.button(
                            rx.icon("rotate_ccw"),
                            "Confirmar Reversión",
                            on_click=LiquidacionesState.confirmar_reversar,
                            color_scheme="yellow",
                        ),
                    ),
                    spacing="3",
                ),
            ),
        ),
        open=LiquidacionesState.show_reverse_confirm,
    )
