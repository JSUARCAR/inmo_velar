import reflex as rx
from src.presentacion_reflex.state.liquidacion_asesores.form_state import LiquidacionFormState
from src.presentacion_reflex import styles
from src.presentacion_reflex.components.neuro_elements import neuro_button, neuro_input

def reverse_modal() -> rx.Component:
    """Modal para reversar una liquidación con campo de motivo condicional."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    rx.icon("rotate-ccw", size=24, color=styles.BRAND_PRIMARY),
                    rx.heading("Confirmar Reversión", size="5", color=styles.TEXT_PRIMARY),
                    align="center",
                    spacing="3",
                ),
                rx.text(
                    "¿Está seguro de reversar el estado de esta liquidación?",
                    size="3",
                    color=styles.TEXT_SECONDARY,
                ),
                rx.cond(
                    LiquidacionFormState.reverse_motivo_requerido,
                    rx.vstack(
                        rx.text("Motivo de la reversión (mín. 10 caracteres):", size="2", weight="bold"),
                        neuro_input(
                            placeholder="Ingrese el motivo de la reversión...",
                            value=LiquidacionFormState.reverse_motivo,
                            on_change=LiquidacionFormState.set_reverse_motivo,
                            width="100%",
                        ),
                        width="100%",
                        align_items="start",
                        spacing="2",
                    )
                ),
                rx.hstack(
                    neuro_button(
                        "Cancelar",
                        on_click=LiquidacionFormState.close_reverse_modal,
                        variant="soft",
                        color_scheme="gray",
                    ),
                    neuro_button(
                        "Reversar",
                        on_click=LiquidacionFormState.reversar_liquidacion(
                            LiquidacionFormState.liquidacion_id_for_action,
                            LiquidacionFormState.reverse_motivo
                        ),
                        color_scheme="blue",
                        disabled=rx.cond(
                            LiquidacionFormState.reverse_motivo_requerido,
                            LiquidacionFormState.reverse_motivo.length() < 10,
                            False
                        ),
                    ),
                    justify="end",
                    width="100%",
                    spacing="3",
                    margin_top="4",
                ),
                spacing="4",
                width="100%",
            ),
            style=styles.NEU_PANEL_STYLE,
            max_width="450px",
        ),
        open=LiquidacionFormState.show_reverse_modal,
        on_open_change=lambda _: LiquidacionFormState.close_reverse_modal(),
    )
