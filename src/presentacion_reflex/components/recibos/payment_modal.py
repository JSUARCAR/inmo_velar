import reflex as rx

from src.presentacion_reflex.state.recibos_state import RecibosState
from src.presentacion_reflex.components.neuro_elements import (
    neuro_floating_input,
    neuro_button,
)


def payment_modal() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Registrar Pago"),
            rx.dialog.description("Ingrese los detalles del pago realizado."),
            rx.flex(
                neuro_floating_input(
                    label="Fecha de Pago",
                    value=RecibosState.payment_data["fecha_pago"],
                    on_change=lambda val: RecibosState.set_payment_field(
                        "fecha_pago", val
                    ),
                    type="date",
                ),
                neuro_floating_input(
                    label="Comprobante / Referencia",
                    value=RecibosState.payment_data["comprobante"],
                    on_change=lambda val: RecibosState.set_payment_field(
                        "comprobante", val
                    ),
                    placeholder="Ej: TRX-123456",
                ),
                rx.cond(
                    RecibosState.error_message != "",
                    rx.callout(
                        RecibosState.error_message,
                        icon="triangle-alert",
                        color_scheme="red",
                        role="alert",
                        width="100%",
                    ),
                ),
                direction="column",
                spacing="4",
                margin_y="4",
            ),
            rx.flex(
                rx.dialog.close(
                    neuro_button(
                        "Cancelar",
                        variant="soft",
                        color_scheme="gray",
                        tooltip_content="Cancelar registro de pago",
                    ),
                ),
                neuro_button(
                    "Confirmar Pago",
                    on_click=RecibosState.register_payment,
                    loading=RecibosState.is_loading,
                    color_scheme="green",
                    tooltip_content="Confirmar y registrar el pago",
                ),
                spacing="3",
                justify="end",
            ),
        ),
        open=RecibosState.show_payment_modal,
        on_open_change=RecibosState.handle_payment_open_change,
    )
