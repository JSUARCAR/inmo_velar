"""
Formulario modal para gestión de Recibos Públicos.
"""

import reflex as rx

from src.presentacion_reflex.state.recibos_state import RecibosState
from src.presentacion_reflex.components.neuro_elements import neuro_input, neuro_button, neuro_select_root
from src.presentacion_reflex import styles


def modal_form() -> rx.Component:
    """Formulario para crear o editar un recibo público."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.cond(
                    RecibosState.selected_recibo_id > 0,
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
                                rx.text("Propiedad *", size="2", weight="bold", margin_bottom="1"),
                                neuro_select_root(
                                    rx.foreach(
                                        RecibosState.propiedades_options,
                                        lambda x: rx.select.item(x["label"], value=x["value"]),
                                    ),
                                    placeholder="Seleccione propiedad...",
                                    name="id_propiedad",
                                    required=True,
                                    value=RecibosState.form_data["id_propiedad"],
                                    on_change=lambda val: RecibosState.set_form_field(
                                        "id_propiedad", val
                                    ),
                                ),
                                width="100%",
                            ),
                            # Tipo de Servicio
                            rx.box(
                                rx.text(
                                    "Tipo de Servicio *",
                                    size="2",
                                    weight="bold",
                                    margin_bottom="1",
                                ),
                                neuro_select_root(
                                    [
                                        rx.select.item("Agua", value="Agua"),
                                        rx.select.item("Luz", value="Luz"),
                                        rx.select.item("Gas", value="Gas"),
                                        rx.select.item("Internet", value="Internet"),
                                        rx.select.item("Teléfono", value="Teléfono"),
                                        rx.select.item("Aseo", value="Aseo"),
                                        rx.select.item("Otros", value="Otros"),
                                    ],
                                    placeholder="Seleccione servicio...",
                                    name="tipo_servicio",
                                    required=True,
                                    value=RecibosState.form_data["tipo_servicio"],
                                    on_change=lambda val: RecibosState.set_form_field(
                                        "tipo_servicio", val
                                    ),
                                ),
                                width="100%",
                            ),
                            # Periodo
                            rx.box(
                                rx.text(
                                    "Período (Mes/Año) *",
                                    size="2",
                                    weight="bold",
                                    margin_bottom="1",
                                ),
                                neuro_input(
                                    name="periodo_recibo",
                                    placeholder="Ej: Enero 2024",
                                    required=True,
                                    value=RecibosState.form_data["periodo_recibo"],
                                    on_change=lambda val: RecibosState.set_form_field(
                                        "periodo_recibo", val
                                    ),
                                ),
                                width="100%",
                            ),
                            # Valor
                            rx.box(
                                rx.text("Valor Facturado *", size="2", weight="bold", margin_bottom="1"),
                                neuro_input(
                                    name="valor_total",
                                    type="number",
                                    placeholder="0",
                                    required=True,
                                    value=RecibosState.form_data["valor_total"],
                                    on_change=lambda val: RecibosState.set_form_field(
                                        "valor_total", val
                                    ),
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
                                rx.text("Fecha Desde", size="2", weight="bold", margin_bottom="1"),
                                neuro_input(
                                    name="fecha_desde",
                                    type="date",
                                    value=RecibosState.form_data["fecha_desde"],
                                    on_change=lambda val: RecibosState.set_form_field(
                                        "fecha_desde", val
                                    ),
                                ),
                                width="100%",
                            ),
                            # Fecha Hasta
                            rx.box(
                                rx.text("Fecha Hasta", size="2", weight="bold", margin_bottom="1"),
                                neuro_input(
                                    name="fecha_hasta",
                                    type="date",
                                    value=RecibosState.form_data["fecha_hasta"],
                                    on_change=lambda val: RecibosState.set_form_field(
                                        "fecha_hasta", val
                                    ),
                                ),
                                width="100%",
                            ),
                            # Vencimiento
                            rx.box(
                                rx.text(
                                    "Fecha Vencimiento *", size="2", weight="bold", margin_bottom="1"
                                ),
                                neuro_input(
                                    name="fecha_vencimiento",
                                    type="date",
                                    required=True,
                                    value=RecibosState.form_data["fecha_vencimiento"],
                                    on_change=lambda val: RecibosState.set_form_field(
                                        "fecha_vencimiento", val
                                    ),
                                ),
                                width="100%",
                            ),
                            # Referencia
                            rx.box(
                                rx.text(
                                    "Referencia de Pago", size="2", weight="bold", margin_bottom="1"
                                ),
                                neuro_input(
                                    name="referencia_pago",
                                    placeholder="Número de contrato o factura",
                                    value=RecibosState.form_data["referencia_pago"],
                                    on_change=lambda val: RecibosState.set_form_field(
                                        "referencia_pago", val
                                    ),
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
                        rx.text("Observaciones", size="2", weight="bold", margin_bottom="1"),
                        rx.text_area(
                            name="observaciones",
                            placeholder="Notas adicionales...",
                            width="100%",
                            value=RecibosState.form_data["observaciones"],
                            on_change=lambda val: RecibosState.set_form_field("observaciones", val),
                        ),
                        width="100%",
                        margin_top="4",
                    ),
                    direction="column",
                    width="100%",
                ),
                rx.flex(
                    rx.dialog.close(
                        rx.button(
                            "Cancelar",
                            variant="soft",
                            color_scheme="gray",
                            type="button",
                            on_click=RecibosState.close_modal,
                        )
                    ),
                    rx.button(
                        rx.cond(
                            RecibosState.selected_recibo_id > 0,
                            "Guardar Cambios",
                            "Crear Recibo",
                        ),
                        type="submit",
                        loading=RecibosState.is_loading,
                    ),
                    spacing="3",
                    justify="end",
                    margin_top="4",
                ),
                on_submit=RecibosState.handle_save_form,
            ),
            max_width="700px",
        ),
        open=RecibosState.show_form_modal,
        on_open_change=RecibosState.set_show_form_modal,
    )
