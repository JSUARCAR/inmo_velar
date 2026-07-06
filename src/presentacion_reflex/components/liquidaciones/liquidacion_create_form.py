"""
Formulario de Creación de Liquidación
"""

from typing import Any

import reflex as rx

from src.presentacion_reflex.state.liquidaciones_state import LiquidacionesState
from src.presentacion_reflex import styles


from src.presentacion_reflex.components.shared.searchable_select import (
    searchable_select,
)

from src.presentacion_reflex.components.neuro_elements import (
    neuro_floating_input,
    neuro_text_area,
)

def form_field(
    label: str,
    name: str,
    placeholder: str = "",
    type: str = "text",
    default_value: str = "",
    required: bool = False,
    read_only: bool = False,
    value: str = None,
    on_change: Any = None,
) -> rx.Component:
    """Campo de formulario reutilizable."""
    return rx.box(
        neuro_floating_input(
            label=label,
            value=value if value is not None else default_value,
            on_change=on_change,
            name=name,
            placeholder=placeholder,
            type=type,
            required=required,
            disabled=read_only,
            width="100%",
            size="2",
        ),
        width="100%",
    )


def section_title(title: str) -> rx.Component:
    """Título de sección del formulario."""
    return rx.text(
        title,
        size="3",
        weight="bold",
        color="blue.600",
        margin_top="1em",
        margin_bottom="0.5em",
    )


def liquidacion_create_form() -> rx.Component:
    """Modal con formulario para crear nueva liquidación."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Nueva Liquidación Mensual"),
            rx.dialog.description(
                "Genere una liquidación para un contrato de mandato. Los cálculos se realizarán automáticamente."
            ),
            rx.form.root(
                rx.vstack(
                    # Selección de Contrato y Período
                    section_title("Configuración Básica"),
                    rx.grid(
                        searchable_select(
                            "Contrato de Mandato/Propiedad",
                            "Seleccione propiedad...",
                            LiquidacionesState.propiedad_liq_selected_label,
                            LiquidacionesState.propiedad_liq_search,
                            LiquidacionesState.propiedad_liq_menu_open,
                            LiquidacionesState.filtered_propiedades_liq_options,
                            LiquidacionesState.set_propiedad_liq_search,
                            LiquidacionesState.toggle_propiedad_liq_menu,
                            LiquidacionesState.select_propiedad_liq,
                        ),
                        rx.grid(
                            form_field(
                                "Propietario",
                                "nombre_propietario",
                                "Autocargado...",
                                read_only=True,
                                value=LiquidacionesState.form_data[
                                    "nombre_propietario"
                                ],
                            ),
                            form_field(
                                "Dirección Inmueble",
                                "direccion_propiedad",
                                "Autocargado...",
                                read_only=True,
                                value=LiquidacionesState.form_data[
                                    "direccion_propiedad"
                                ],
                            ),
                            columns="2",
                            spacing="3",
                            width="100%",
                        ),
                        form_field(
                            "Canon Mandato",
                            "canon_mandato",
                            "Autocargado...",
                            read_only=True,
                            value=LiquidacionesState.form_data["canon_mandato"],
                        ),
                        form_field(
                            "ID Contrato Mandato",
                            "id_contrato_m",
                            "Ej: 1",
                            type="number",
                            required=True,
                            value=LiquidacionesState.form_data["id_contrato_m"],
                            on_change=lambda val: LiquidacionesState.set_form_field(
                                "id_contrato_m", val
                            ),
                        ),
                        form_field(
                            "Período (YYYY-MM)",
                            "periodo",
                            "Ej: 2023-10",
                            type="month",
                            required=True,
                            value=LiquidacionesState.form_data["periodo"],
                            on_change=lambda val: LiquidacionesState.set_form_field(
                                "periodo", val
                            ),
                        ),
                        columns="2",
                        spacing="3",
                        width="100%",
                    ),
                    rx.callout(
                        "Nota: Al ingresar el ID del contrato, el sistema cargará automáticamente el canon pactado.",
                        icon="info",
                        color_scheme="blue",
                        size="1",
                    ),
                    # Sección de Ingresos Adicionales
                    section_title("Ingresos Adicionales"),
                    rx.grid(
                        form_field(
                            "Otros Ingresos",
                            "otros_ingresos",
                            "0",
                            type="number",
                            value=LiquidacionesState.form_data["otros_ingresos"],
                            on_change=lambda val: LiquidacionesState.set_form_field(
                                "otros_ingresos", val
                            ),
                        ),
                        spacing="3",
                        width="100%",
                    ),
                    # Sección de Egresos Variables
                    section_title("Egresos Variables"),
                    rx.grid(
                        form_field(
                            "Gastos Administración",
                            "gastos_administracion",
                            "0",
                            type="number",
                            value=LiquidacionesState.form_data["gastos_administracion"],
                            on_change=lambda val: LiquidacionesState.set_form_field(
                                "gastos_administracion", val
                            ),
                        ),
                        form_field(
                            "Gastos Servicios",
                            "gastos_servicios",
                            "0",
                            type="number",
                            value=LiquidacionesState.form_data["gastos_servicios"],
                            on_change=lambda val: LiquidacionesState.set_form_field(
                                "gastos_servicios", val
                            ),
                        ),
                        form_field(
                            "Incidentes",
                            "gastos_reparaciones",
                            "0",
                            type="number",
                            value=LiquidacionesState.form_data["gastos_reparaciones"],
                            on_change=lambda val: LiquidacionesState.set_form_field(
                                "gastos_reparaciones", val
                            ),
                        ),
                        form_field(
                            "Pago Predial",
                            "pago_predial",
                            "0",
                            type="number",
                            value=LiquidacionesState.form_data["pago_predial"],
                            on_change=lambda val: LiquidacionesState.set_form_field(
                                "pago_predial", val
                            ),
                        ),
                        form_field(
                            "Otros Egresos",
                            "otros_egresos",
                            "0",
                            type="number",
                            value=LiquidacionesState.form_data["otros_egresos"],
                            on_change=lambda val: LiquidacionesState.set_form_field(
                                "otros_egresos", val
                            ),
                        ),
                        columns="2",
                        spacing="3",
                        width="100%",
                    ),
                    # Observaciones
                    section_title("Observaciones"),
                    neuro_text_area(
                        name="observaciones",
                        placeholder="Detalles adicionales sobre la liquidación...",
                        width="100%",
                    ),
                    rx.divider(margin_y="1em"),
                    # Botones
                    rx.hstack(
                        rx.dialog.close(
                            rx.tooltip(
                                rx.button(
                                    "Cancelar",
                                    variant="soft",
                                    color_scheme="gray",
                                    type="button",
                                ),
                                content="Cerrar sin guardar",
                            ),
                        ),
                        rx.spacer(),
                        rx.tooltip(
                            rx.button(
                                "Generar Liquidación", type="submit", color_scheme="blue"
                            ),
                            content="Crear la liquidación con los datos ingresados",
                        ),
                        width="100%",
                    ),
                    spacing="4",
                    width="100%",
                ),
                on_submit=LiquidacionesState.save_liquidacion,
                reset_on_submit=True,
            ),
            max_width="600px",
        ),
        open=LiquidacionesState.show_create_modal,
        on_open_change=LiquidacionesState.close_modal,
    )
