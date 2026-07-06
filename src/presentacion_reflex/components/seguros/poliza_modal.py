"""
Modal Form para Crear Pólizas de Seguro
"""

import reflex as rx

from src.presentacion_reflex.state.seguros_state import SegurosState
from src.presentacion_reflex.components.neuro_elements import (
    neuro_floating_input,
    neuro_button,
)


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
                            icon="triangle-alert",
                            color_scheme="red",
                            role="alert",
                            width="100%",
                        ),
                    ),
                    # Número de Póliza *
                    neuro_floating_input(
                        label="Número de Póliza *",
                        value=SegurosState.poliza_form_data["numero_poliza"],
                        name="numero_poliza",
                        required=True,
                        placeholder="Ej: POL-2024-001",
                    ),
                    # Contrato ID *
                    neuro_floating_input(
                        label="ID Contrato de Arrendamiento *",
                        value="",
                        name="id_contrato",
                        type="number",
                        required=True,
                        placeholder="Ej: 1",
                    ),
                    rx.text(
                        "Ingrese el ID del contrato de arrendamiento",
                        size="1",
                        color="gray",
                    ),
                    # Seguro ID *
                    neuro_floating_input(
                        label="ID Seguro *",
                        value="",
                        name="id_seguro",
                        type="number",
                        required=True,
                        placeholder="Ej: 1",
                    ),
                    rx.text(
                        "Ingrese el ID del seguro a asignar", size="1", color="gray"
                    ),
                    # Fecha Inicio y Fecha Fin (en fila)
                    rx.hstack(
                        neuro_floating_input(
                            label="Fecha Inicio *",
                            value=SegurosState.poliza_form_data["fecha_inicio"],
                            name="fecha_inicio",
                            type="date",
                            required=True,
                        ),
                        neuro_floating_input(
                            label="Fecha Fin *",
                            value=SegurosState.poliza_form_data["fecha_fin"],
                            name="fecha_fin",
                            type="date",
                            required=True,
                        ),
                        spacing="3",
                        width="100%",
                    ),
                    # Botones
                    rx.hstack(
                        rx.dialog.close(
                            neuro_button(
                                "Cancelar",
                                variant="soft",
                                color_scheme="gray",
                                type="button",
                                on_click=SegurosState.close_poliza_modal,
                                tooltip_content="Cerrar modal sin guardar",
                            ),
                        ),
                        neuro_button(
                            "Crear Póliza",
                            type="submit",
                            loading=SegurosState.is_loading,
                            tooltip_content="Guardar nueva póliza de seguro",
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
