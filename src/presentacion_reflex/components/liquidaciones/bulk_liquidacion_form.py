"""
Formulario para generar liquidaciones masivas por propietario.
Permite seleccionar un propietario y período para generar liquidaciones consolidadas.
"""

from typing import Callable

import reflex as rx


def bulk_liquidacion_form(
    form_data: rx.Var,
    propietarios_options: rx.Var,  # Lista de strings "Nombre - Documento"
    on_submit: Callable,
    on_cancel: Callable,
    is_loading: rx.Var,
):
    """
    Formulario para generar liquidación masiva de un propietario.

    Args:
        form_data: Dict con id_propietario y periodo
        propietarios_options: Lista de propietarios como "Nombre - Documento"
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
                "Genera liquidaciones para todas las propiedades activas de un propietario en el período seleccionado.",
                size="2",
                margin_bottom="1rem",
                color="#666",
            ),
            # Formulario
            rx.form(
                rx.vstack(
                    # Selector de propietario
                    rx.box(
                        rx.text("Propietario", font_weight="600", margin_bottom="0.5rem"),
                        rx.select(
                            propietarios_options,
                            placeholder="Seleccione un propietario...",
                            name="id_propietario",
                            required=True,
                            width="100%",
                        ),
                        width="100%",
                    ),
                    # Período
                    rx.box(
                        rx.text("Período (YYYY-MM)", font_weight="600", margin_bottom="0.5rem"),
                        rx.input(
                            placeholder="2026-01",
                            name="periodo",
                            type="month",
                            default_value=form_data["periodo"],
                            required=True,
                            width="100%",
                        ),
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
                            rx.button(
                                "Cancelar", variant="soft", color_scheme="gray", on_click=on_cancel
                            )
                        ),
                        rx.button(
                            rx.cond(
                                is_loading,
                                rx.hstack(
                                    rx.spinner(size="1"), rx.text("Generando..."), spacing="2"
                                ),
                                rx.text("Generar Liquidaciones"),
                            ),
                            type="submit",
                            disabled=is_loading,
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
