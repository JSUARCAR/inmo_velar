import reflex as rx

from src.presentacion_reflex.state.liquidacion_asesores.form_state import (
    LiquidacionFormState,
)
from src.presentacion_reflex.components.neuro_elements import (
    neuro_text_area,
    neuro_button,
)


def annul_modal() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Anular Liquidación"),
            rx.dialog.description(
                "¿Está seguro de que desea anular esta liquidación? Esta acción no se puede deshacer."
            ),
            rx.flex(
                rx.text("Motivo de anulación:", size="2", mb="1", weight="bold"),
                neuro_text_area(
                    placeholder="Ingrese el motivo de la anulación...",
                    value=LiquidacionFormState.annul_reason,
                    on_change=LiquidacionFormState.set_annul_reason,
                ),
                direction="column",
                spacing="3",
            ),
            rx.flex(
                rx.dialog.close(
                    neuro_button(
                        "Cancelar",
                        color_scheme="gray",
                        on_click=LiquidacionFormState.close_modal,
                        tooltip_content="Cerrar sin anular",
                    ),
                ),
                neuro_button(
                    "Anular Liquidación",
                    color_scheme="red",
                    on_click=lambda: LiquidacionFormState.anular_liquidacion(
                        LiquidacionFormState.selected_liquidacion_id,
                        LiquidacionFormState.annul_reason,
                    ),
                    tooltip_content="Confirmar anulación de la liquidación",
                ),
                spacing="3",
                mt="4",
                justify="end",
            ),
            max_width="450px",
        ),
        open=LiquidacionFormState.show_annul_modal,
        on_open_change=LiquidacionFormState.set_show_annul_modal,
    )
