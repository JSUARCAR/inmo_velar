"""
Modal Form para Crear/Editar Seguros
"""

import reflex as rx

from src.presentacion_reflex.state.seguros_state import SegurosState


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
                            icon="triangle_alert",
                            color_scheme="red",
                            role="alert",
                            width="100%",
                        ),
                    ),
                    # Nombre del Seguro *
                    rx.vstack(
                        rx.text("Nombre del Seguro *", size="2", weight="bold"),
                        rx.input(
                            name="nombre_seguro",
                            placeholder="Ej: Seguro Todo Riesgo",
                            required=True,
                            default_value=SegurosState.seguro_form_data["nombre_seguro"],
                            width="100%",
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    # Porcentaje y Fecha Inicio (en fila)
                    rx.hstack(
                        rx.vstack(
                            rx.text("Porcentaje de Seguro * (%)", size="2", weight="bold"),
                            rx.input(
                                name="porcentaje_seguro",
                                type="number",
                                placeholder="Ej: 10",
                                required=True,
                                default_value=SegurosState.seguro_form_data["porcentaje_seguro"],
                                width="100%",
                            ),
                            width="50%",
                            spacing="1",
                        ),
                        rx.vstack(
                            rx.text("Fecha Inicio", size="2", weight="bold"),
                            rx.input(
                                name="fecha_inicio_seguro",
                                type="date",
                                default_value=SegurosState.seguro_form_data["fecha_inicio_seguro"],
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
                                on_click=SegurosState.close_seguro_modal,
                            ),
                        ),
                        rx.button(
                            "Guardar",
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
                on_submit=SegurosState.save_seguro,
                width="100%",
            ),
            max_width="500px",
            width="100%",
        ),
        open=SegurosState.show_seguro_modal,
    )
