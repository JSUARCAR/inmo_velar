"""
Formulario de Edición de Liquidación
"""

import reflex as rx

from src.presentacion_reflex.state.liquidaciones_state import LiquidacionesState


def form_field(
    label: str,
    name: str,
    value: str = "",
    type: str = "text",
    read_only: bool = False,
    required: bool = False,
) -> rx.Component:
    """Campo de formulario reutilizable con binding de valor."""
    return rx.vstack(
        rx.text(label, size="2", weight="medium", color="gray.700"),
        rx.input(
            name=name,
            default_value=value,  # Usamos default_value para que sea editable
            type=type,
            read_only=read_only,
            required=required,
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
                    # Campos Ocultos para IDs
                    rx.input(
                        name="id_liquidacion",
                        value=LiquidacionesState.form_data["id_liquidacion"],
                        type="hidden",
                    ),
                    # Información Inmutable
                    section_title("Información General"),
                    rx.grid(
                        form_field(
                            "ID Contrato",
                            "id_contrato_m",
                            LiquidacionesState.form_data["id_contrato_m"].to(str),
                            read_only=True,
                        ),
                        form_field(
                            "Período",
                            "periodo",
                            LiquidacionesState.form_data["periodo"],
                            read_only=True,
                        ),
                        columns="2",
                        spacing="3",
                        width="100%",
                    ),
                    # Ingresos Editables
                    section_title("Ingresos"),
                    rx.grid(
                        form_field(
                            "Otros Ingresos",
                            "otros_ingresos",
                            LiquidacionesState.form_data["otros_ingresos"].to(str),
                            type="number",
                        ),
                        spacing="3",
                        width="100%",
                    ),
                    # Egresos Editables
                    section_title("Egresos Variables"),
                    rx.grid(
                        form_field(
                            "Gastos Administración",
                            "gastos_administracion",
                            LiquidacionesState.form_data["gastos_administracion"].to(str),
                            type="number",
                        ),
                        form_field(
                            "Gastos Servicios",
                            "gastos_servicios",
                            LiquidacionesState.form_data["gastos_servicios"].to(str),
                            type="number",
                        ),
                        form_field(
                            "Gastos Reparaciones",
                            "gastos_reparaciones",
                            LiquidacionesState.form_data["gastos_reparaciones"].to(str),
                            type="number",
                        ),
                        form_field(
                            "Otros Egresos",
                            "otros_egresos",
                            LiquidacionesState.form_data["otros_egresos"].to(str),
                            type="number",
                        ),
                        columns="2",
                        spacing="3",
                        width="100%",
                    ),
                    # Observaciones
                    section_title("Observaciones"),
                    rx.text_area(
                        name="observaciones",
                        default_value=LiquidacionesState.form_data["observaciones"],
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
                        rx.button("Guardar Cambios", type="submit", color_scheme="blue"),
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
