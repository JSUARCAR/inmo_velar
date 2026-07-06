"""
Modal Form para Crear/Editar Seguros
"""

import reflex as rx

from src.presentacion_reflex.state.seguros_state import SegurosState
from src.presentacion_reflex.components.neuro_elements import (
    neuro_floating_input,
    neuro_button,
)


def modal_seguro() -> rx.Component:
    """Modal para crear/editar seguro."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.cond(SegurosState.is_editing_seguro, "Editar Seguro", "Nuevo Seguro")
            ),
            rx.dialog.description(
                "Ingrese los datos del seguro. Los campos marcados con * son obligatorios.",
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
                    # Nombre del Seguro *
                    neuro_floating_input(
                        label="Nombre del Seguro *",
                        value=SegurosState.seguro_form_data["nombre_seguro"],
                        name="nombre_seguro",
                        required=True,
                        placeholder="Ej: Seguro Todo Riesgo",
                    ),
                    # Porcentaje y Fecha Inicio (en fila)
                    rx.hstack(
                        neuro_floating_input(
                            label="Porcentaje de Seguro * (%)",
                            value=SegurosState.seguro_form_data["porcentaje_seguro"],
                            name="porcentaje_seguro",
                            type="number",
                            required=True,
                            placeholder="Ej: 10",
                        ),
                        neuro_floating_input(
                            label="Fecha Inicio",
                            value=SegurosState.seguro_form_data["fecha_inicio_seguro"],
                            name="fecha_inicio_seguro",
                            type="date",
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
                                on_click=SegurosState.close_seguro_modal,
                                tooltip_content="Cerrar modal sin guardar",
                            ),
                        ),
                        neuro_button(
                            "Guardar",
                            type="submit",
                            loading=SegurosState.is_loading,
                            tooltip_content="Guardar datos del seguro",
                        ),
                        spacing="3",
                        justify="end",
                        margin_top="4",
                        width="100%",
                    ),
                    spacing="4",
                    width="100%",
                ),
                on_submit=SegurosState.save_seguro,
                width="100%",
            ),
            max_width="500px",
            width="100%",
        ),
        open=SegurosState.show_seguro_modal,
    )
