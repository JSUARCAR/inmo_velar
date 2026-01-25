import reflex as rx

from src.presentacion_reflex.state.liquidacion_asesores_state import LiquidacionAsesoresState


def annul_modal() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Anular Liquidación"),
            rx.dialog.description(
                "¿Está seguro de que desea anular esta liquidación? Esta acción no se puede deshacer."
            ),
            rx.flex(
                rx.text("Motivo de anulación:", size="2", mb="1", weight="bold"),
                rx.text_area(
                    placeholder="Ingrese el motivo de la anulación...",
                    value=LiquidacionAsesoresState.annul_reason,
                    on_change=LiquidacionAsesoresState.set_annul_reason,
                ),
                direction="column",
                spacing="3",
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button(
                        "Cancelar",
                        color_scheme="gray",
                        variant="soft",
                        on_click=LiquidacionAsesoresState.close_annul_modal,
                    ),
                ),
                rx.button(
                    "Anular Liquidación",
                    color_scheme="red",
                    on_click=LiquidacionAsesoresState.confirm_annulment,
                ),
                spacing="3",
                mt="4",
                justify="end",
            ),
            max_width="450px",
        ),
        open=LiquidacionAsesoresState.show_annul_modal,
        on_open_change=LiquidacionAsesoresState.close_annul_modal,
    )
