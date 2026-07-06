"""
Formulario modal para gestión de Recibos Públicos.
"""

import reflex as rx

from src.presentacion_reflex.state.recibos_state import RecibosState
from src.presentacion_reflex.components.neuro_elements import (
    neuro_floating_input,
    neuro_floating_select,
    neuro_button,
)


def modal_form() -> rx.Component:
    """Formulario para crear o editar un recibo público."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.cond(
                    RecibosState.is_editing,
                    "Editar Recibo Público",
                    "Nuevo Recibo Público",
                )
            ),
            rx.dialog.description(
                "Ingrese los detalles del recibo del servicio público."
            ),
            rx.form.root(
                rx.flex(
                    rx.grid(
                        rx.flex(
                            # Propiedad
                            rx.box(
                                neuro_floating_select(
                                    label="Propiedad *",
                                    value=RecibosState.form_data["id_propiedad"],
                                    options=RecibosState.propiedades_disponibles,
                                    on_change=lambda val: RecibosState.set_form_field(
                                        "id_propiedad", val
                                    ),
                                    name="id_propiedad",
                                    required=True,
                                    placeholder="Seleccione propiedad...",
                                ),
                                width="100%",
                            ),
                            # Tipo de Servicio
                            rx.box(
                                neuro_floating_select(
                                    label="Tipo de Servicio *",
                                    value=RecibosState.form_data["tipo_servicio"],
                                    options=[
                                        {"label": "Agua", "value": "Agua"},
                                        {"label": "Luz", "value": "Luz"},
                                        {"label": "Gas", "value": "Gas"},
                                        {"label": "Internet", "value": "Internet"},
                                        {"label": "Teléfono", "value": "Teléfono"},
                                        {"label": "Aseo", "value": "Aseo"},
                                        {"label": "Otros", "value": "Otros"},
                                    ],
                                    on_change=lambda val: RecibosState.set_form_field(
                                        "tipo_servicio", val
                                    ),
                                    name="tipo_servicio",
                                    required=True,
                                    placeholder="Seleccione servicio...",
                                ),
                                width="100%",
                            ),
                            # Periodo
                            rx.box(
                                neuro_floating_input(
                                    label="Período (Mes/Año) *",
                                    value=RecibosState.form_data["periodo_recibo"],
                                    on_change=lambda val: RecibosState.set_form_field(
                                        "periodo_recibo", val
                                    ),
                                    name="periodo_recibo",
                                    required=True,
                                    placeholder="Ej: Enero 2024",
                                ),
                                width="100%",
                            ),
                            # Valor
                            rx.box(
                                neuro_floating_input(
                                    label="Valor Facturado *",
                                    value=RecibosState.form_data["valor_recibo"],
                                    on_change=lambda val: RecibosState.set_form_field(
                                        "valor_recibo", val
                                    ),
                                    name="valor_recibo",
                                    type="number",
                                    required=True,
                                    placeholder="0",
                                ),
                                width="100%",
                            ),
                            direction="column",
                            spacing="4",
                            width="100%",
                        ),
                        rx.flex(
                            # Fecha Desde
                            rx.box(
                                neuro_floating_input(
                                    label="Fecha Desde",
                                    value=RecibosState.form_data["fecha_desde"],
                                    on_change=lambda val: RecibosState.set_form_field(
                                        "fecha_desde", val
                                    ),
                                    name="fecha_desde",
                                    type="date",
                                ),
                                width="100%",
                            ),
                            # Fecha Hasta
                            rx.box(
                                neuro_floating_input(
                                    label="Fecha Hasta",
                                    value=RecibosState.form_data["fecha_hasta"],
                                    on_change=lambda val: RecibosState.set_form_field(
                                        "fecha_hasta", val
                                    ),
                                    name="fecha_hasta",
                                    type="date",
                                ),
                                width="100%",
                            ),
                            # Vencimiento
                            rx.box(
                                neuro_floating_input(
                                    label="Fecha Vencimiento *",
                                    value=RecibosState.form_data["fecha_vencimiento"],
                                    on_change=lambda val: RecibosState.set_form_field(
                                        "fecha_vencimiento", val
                                    ),
                                    name="fecha_vencimiento",
                                    type="date",
                                    required=True,
                                ),
                                width="100%",
                            ),
                            # Referencia
                            rx.box(
                                neuro_floating_input(
                                    label="Referencia de Pago",
                                    value=RecibosState.form_data.get(
                                        "referencia_pago", ""
                                    ),
                                    on_change=lambda val: RecibosState.set_form_field(
                                        "referencia_pago", val
                                    ),
                                    name="referencia_pago",
                                    placeholder="Número de contrato o factura",
                                ),
                                width="100%",
                            ),
                            direction="column",
                            spacing="4",
                            width="100%",
                        ),
                        columns="2",
                        spacing="4",
                        width="100%",
                    ),
                    # Observaciones
                    rx.box(
                        rx.text(
                            "Observaciones", size="2", weight="bold", margin_bottom="1"
                        ),
                        rx.text_area(
                            name="observaciones",
                            placeholder="Notas adicionales...",
                            width="100%",
                            value=RecibosState.form_data["observaciones"],
                            on_change=lambda val: RecibosState.set_form_field(
                                "observaciones", val
                            ),
                        ),
                        width="100%",
                        margin_top="4",
                    ),
                    direction="column",
                    width="100%",
                ),
                rx.flex(
                    rx.dialog.close(
                        neuro_button(
                            "Cancelar",
                            variant="soft",
                            color_scheme="gray",
                            type="button",
                            on_click=lambda: RecibosState.handle_form_open_change(
                                False
                            ),
                            tooltip_content="Cerrar modal sin guardar",
                        )
                    ),
                    neuro_button(
                        rx.cond(
                            RecibosState.is_editing,
                            "Guardar Cambios",
                            "Crear Recibo",
                        ),
                        type="submit",
                        loading=RecibosState.is_loading,
                        tooltip_content="Guardar recibo público",
                    ),
                    spacing="3",
                    justify="end",
                    margin_top="4",
                ),
                on_submit=RecibosState.save_recibo,
            ),
            max_width="700px",
        ),
        open=RecibosState.show_form_modal,
        on_open_change=RecibosState.handle_form_open_change,
    )
