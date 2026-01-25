"""
Formulario de Creación de Liquidación
"""

from typing import Any

import reflex as rx

from src.presentacion_reflex.state.liquidaciones_state import LiquidacionesState


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
    return rx.vstack(
        rx.text(label, size="2", weight="medium", color="gray.700"),
        rx.input(
            name=name,
            placeholder=placeholder,
            type=type,
            default_value=default_value if value is None else None,
            value=value,
            on_change=on_change,
            required=required,
            read_only=read_only,
            width="100%",
            variant="surface" if read_only else "soft",
        ),
        spacing="1",
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
                        rx.vstack(
                            rx.text("Contrato de Mandato/Propiedad", size="2", weight="medium"),
                            rx.select(
                                LiquidacionesState.propiedades_select_options,
                                name="id_propiedad",
                                placeholder="Seleccione propiedad...",
                                on_change=LiquidacionesState.handle_propiedad_change,
                                required=True,
                                width="100%",
                            ),
                            spacing="1",
                        ),
                        rx.grid(
                            form_field(
                                "Propietario",
                                "nombre_propietario",
                                "Autocargado...",
                                read_only=True,
                                value=LiquidacionesState.form_data["nombre_propietario"],
                            ),
                            form_field(
                                "Dirección Inmueble",
                                "direccion_propiedad",
                                "Autocargado...",
                                read_only=True,
                                value=LiquidacionesState.form_data["direccion_propiedad"],
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
                            on_change=lambda val: LiquidacionesState.set_form_field("periodo", val),
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
                            "Gastos Reparaciones",
                            "gastos_reparaciones",
                            "0",
                            type="number",
                            value=LiquidacionesState.form_data["gastos_reparaciones"],
                            on_change=lambda val: LiquidacionesState.set_form_field(
                                "gastos_reparaciones", val
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
                    rx.text_area(
                        name="observaciones",
                        placeholder="Detalles adicionales sobre la liquidación...",
                        width="100%",
                    ),
                    rx.divider(margin_y="1em"),
                    # Botones
                    rx.hstack(
                        rx.dialog.close(
                            rx.button(
                                "Cancelar", variant="soft", color_scheme="gray", type="button"
                            ),
                        ),
                        rx.spacer(),
                        rx.button("Generar Liquidación", type="submit", color_scheme="blue"),
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
