"""
Formulario de Edición de Liquidación
"""

import reflex as rx

from src.presentacion_reflex.state.liquidaciones_state import LiquidacionesState
from src.presentacion_reflex.state.auth_state import AuthState
from src.presentacion_reflex import styles


def form_field_readonly(label: str, name: str, value: str) -> rx.Component:
    """Campo de solo lectura para el formulario de edición."""
    return rx.vstack(
        rx.text(label, size="2", weight="medium", color="gray.700"),
        rx.input(
            name=name,
            default_value=value,
            read_only=True,
            width="100%",
            style=styles.NEU_INPUT_STYLE,
            variant="surface",
        ),
        spacing="1",
        width="100%",
    )


def form_field_editable(
    label: str, name: str, default_value: str, type: str = "number"
) -> rx.Component:
    """Campo editable para el formulario de edición."""
    return rx.vstack(
        rx.text(label, size="2", weight="medium", color="gray.700"),
        rx.input(
            name=name,
            default_value=default_value,
            type=type,
            width="100%",
            style=styles.NEU_INPUT_STYLE,
            variant="soft",
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


def liquidacion_edit_form() -> rx.Component:
    """Modal con formulario para editar una liquidación existente."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Editar Liquidación"),
            rx.dialog.description(
                "Modifique los valores variables. El período y contrato no pueden cambiarse."
            ),
            rx.form.root(
                rx.vstack(
                    rx.input(
                        name="id_liquidacion",
                        value=LiquidacionesState.form_data["id_liquidacion"],
                        type="hidden",
                    ),
                    section_title("Información General"),
                    rx.grid(
                        rx.grid(
                            form_field_readonly(
                                "Propietario",
                                "nombre_propietario",
                                LiquidacionesState.form_data["nombre_propietario"],
                            ),
                            form_field_readonly(
                                "Dirección Inmueble",
                                "direccion_propiedad",
                                LiquidacionesState.form_data["direccion_propiedad"],
                            ),
                            columns="2",
                            spacing="3",
                            width="100%",
                        ),
                        form_field_readonly(
                            "Canon Mandato",
                            "canon_mandato",
                            LiquidacionesState.form_data["canon_mandato"],
                        ),
                        form_field_readonly(
                            "ID Contrato",
                            "id_contrato_m",
                            LiquidacionesState.form_data["id_contrato_m"],
                        ),
                        form_field_readonly(
                            "Período",
                            "periodo",
                            LiquidacionesState.form_data["periodo"],
                        ),
                        columns="2",
                        spacing="3",
                        width="100%",
                    ),
                    section_title("Ingresos"),
                    form_field_editable(
                        "Otros Ingresos",
                        "otros_ingresos",
                        LiquidacionesState.form_data["otros_ingresos"],
                    ),
                    section_title("Egresos Variables"),
                    rx.grid(
                        form_field_editable(
                            "Gastos Administración",
                            "gastos_administracion",
                            LiquidacionesState.form_data["gastos_administracion"],
                        ),
                        form_field_editable(
                            "Gastos Servicios",
                            "gastos_servicios",
                            LiquidacionesState.form_data["gastos_servicios"],
                        ),
                        form_field_editable(
                            "Incidentes",
                            "valor_incidentes",
                            LiquidacionesState.form_data["valor_incidentes"],
                        ),
                        form_field_editable(
                            "Pago Predial",
                            "pago_predial",
                            LiquidacionesState.form_data["pago_predial"],
                        ),
                        form_field_editable(
                            "Otros Egresos",
                            "otros_egresos",
                            LiquidacionesState.form_data["otros_egresos"],
                        ),
                        columns="2",
                        spacing="3",
                        width="100%",
                    ),
                    # Botón Seleccionar Incidentes (solo para liquidaciones en proceso)
                    rx.cond(
                        LiquidacionesState.form_data["estado"] == "En Proceso",
                        rx.cond(
                            AuthState.check_action("Liquidaciones", "SELECCIONAR_INCIDENTES"),
                            rx.button(
                                rx.hstack(
                                    rx.icon("link", size=16),
                                    rx.text("Seleccionar Incidentes"),
                                ),
                                on_click=LiquidacionesState.open_seleccion_incidentes_modal(
                                    LiquidacionesState.form_data["id_liquidacion"]
                                ),
                                type="button",
                                variant="soft",
                                color_scheme="orange",
                                margin_top="1em",
                            ),
                        ),
                    ),
                    section_title("Observaciones"),
                    rx.text_area(
                        name="observaciones",
                        default_value=LiquidacionesState.form_data["observaciones"],
                        placeholder="Detalles adicionales sobre la liquidación...",
                        width="100%",
                        style=styles.NEU_INPUT_STYLE,
                    ),
                    rx.divider(margin_y="1em"),
                    rx.hstack(
                        rx.dialog.close(
                            rx.button(
                                "Cancelar",
                                variant="soft",
                                color_scheme="gray",
                                type="button",
                            ),
                        ),
                        rx.spacer(),
                        rx.button(
                            "Guardar Cambios", type="submit", color_scheme="blue"
                        ),
                        width="100%",
                    ),
                    spacing="4",
                    width="100%",
                ),
                on_submit=LiquidacionesState.save_liquidacion,
            ),
            max_width="600px",
        ),
        open=LiquidacionesState.show_edit_modal,
        on_open_change=LiquidacionesState.close_modal,
    )
