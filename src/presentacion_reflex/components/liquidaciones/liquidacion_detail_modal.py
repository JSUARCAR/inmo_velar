"""
Modal de Detalle de Liquidación
Muestra el breakdown completo de ingresos y egresos
"""

import reflex as rx
from src.presentacion_reflex.state.liquidaciones_state import LiquidacionesState


def format_money(amount: int) -> str:
    """Formatea un monto a pesos colombianos."""
    return f"${amount:,}".replace(",", ".")


def info_row(label: str, value) -> rx.Component:
    """Fila de información (label: value)."""
    return rx.hstack(
        rx.text(label, weight="medium", color="gray.700"),
        rx.spacer(),
        rx.text(value, weight="bold"),
        width="100%",
        padding_y="0.5em",
    )


def section_header(title: str, icon: str = "") -> rx.Component:
    """Header de sección."""
    return rx.heading(
        rx.hstack(
            rx.cond(
                icon != "",
                rx.icon(icon, size=20),
                rx.box(),
            ),
            title,
            spacing="2",
        ),
        size="5",
        margin_top="1em",
        margin_bottom="0.5em",
    )


def liquidacion_detail_modal() -> rx.Component:
    """Modal que muestra el detalle completo de una liquidación."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.hstack(
                    "Detalle de Liquidación",
                    rx.cond(
                        LiquidacionesState.liquidacion_actual,
                        rx.text(
                            f" - Período {LiquidacionesState.liquidacion_actual['periodo']}",
                            weight="regular",
                            color="gray",
                        ),
                        rx.box(),
                    ),
                    spacing="2",
                )
            ),
            
            rx.dialog.description(
                rx.cond(
                    LiquidacionesState.liquidacion_actual,
                    rx.match(
                        LiquidacionesState.liquidacion_actual["estado"],
                        ("En Proceso", rx.badge("En Proceso", color_scheme="yellow")),
                        ("Aprobada", rx.badge("Aprobada", color_scheme="blue")),
                        ("Pagada", rx.badge("Pagada", color_scheme="green")),
                        ("Cancelada", rx.badge("Cancelada", color_scheme="red")),
                        rx.badge("Desconocido"),
                    ),
                    rx.box(),
                )
            ),
            
            rx.cond(
                LiquidacionesState.liquidacion_actual,
                rx.vstack(
                    # Sección: Información General
                    section_header("Información General", "info"),
                    rx.box(
                        info_row("Propiedad:", LiquidacionesState.liquidacion_actual["propiedad"]),
                        info_row("Matrícula:", LiquidacionesState.liquidacion_actual["matricula"]),
                        info_row("Propietario:", LiquidacionesState.liquidacion_actual["propietario"]),
                        info_row("Documento:", LiquidacionesState.liquidacion_actual["documento"]),
                        info_row("Período:", LiquidacionesState.liquidacion_actual["periodo"]),
                        info_row("Fecha Generación:", LiquidacionesState.liquidacion_actual["fecha_generacion"]),
                        padding="1em",
                        background="gray.50",
                        border_radius="8px",
                    ),
                    
                    # Sección: Propiedades (solo si es consolidado)
                    rx.cond(
                        LiquidacionesState.propiedades_consolidadas,
                        rx.vstack(
                            section_header("Propiedades Incluidas", "home"),
                            rx.table.root(
                                rx.table.header(
                                    rx.table.row(
                                        rx.table.column_header_cell("Dirección"),
                                        rx.table.column_header_cell("Matrícula"),
                                        rx.table.column_header_cell("Canon"),
                                        rx.table.column_header_cell("Neto"),
                                    )
                                ),
                                rx.table.body(
                                    rx.foreach(
                                        LiquidacionesState.propiedades_consolidadas,
                                        lambda prop: rx.table.row(
                                            rx.table.cell(prop["direccion"], max_width="200px"),
                                            rx.table.cell(prop["matricula"]),
                                            rx.table.cell(format_money(prop["canon"])),
                                            rx.table.cell(
                                                format_money(prop["neto"]),
                                                weight="bold",
                                                color="green.600"
                                            ),
                                        )
                                    )
                                ),
                                width="100%",
                                variant="surface",
                                size="2",
                            ),
                            width="100%",
                        ),
                        rx.box(),
                    ),
                    
                    # Sección: Ingresos
                    section_header("Ingresos", "circle_arrow_down"),
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("Concepto"),
                                rx.table.column_header_cell("Valor"),
                            )
                        ),
                        rx.table.body(
                            rx.foreach(
                                LiquidacionesState.detalles_ingresos,
                                lambda item: rx.table.row(
                                    rx.table.cell(item["concepto"]),
                                    rx.table.cell(format_money(item["valor"])),
                                )
                            )
                        ),
                        width="100%",
                        variant="surface"
                    ),
                    
                    # Egresos
                    section_header("Egresos", "circle_arrow_up"),
                    rx.box(
                        info_row(
                            f"Comisión ({LiquidacionesState.liquidacion_actual['comision_pct_view']}%):",
                            format_money(LiquidacionesState.liquidacion_actual["comision_monto"])
                        ),
                        info_row(
                            "IVA Comisión (19%):",
                            format_money(LiquidacionesState.liquidacion_actual["iva_comision"])
                        ),
                        info_row(
                            "4x1000:",
                            format_money(LiquidacionesState.liquidacion_actual["impuesto_4x1000"])
                        ),
                        info_row(
                            "Gastos Administración:",
                            format_money(LiquidacionesState.liquidacion_actual["gastos_admin"])
                        ),
                        info_row(
                            "Gastos Servicios:",
                            format_money(LiquidacionesState.liquidacion_actual["gastos_serv"])
                        ),
                        info_row(
                            "Gastos Reparaciones:",
                            format_money(LiquidacionesState.liquidacion_actual["gastos_rep"])
                        ),
                        info_row(
                            "Otros Egresos:",
                            format_money(LiquidacionesState.liquidacion_actual["otros_egr"])
                        ),
                        rx.divider(),
                        info_row(
                            "Total Egresos:",
                            rx.text(
                                format_money(LiquidacionesState.liquidacion_actual["total_egresos"]),
                                weight="bold",
                                size="4",
                                color="red",
                            )
                        ),
                        padding="1em",
                        background="red.50",
                        border_radius="8px",
                    ),
                    
                    # Sección: Resultado Final
                    section_header("Resultado", "dollar_sign"),
                    rx.box(
                        rx.center(
                            rx.vstack(
                                rx.text("NETO A PAGAR", size="2", color="gray.600", weight="medium"),
                                rx.text(
                                    format_money(LiquidacionesState.liquidacion_actual["neto_pagar"]),
                                    size="8",
                                    weight="bold",
                                    color="blue.600",
                                ),
                                spacing="1",
                            ),
                            padding="1.5em",
                        ),
                        background="blue.50",
                        border_radius="8px",
                        border="2px solid",
                        border_color="blue.300",
                    ),
                    
                    # Sección: Información de Pago (solo si está pagada)
                    rx.cond(
                        LiquidacionesState.liquidacion_actual["estado"] == "Pagada",
                        rx.vstack(
                            section_header("Información de Pago", "circle_check"),
                            rx.box(
                                info_row("Fecha de Pago:", LiquidacionesState.liquidacion_actual["fecha_pago"]),
                                info_row("Método:", LiquidacionesState.liquidacion_actual["metodo_pago"]),
                                info_row("Referencia:", LiquidacionesState.liquidacion_actual["referencia_pago"]),
                                padding="1em",
                                background="green.50",
                                border_radius="8px",
                            ),
                            width="100%",
                        ),
                        rx.box(),
                    ),
                    
                    # Observaciones
                    rx.cond(
                        LiquidacionesState.liquidacion_actual["observaciones"] != "Sin observaciones",
                        rx.vstack(
                            section_header("Observaciones", "message_square"),
                            rx.box(
                                rx.text(
                                    LiquidacionesState.liquidacion_actual["observaciones"],
                                    size="2",
                                ),
                                padding="1em",
                                background="gray.50",
                                border_radius="8px",
                            ),
                            width="100%",
                        ),
                        rx.box(),
                    ),
                    
                    # Botones de Acción
                    rx.hstack(
                        rx.dialog.close(
                            rx.button("Cerrar", variant="soft", color_scheme="gray"),
                        ),
                        rx.spacer(),
                        # Editar (solo En Proceso)
                        rx.cond(
                            LiquidacionesState.liquidacion_actual["estado"] == "En Proceso",
                            rx.button(
                                rx.icon("pencil"),
                                "Editar",
                                on_click=lambda: LiquidacionesState.open_edit_modal(
                                    LiquidacionesState.liquidacion_actual["id"]
                                ),
                                color_scheme="blue",
                            ),
                            rx.box(),
                        ),
                        # Aprobar (solo En Proceso)
                        rx.cond(
                            LiquidacionesState.liquidacion_actual["estado"] == "En Proceso",
                            rx.button(
                                rx.icon("circle_check"),
                                "Aprobar",
                                on_click=lambda: LiquidacionesState.aprobar_liquidacion(
                                    LiquidacionesState.liquidacion_actual["id"]
                                ),
                                color_scheme="green",
                            ),
                            rx.box(),
                        ),
                        # Registrar Pago (solo Aprobada)
                        rx.cond(
                            LiquidacionesState.liquidacion_actual["estado"] == "Aprobada",
                            rx.button(
                                rx.icon("dollar_sign"),
                                "Registrar Pago",
                                on_click=lambda: LiquidacionesState.open_payment_modal(
                                    LiquidacionesState.liquidacion_actual["id"]
                                ),
                                color_scheme="violet",
                            ),
                            rx.box(),
                        ),
                        # Reversar (solo Aprobada)
                        rx.cond(
                            LiquidacionesState.liquidacion_actual["estado"] == "Aprobada",
                            rx.button(
                                rx.icon("rotate_ccw"),
                                "Reversar",
                                on_click=lambda: LiquidacionesState.open_reverse_confirm(
                                    LiquidacionesState.liquidacion_actual["id"]
                                ),
                                color_scheme="yellow",
                            ),
                            rx.box(),
                        ),
                        # Cancelar (solo En Proceso o Aprobada)
                        rx.cond(
                            (LiquidacionesState.liquidacion_actual["estado"] == "En Proceso") | 
                            (LiquidacionesState.liquidacion_actual["estado"] == "Aprobada"),
                            rx.button(
                                rx.icon("circle_x"),
                                "Cancelar",
                                on_click=lambda: LiquidacionesState.open_cancel_modal(
                                    LiquidacionesState.liquidacion_actual["id"]
                                ),
                                color_scheme="red",
                                variant="soft",
                            ),
                            rx.box(),
                        ),
                        width="100%",
                        padding_top="1em",
                    ),
                    
                    spacing="3",
                    width="100%",
                ),
                rx.center(
                    rx.spinner(size="3"),
                    min_height="300px",
                ),
            ),
            
            max_width="700px",
            max_height="80vh",
            overflow_y="auto",
        ),
        open=LiquidacionesState.show_detail_modal,
        on_open_change=LiquidacionesState.close_modal,
    )
