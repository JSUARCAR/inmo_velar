import reflex as rx
from typing import Callable

from src.presentacion_reflex.components.neuro_elements import (
    neuro_floating_input,
    neuro_button,
)


def bulk_modal_form(
    is_open: rx.Var,
    on_open_change: Callable,
    form_data: rx.Var,
    on_submit: Callable,
    is_loading: rx.Var,
) -> rx.Component:
    """
    Formulario para generar liquidaciones masivas de asesores.

    Args:
        is_open: Estado de apertura del modal
        on_open_change: Event handler para cambiar el estado de apertura
        form_data: Diccionario con datos del formulario (periodo)
        on_submit: Event handler para el envío del formulario
        is_loading: Estado de carga
    """
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                "Generación Masiva de Liquidaciones",
                font_size="20px",
                font_weight="700",
                margin_bottom="1rem",
            ),
            rx.dialog.description(
                "Esta acción generará liquidaciones para TODOS los asesores activos que tengan contratos de arrendamiento vigentes en el período seleccionado.",
                margin_bottom="1.5rem",
                color="gray",
            ),
            rx.form.root(
                rx.flex(
                    # Período
                    neuro_floating_input(
                        label="Período a Liquidar (YYYY-MM)",
                        name="periodo",
                        type="month",
                        required=True,
                        value=form_data["periodo"],
                        width="100%",
                    ),
                    rx.callout(
                        "Nota: Se omitirán los asesores que ya tengan una liquidación generada para este período.",
                        icon="info",
                        color_scheme="blue",
                        size="1",
                        margin_top="1rem",
                    ),
                    # Botones
                    rx.flex(
                        rx.dialog.close(
                            neuro_button(
                                "Cancelar",
                                color_scheme="gray",
                                type="button",
                                tooltip_content="Cerrar sin generar",
                            )
                        ),
                        neuro_button(
                            rx.cond(
                                is_loading,
                                rx.flex(
                                    rx.spinner(size="1"),
                                    rx.text("Procesando..."),
                                    spacing="2",
                                ),
                                "Generar Liquidaciones",
                            ),
                            type="submit",
                            disabled=is_loading,
                            tooltip_content="Generar liquidaciones para todos los asesores activos",
                        ),
                        spacing="3",
                        justify="end",
                        margin_top="1.5rem",
                        width="100%",
                    ),
                    direction="column",
                    width="100%",
                ),
                on_submit=on_submit,
            ),
            max_width="450px",
        ),
        open=is_open,
        on_open_change=on_open_change,
    )
