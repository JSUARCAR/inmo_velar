"""
Componente Modal para Definición de Plan de Pago de Incidentes.
Feature: 003-integracion-incidentes-liquidaciones
Date: 2026-06-30
"""

import reflex as rx
from src.presentacion_reflex.state.incidentes_state import IncidentesState
from src.presentacion_reflex.components.neuro_elements import neuro_floating_input, neuro_button


def _plan_details_view() -> rx.Component:
    """Vista de solo lectura mostrando el plan de pago existente y sus cuotas."""
    return rx.flex(
        # Encabezado del plan
        rx.box(
            rx.flex(
                rx.icon("check-circle", size=16, color="var(--green-9)"),
                rx.text("Plan de Pago Activo", weight="bold", color="var(--green-9)"),
                spacing="2",
                align="center",
            ),
            padding="3",
            background_color=rx.color("green", 1),
            border_radius="md",
            margin_bottom="4",
            width="100%",
        ),
        # Resumen del plan
        rx.grid(
            rx.box(
                rx.text("Total del Plan", size="2", color="var(--gray-9)"),
                rx.text(
                    "$ ",
                    IncidentesState.plan_pago_data.get("total_plan", 0).to_string(),
                    weight="bold",
                    size="4",
                ),
                padding="3",
                background_color=rx.color("gray", 1),
                border_radius="md",
            ),
            rx.box(
                rx.text("N° Cuotas", size="2", color="var(--gray-9)"),
                rx.text(
                    IncidentesState.plan_pago_data.get("num_cuotas", 0).to_string(),
                    weight="bold",
                    size="4",
                ),
                padding="3",
                background_color=rx.color("gray", 1),
                border_radius="md",
            ),
            rx.box(
                rx.text("Valor Cuota", size="2", color="var(--gray-9)"),
                rx.text(
                    "$ ",
                    IncidentesState.plan_pago_data.get("valor_cuota", 0).to_string(),
                    weight="bold",
                    size="4",
                ),
                padding="3",
                background_color=rx.color("gray", 1),
                border_radius="md",
            ),
            rx.box(
                rx.text("Estado", size="2", color="var(--gray-9)"),
                rx.text(
                    IncidentesState.plan_pago_data.get("estado", "N/A"),
                    weight="bold",
                    size="4",
                ),
                padding="3",
                background_color=rx.color("gray", 1),
                border_radius="md",
            ),
            columns="4",
            spacing="3",
            width="100%",
            margin_bottom="4",
        ),
        # Lista de cuotas
        rx.text("Detalle de Cuotas", weight="bold", size="3", margin_bottom="2"),
        rx.cond(
            IncidentesState.plan_pago_cuotas.length() > 0,
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("N°"),
                        rx.table.column_header_cell("Valor"),
                        rx.table.column_header_cell("Estado"),
                        rx.table.column_header_cell("Liquidación"),
                    ),
                ),
                rx.table.body(
                    rx.foreach(
                        IncidentesState.plan_pago_cuotas,
                        lambda cuota: rx.table.row(
                            rx.table.cell(cuota.get("numero_cuota", "")),
                            rx.table.cell(
                                "$ ",
                                cuota.get("valor_cuota", 0).to_string(),
                            ),
                            rx.table.cell(
                                rx.badge(
                                    cuota.get("estado_pago", "Pendiente"),
                                    color_scheme=rx.cond(
                                        cuota.get("estado_pago") == "Pagada",
                                        "green",
                                        rx.cond(
                                            cuota.get("estado_pago") == "Asociado",
                                            "blue",
                                            "gray",
                                        ),
                                    ),
                                ),
                            ),
                            rx.table.cell(
                                rx.cond(
                                    cuota.get("id_liquidacion"),
                                    cuota.get("id_liquidacion").to_string(),
                                    rx.text("Sin asociar", color="var(--gray-9)"),
                                ),
                            ),
                        ),
                    ),
                ),
                width="100%",
            ),
            rx.text("No hay cuotas registradas.", color="var(--gray-9)"),
        ),
        # Botón cerrar
        rx.flex(
            rx.dialog.close(
                neuro_button(
                    "Cerrar",
                    variant="soft",
                    color_scheme="gray",
                    on_click=IncidentesState.close_plan_pago_modal,
                    tooltip_content="Cerrar plan de pago",
                )
            ),
            justify="end",
            margin_top="4",
        ),
        direction="column",
        spacing="3",
        width="100%",
    )


def _plan_creation_form() -> rx.Component:
    """Formulario para crear un nuevo plan de pago."""
    return rx.flex(
        # Información del incidente
        rx.box(
            rx.flex(
                rx.icon("info", size=16, color="var(--blue-9)"),
                rx.text(
                    "Costo Total: $",
                    rx.cond(
                        IncidentesState.plan_pago_data,
                        IncidentesState.plan_pago_data.get("total_plan", 0).to_string(),
                        "0",
                    ),
                    weight="bold",
                ),
                spacing="2",
                align="center",
            ),
            padding="3",
            background_color=rx.color("blue", 1),
            border_radius="md",
            margin_bottom="4",
        ),
        # Formulario
        rx.form(
            rx.flex(
                neuro_floating_input(
                    label="Número de Cuotas",
                    name="num_cuotas",
                    type="number",
                    min_=1,
                    max_=12,
                    value=IncidentesState.plan_pago_num_cuotas,
                    on_change=IncidentesState.set_plan_pago_num_cuotas,
                    required=True,
                    width="100%",
                ),
                neuro_floating_input(
                    label="Valor por Cuota",
                    name="valor_cuota",
                    type="number",
                    min_=1,
                    value=IncidentesState.plan_pago_valor_cuota,
                    required=True,
                    width="100%",
                    read_only=True,
                ),
                direction="column",
                spacing="3",
                width="100%",
            ),
            # Resumen del plan
            rx.cond(
                IncidentesState.plan_pago_num_cuotas > 0,
                rx.box(
                    rx.flex(
                        rx.icon("calculator", size=16, color="var(--green-9)"),
                        rx.text(
                            "Resumen: ",
                            IncidentesState.plan_pago_num_cuotas,
                            " cuotas de $",
                            IncidentesState.plan_pago_valor_cuota.to_string(),
                            weight="bold",
                        ),
                        spacing="2",
                        align="center",
                    ),
                    padding="3",
                    background_color=rx.color("green", 1),
                    border_radius="md",
                    margin_top="3",
                ),
            ),
            # Mostrar error si existe
            rx.cond(
                IncidentesState.plan_pago_error != "",
                rx.callout(
                    IncidentesState.plan_pago_error,
                    icon="triangle-alert",
                    color_scheme="red",
                    margin_top="3",
                ),
            ),
            # Botones de acción DENTRO del form
            rx.flex(
                rx.dialog.close(
                    neuro_button(
                        "Cancelar",
                        variant="soft",
                        color_scheme="gray",
                        on_click=IncidentesState.close_plan_pago_modal,
                        tooltip_content="Cancelar creación de plan",
                    )
                ),
                neuro_button(
                    "Crear Plan",
                    type="submit",
                    color_scheme="green",
                    disabled=IncidentesState.plan_pago_loading,
                    tooltip_content="Crear plan de pago",
                ),
                justify="end",
                gap="3",
                margin_top="4",
            ),
            on_submit=IncidentesState.crear_plan_pago,
            width="100%",
        ),
        direction="column",
        spacing="4",
        width="100%",
    )


def modal_plan_pago() -> rx.Component:
    """Modal para definir o consultar plan de pago del incidente."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.flex(
                    rx.icon("dollar-sign", size=20),
                    rx.text(
                        rx.cond(
                            IncidentesState.plan_pago_data.get("id_plan_pago", None),
                            "Plan de Pago",
                            "Definir Plan de Pago",
                        )
                    ),
                    spacing="2",
                    align="center",
                )
            ),
            rx.dialog.description(
                rx.cond(
                    IncidentesState.plan_pago_data.get("id_plan_pago", None),
                    "Detalle del plan de pago y cuotas del incidente.",
                    "Defina el número de cuotas y valor por cuota para el plan de pago del incidente.",
                )
            ),
            rx.cond(
                IncidentesState.plan_pago_loading,
                rx.flex(
                    rx.spinner(size="3"),
                    rx.text("Cargando..."),
                    spacing="2",
                    align="center",
                    justify="center",
                    padding="4",
                ),
                rx.cond(
                    IncidentesState.plan_pago_data.get("id_plan_pago", None),
                    _plan_details_view(),
                    _plan_creation_form(),
                ),
            ),
        ),
        open=IncidentesState.show_plan_pago_modal,
    )
