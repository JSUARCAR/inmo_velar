"""
Modal Form para Crear Pólizas de Seguro
"""

import reflex as rx
from src.presentacion_reflex.state.seguros_state import SegurosState


def modal_poliza() -> rx.Component:
    """Modal para crear póliza de seguro."""
    
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Nueva Póliza de Seguro"),
            rx.dialog.description(
                "Asigne un seguro a un contrato de arrendamiento. Todos los campos son obligatorios.",
                size="2",
                margin_bottom="4",
            ),
            
            rx.form(
                rx.vstack(
                    # Error message
                    rx.cond(
                        SegurosState.error_message != "",
                        rx.callout(
                            SegurosState.error_message,
                            icon="triangle_alert",
                            color_scheme="red",
                            role="alert",
                            width="100%",
                        ),
                    ),
                    
                    # Número de Póliza *
                    rx.vstack(
                        rx.text("Número de Póliza *", size="2", weight="bold"),
                        rx.input(
                            name="numero_poliza",
                            placeholder="Ej: POL-2024-001",
                            required=True,
                            default_value=SegurosState.poliza_form_data["numero_poliza"],
                            width="100%",
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    
                    # Contrato ID *
                    rx.vstack(
                        rx.text("ID Contrato de Arrendamiento *", size="2", weight="bold"),
                        rx.input(
                            name="id_contrato",
                            type="number",
                            placeholder="Ej: 1",
                            required=True,
                            width="100%",
                        ),
                        rx.text(
                            "Ingrese el ID del contrato de arrendamiento",
                            size="1",
                            color="gray"
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    
                    # Seguro ID *
                    rx.vstack(
                        rx.text("ID Seguro *", size="2", weight="bold"),
                        rx.input(
                            name="id_seguro",
                            type="number",
                            placeholder="Ej: 1",
                            required=True,
                            width="100%",
                        ),
                        rx.text(
                            "Ingrese el ID del seguro a asignar",
                            size="1",
                            color="gray"
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    
                    # Fecha Inicio y Fecha Fin (en fila)
                    rx.hstack(
                        rx.vstack(
                            rx.text("Fecha Inicio *", size="2", weight="bold"),
                            rx.input(
                                name="fecha_inicio",
                                type="date",
                                required=True,
                                default_value=SegurosState.poliza_form_data["fecha_inicio"],
                                width="100%",
                            ),
                            width="50%",
                            spacing="1",
                        ),
                        rx.vstack(
                            rx.text("Fecha Fin *", size="2", weight="bold"),
                            rx.input(
                                name="fecha_fin",
                                type="date",
                                required=True,
                                default_value=SegurosState.poliza_form_data["fecha_fin"],
                                width="100%",
                            ),
                            width="50%",
                            spacing="1",
                        ),
                        spacing="3",
                        width="100%",
                    ),
                    
                    # Botones
                    rx.hstack(
                        rx.dialog.close(
                            rx.button(
                                "Cancelar",
                                variant="soft",
                                color_scheme="gray",
                                type="button",
                                on_click=SegurosState.close_poliza_modal,
                            ),
                        ),
                        rx.button(
                            "Crear Póliza",
                            type="submit",
                            loading=SegurosState.is_loading,
                        ),
                        spacing="3",
                        justify="end",
                        margin_top="4",
                        width="100%",
                    ),
                    
                    spacing="4",
                    width="100%",
                ),
                on_submit=SegurosState.save_poliza,
                width="100%",
            ),
            
            max_width="550px",
            width="100%",
        ),
        open=SegurosState.show_poliza_modal,
    )
