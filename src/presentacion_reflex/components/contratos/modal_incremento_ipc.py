"""
Modal para aplicación de Incremento IPC a contratos de arrendamiento.
"""

import reflex as rx

from src.presentacion_reflex.state.contratos_state import ContratosState
from src.presentacion_reflex.components.neuro_elements import neuro_floating_input, neuro_text_area, neuro_button


def modal_incremento_ipc() -> rx.Component:
    """Modal para aplicar incremento IPC."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Aplicar Incremento IPC"),
            rx.dialog.description(
                "Aplicar incremento por Índice de Precios al Consumidor (IPC) "
                "al canon de arrendamiento. Esta operación es irreversible.",
                margin_bottom="1rem",
            ),
            # Error message
            rx.cond(
                ContratosState.error_message != "",
                rx.callout(
                    ContratosState.error_message,
                    icon="triangle-alert",
                    color="red",
                    margin_bottom="1rem",
                ),
            ),
            # Form
            rx.form(
                rx.vstack(
                    neuro_floating_input(
                        label="Porcentaje IPC",
                        type="number",
                        name="porcentaje_ipc",
                        placeholder="5.62",
                        step="0.01",
                        min="0.01",
                        max="20",
                        required=True,
                        value=ContratosState.form_data["porcentaje_ipc"],
                        on_change=lambda v: ContratosState.set_form_field("porcentaje_ipc", v),
                        width="100%",
                    ),
                    neuro_floating_input(
                        label="Fecha de Aplicación",
                        type="date",
                        name="fecha_application",
                        required=True,
                        value=ContratosState.form_data["fecha_aplicacion"],
                        on_change=lambda v: ContratosState.set_form_field("fecha_aplicacion", v),
                        width="100%",
                    ),
                    neuro_text_area(
                        label="Observaciones (opcional)",
                        name="observaciones",
                        placeholder="Notas adicionales sobre el incremento...",
                        value=ContratosState.form_data["observaciones"],
                        on_change=lambda v: ContratosState.set_form_field("observaciones", v),
                        width="100%",
                    ),
                    spacing="4",
                    width="100%",
                ),
                # Buttons
                rx.flex(
                    rx.dialog.close(
                        neuro_button(
                            "Cancelar",
                            variant="soft",
                            color_scheme="gray",
                            on_click=ContratosState.close_ipc_modal,
                            tooltip_content="Cancelar",
                        )
                    ),
                    neuro_button(
                        rx.cond(
                            ContratosState.is_loading,
                            rx.spinner(size="1"),
                            rx.text("Aplicar IPC"),
                        ),
                        type="submit",
                        disabled=ContratosState.is_loading,
                        color_scheme="green",
                        tooltip_content="Aplicar incremento IPC",
                    ),
                    spacing="3",
                    margin_top="1rem",
                    justify="end",
                ),
                on_submit=ContratosState.apply_ipc_increment,
                reset_on_submit=False,
            ),
            max_width="500px",
        ),
        open=ContratosState.show_ipc_modal,
        on_open_change=ContratosState.close_ipc_modal,
    )
