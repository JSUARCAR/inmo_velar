"""
Modal de Cancelación de Liquidación
Permite ingresar el motivo de cancelación
"""

import reflex as rx
from src.presentacion_reflex.state.liquidaciones_state import LiquidacionesState


def cancel_modal() -> rx.Component:
    """Modal para cancelar una liquidación individual"""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.hstack(
                    rx.icon("circle_x", size=24, color="red"),
                    "Cancelar Liquidación",
                    spacing="2",
                )
            ),
            rx.dialog.description(
                "Ingrese el motivo de cancelación. Esta acción no se puede deshacer.",
                color="gray",
            ),
            
            rx.vstack(
                rx.text(
                    "Motivo de cancelación:",
                    weight="medium",
                    size="2",
                ),
                rx.text_area(
                    placeholder="Ingrese el motivo (mínimo 10 caracteres)...",
                    value=LiquidacionesState.cancel_motivo,
                    on_change=LiquidacionesState.set_cancel_motivo,
                    min_height="100px",
                    width="100%",
                ),
                rx.cond(
                    LiquidacionesState.error_message != "",
                    rx.callout(
                        LiquidacionesState.error_message,
                        icon="triangle_alert",
                        color_scheme="red",
                        size="1",
                    ),
                    rx.box(),
                ),
                
                rx.hstack(
                    rx.dialog.close(
                        rx.button(
                            "Cancelar",
                            variant="soft",
                            color_scheme="gray",
                            on_click=LiquidacionesState.close_cancel_modal,
                        ),
                    ),
                    rx.spacer(),
                    rx.button(
                        rx.icon("circle_x"),
                        "Confirmar Cancelación",
                        on_click=LiquidacionesState.confirmar_cancelacion,
                        color_scheme="red",
                        loading=LiquidacionesState.is_loading,
                    ),
                    width="100%",
                    padding_top="1em",
                ),
                
                spacing="3",
                width="100%",
            ),
            
            max_width="500px",
        ),
        open=LiquidacionesState.show_cancel_modal,
    )
