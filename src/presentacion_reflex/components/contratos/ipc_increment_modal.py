"""
Modal para aplicación de Incremento IPC a contratos de arrendamiento.
"""
import reflex as rx
from src.presentacion_reflex.state.contratos_state import ContratosState


def ipc_increment_modal() -> rx.Component:
    """Modal para aplicar incremento IPC."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Aplicar Incremento IPC"),
            rx.dialog.description(
                "Aplicar incremento por Índice de Precios al Consumidor (IPC) "
                "al canon de arrendamiento. Esta operación es irreversible.",
                margin_bottom="1rem"
            ),
            
            # Error message
            rx.cond(
                ContratosState.error_message != "",
                rx.callout(
                    ContratosState.error_message,
                    icon="alert-circle",
                    color="red",
                    margin_bottom="1rem"
                )
            ),
            
            # Form
            rx.form(
                rx.vstack(
                    # Porcentaje IPC
                    rx.vstack(
                        rx.text("Porcentaje IPC *", size="2", weight="bold"),
                        rx.input(
                            type="number",
                            name="porcentaje_ipc",
                            placeholder="5.62",
                            step="0.01",
                            min="0.01",
                            max="20",
                            required=True,
                            value=ContratosState.form_data.get("porcentaje_ipc", ""),
                            on_change=lambda v: ContratosState.set_form_field("porcentaje_ipc", v)
                        ),
                        rx.text(
                            "Ejemplo: 5.62 para 5.62% de incremento",
                            size="1",
                            color="gray"
                        ),
                        spacing="1",
                        width="100%"
                    ),
                    
                    # Fecha de aplicación
                    rx.vstack(
                        rx.text("Fecha de Aplicación *", size="2", weight="bold"),
                        rx.input(
                            type="date",
                            name="fecha_aplicacion",
                            required=True,
                            value=ContratosState.form_data.get("fecha_aplicacion", ""),
                            on_change=lambda v: ContratosState.set_form_field("fecha_aplicacion", v)
                        ),
                        spacing="1",
                        width="100%"
                    ),
                    
                    # Observaciones
                    rx.vstack(
                        rx.text("Observaciones (opcional)", size="2", weight="bold"),
                        rx.text_area(
                            name="observaciones",
                            placeholder="Notas adicionales sobre el incremento...",
                            value=ContratosState.form_data.get("observaciones", ""),
                            on_change=lambda v: ContratosState.set_form_field("observaciones", v),
                            min_height="80px"
                        ),
                        spacing="1",
                        width="100%"
                    ),
                    
                    spacing="4",
                    width="100%"
                ),
                
                # Buttons
                rx.flex(
                    rx.dialog.close(
                        rx.button(
                            "Cancelar",
                            variant="soft",
                            color_scheme="gray",
                            on_click=ContratosState.close_ipc_modal
                        )
                    ),
                    rx.button(
                        rx.cond(
                            ContratosState.is_loading,
                            rx.spinner(size="1"),
                            rx.text("Aplicar IPC")
                        ),
                        type="submit",
                        disabled=ContratosState.is_loading,
                        color_scheme="green"
                    ),
                    spacing="3",
                    margin_top="1rem",
                    justify="end"
                ),
                
                on_submit=ContratosState.apply_ipc_increment,
                reset_on_submit=False
            ),
            
            max_width="500px"
        ),
        open=ContratosState.show_ipc_modal,
        on_open_change=ContratosState.close_ipc_modal
    )
