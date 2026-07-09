import reflex as rx
from src.presentacion_reflex.state.liquidacion_asesores.form_state import LiquidacionFormState
from src.presentacion_reflex import styles
from src.presentacion_reflex.components.neuro_elements import neuro_button

def delete_modal() -> rx.Component:
    """Modal de confirmación para eliminar una liquidación."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    rx.icon("trash-2", size=24, color="var(--red-9)"),
                    rx.heading("Confirmar Eliminación", size="5", color=styles.TEXT_PRIMARY),
                    align="center",
                    spacing="3",
                ),
                rx.text(
                    "¿Está seguro de eliminar esta liquidación? Esta acción no se puede deshacer.",
                    size="3",
                    color=styles.TEXT_SECONDARY,
                ),
                rx.hstack(
                    neuro_button(
                        "Cancelar",
                        on_click=LiquidacionFormState.close_delete_modal,
                        variant="soft",
                        color_scheme="gray",
                    ),
                    neuro_button(
                        "Eliminar",
                        on_click=LiquidacionFormState.eliminar_liquidacion(
                            LiquidacionFormState.liquidacion_id_for_action
                        ),
                        color_scheme="red",
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
        open=LiquidacionFormState.show_delete_confirm_modal,
        on_open_change=lambda _: LiquidacionFormState.close_delete_modal(),
    )
