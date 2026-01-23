
import reflex as rx
from src.presentacion_reflex.state.recibos_state import RecibosState

def payment_modal() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Registrar Pago"),
            rx.dialog.description(
                "Ingrese los detalles del pago realizado."
            ),
            rx.flex(
                rx.vstack(
                    rx.text("Fecha de Pago", weight="bold"),
                    rx.input(
                        type="date",
                        value=RecibosState.payment_data["fecha_pago"],
                        on_change=lambda val: RecibosState.set_payment_field("fecha_pago", val),
                        width="100%",
                    ),
                    width="100%",
                ),
                rx.vstack(
                    rx.text("Comprobante / Referencia", weight="bold"),
                    rx.input(
                        placeholder="Ej: TRX-123456",
                        value=RecibosState.payment_data["comprobante"],
                        on_change=lambda val: RecibosState.set_payment_field("comprobante", val),
                        width="100%",
                    ),
                    width="100%",
                ),
                rx.cond(
                    RecibosState.error_message != "",
                    rx.callout(
                        RecibosState.error_message,
                        icon="triangle_alert",
                        color_scheme="red",
                        role="alert",
                        width="100%"
                    )
                ),
                direction="column",
                spacing="4",
                margin_y="4"
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button("Cancelar", variant="soft", color_scheme="gray"),
                ),
                rx.button(
                    "Confirmar Pago", 
                    on_click=RecibosState.register_payment,
                    loading=RecibosState.is_loading,
                    color_scheme="green"
                ),
                spacing="3",
                justify="end",
            ),
        ),
        open=RecibosState.show_payment_modal,
        on_open_change=RecibosState.handle_payment_open_change,
    )
