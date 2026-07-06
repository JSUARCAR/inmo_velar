"""
Formulario para generar liquidaciones masivas por propietario.
Permite seleccionar un propietario y período para generar liquidaciones consolidadas.
"""

from typing import Callable

import reflex as rx


from src.presentacion_reflex.components.neuro_elements import neuro_floating_input

def bulk_liquidacion_form(
    form_data: rx.Var,
    on_submit: Callable,
    on_cancel: Callable,
    is_loading: rx.Var,
):
    """
    Formulario para generar liquidación masiva de TODOS los propietarios.

    Args:
        form_data: Dict con periodo
        on_submit: Callback al enviar
        on_cancel: Callback al cancelar
        is_loading: Estado de carga
    """
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                "Nueva Liquidación Masiva por Propietario",
                font_size="20px",
                font_weight="700",
                margin_bottom="1rem",
            ),
            rx.dialog.description(
                "Genera liquidaciones para todas las propiedades activas de TODOS los propietarios en el período seleccionado.",
                size="2",
                margin_bottom="1rem",
                color="#666",
            ),
            # Formulario
            rx.form(
                rx.vstack(
                    # Período
                    neuro_floating_input(
                        label="Período (YYYY-MM)",
                        value=form_data["periodo"],
                        name="periodo",
                        placeholder="2026-01",
                        type="month",
                        required=True,
                        width="100%",
                    ),
                    # Info box
                    rx.callout(
                        "Se generará una liquidación individual por cada propiedad con contrato de mandato activo.",
                        icon="info",
                        color_scheme="blue",
                        size="1",
                        width="100%",
                    ),
                    # Botones
                    rx.hstack(
                        rx.dialog.close(
                            rx.tooltip(
                                rx.button(
                                    "Cancelar",
                                    variant="soft",
                                    color_scheme="gray",
                                    on_click=on_cancel,
                                ),
                                content="Cerrar sin generar",
                            )
                        ),
                        rx.tooltip(
                            rx.button(
                                rx.cond(
                                    is_loading,
                                    rx.hstack(
                                        rx.spinner(size="1"),
                                        rx.text("Generando..."),
                                        spacing="2",
                                    ),
                                    rx.text("Generar Liquidaciones"),
                                ),
                                type="submit",
                                disabled=is_loading,
                            ),
                            content="Generar liquidaciones para todos los propietarios activos",
                        ),
                        spacing="3",
                        justify="end",
                        width="100%",
                    ),
                    spacing="4",
                    width="100%",
                ),
                on_submit=on_submit,
                reset_on_submit=False,
            ),
            max_width="500px",
            padding="1.5rem",
        ),
        open=True,
    )
