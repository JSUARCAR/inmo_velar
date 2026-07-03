"""
Modal de Selección de Incidentes para Liquidaciones.
Permite a los Administradores asociar incidentes aprobados a una liquidación
para aplicar descuentos al canon.

Feature: 003-integracion-incidentes-liquidaciones
Date: 2026-06-30
"""

import reflex as rx
from src.presentacion_reflex.state.liquidaciones_state import LiquidacionesState


def _badge_estado_pago(estado_pago: str) -> rx.Component:
    """Badge de color para el estado de pago."""
    color_map = {
        "Pendiente": "gray",
        "Parcialmente Pagado": "yellow",
        "Pagado": "green",
    }
    color = color_map.get(estado_pago, "gray")
    return rx.badge(estado_pago, color_scheme=color, size="1")


def _incidente_row(incidente: rx.Var) -> rx.Component:
    """Fila de un incidente en la tabla de selección."""
    return rx.table.row(
        rx.table.cell(
            rx.checkbox(
                default_checked=False,
                on_change=lambda _: LiquidacionesState.toggle_seleccion_incidente(incidente.id),
                disabled=incidente.ya_asociado,
            )
        ),
        rx.table.cell(rx.text(incidente.id, size="2")),
        rx.table.cell(rx.text(incidente.descripcion, size="2")),
        rx.table.cell(rx.text(incidente.propiedad, size="2")),
        rx.table.cell(rx.text(incidente.costo_view, size="2")),
        rx.table.cell(rx.text(incidente.num_cuota, size="2")),
        rx.table.cell(rx.text(incidente.valor_cuota_view, size="2")),
        rx.table.cell(_badge_estado_pago(incidente.estado_pago)),
        rx.table.cell(
            rx.cond(
                incidente.ya_asociado,
                rx.badge("Ya asociado", color_scheme="yellow", size="1"),
                rx.text("", size="2"),
            )
        ),
    )


def modal_seleccion_incidentes() -> rx.Component:
    """Modal para seleccionar incidentes a asociar a una liquidación."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.hstack(
                    rx.icon("link", size=20),
                    rx.text("Seleccionar Incidentes"),
                    spacing="2",
                    align="center",
                )
            ),
            rx.dialog.description(
                "Seleccione los incidentes que desea asociar a esta liquidación. "
                "El valor de cada cuota se descontará del neto a pagar.",
            ),
            rx.cond(
                LiquidacionesState.seleccion_incidentes_loading,
                rx.flex(
                    rx.spinner(size="3"),
                    rx.text("Cargando incidentes disponibles..."),
                    spacing="2",
                    align="center",
                    justify="center",
                    padding="8",
                ),
                rx.vstack(
                    rx.cond(
                        LiquidacionesState.seleccion_incidentes_disponibles.length() > 0,
                        rx.box(
                            rx.table.root(
                                rx.table.header(
                                    rx.table.row(
                                        rx.table.column_header_cell("Sel.", width="50px"),
                                        rx.table.column_header_cell("ID", width="50px"),
                                        rx.table.column_header_cell("Descripción"),
                                        rx.table.column_header_cell("Propiedad"),
                                        rx.table.column_header_cell("Costo", width="100px"),
                                        rx.table.column_header_cell("Cuota", width="70px"),
                                        rx.table.column_header_cell("Valor Cuota", width="110px"),
                                        rx.table.column_header_cell("Estado Pago"),
                                        rx.table.column_header_cell("Nota", width="80px"),
                                    )
                                ),
                                rx.table.body(
                                    rx.foreach(
                                        LiquidacionesState.seleccion_incidentes_disponibles,
                                        _incidente_row,
                                    )
                                ),
                                width="100%",
                                size="1",
                            ),
                            overflow_x="auto",
                            width="100%",
                        ),
                        rx.flex(
                            rx.text("No hay incidentes disponibles para asociar.", color="gray"),
                            padding="4",
                            justify="center",
                        ),
                    ),
                    rx.cond(
                        LiquidacionesState.seleccion_incidentes_seleccionados.length() > 0,
                        rx.box(
                            rx.flex(
                                rx.icon("calculator", size=16),
                                rx.text(
                                    "Seleccionados: ",
                                    LiquidacionesState.seleccion_incidentes_seleccionados.length(),
                                    " | Total descuentos: $",
                                    LiquidacionesState.seleccion_incidentes_total_descuentos.to_string(),
                                    weight="bold",
                                    size="2",
                                ),
                                spacing="2",
                                align="center",
                            ),
                            padding="3",
                            background_color=rx.color("blue", 1),
                            border_radius="md",
                            margin_top="3",
                        ),
                    ),
                    rx.cond(
                        LiquidacionesState.seleccion_incidentes_error != "",
                        rx.callout(
                            LiquidacionesState.seleccion_incidentes_error,
                            icon="triangle-alert",
                            color_scheme="red",
                            margin_top="3",
                        ),
                    ),
                    spacing="3",
                    width="100%",
                ),
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button(
                        "Cancelar",
                        variant="soft",
                        color_scheme="gray",
                        on_click=LiquidacionesState.close_seleccion_incidentes_modal,
                    )
                ),
                rx.button(
                    "Asociar Seleccionados",
                    on_click=LiquidacionesState.asociar_incidentes_seleccionados,
                    color_scheme="green",
                    disabled=LiquidacionesState.seleccion_incidentes_loading,
                ),
                justify="end",
                gap="3",
                margin_top="4",
            ),
            max_width="900px",
        ),
        open=LiquidacionesState.show_seleccion_incidentes_modal,
    )
