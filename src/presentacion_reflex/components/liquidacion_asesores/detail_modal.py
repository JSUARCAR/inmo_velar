import reflex as rx
from src.presentacion_reflex.state.liquidacion_asesores_state import LiquidacionAsesoresState

def detail_modal() -> rx.Component:
    """Modal para ver detalles de una liquidación."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Detalles de Liquidación", size="5"),
            
            rx.scroll_area(
                rx.cond(
                    LiquidacionAsesoresState.liquidacion_actual,
                    rx.flex(
                        # Info Básica
                        rx.card(
                            rx.flex(
                                rx.box(
                                    rx.text("Asesor", size="1", color="gray", weight="bold"),
                                    rx.text(LiquidacionAsesoresState.liquidacion_actual["asesor"], size="3", weight="medium"),
                                ),
                                rx.box(
                                    rx.text("Período", size="1", color="gray", weight="bold"),
                                    rx.text(LiquidacionAsesoresState.liquidacion_actual["periodo"], size="3", weight="medium"),
                                ),
                                rx.box(
                                    rx.text("Estado", size="1", color="gray", weight="bold"),
                                    rx.badge(
                                        LiquidacionAsesoresState.liquidacion_actual["estado"], 
                                        size="2",
                                        color_scheme=rx.match(
                                            LiquidacionAsesoresState.liquidacion_actual["estado"],
                                            ("Pendiente", "yellow"),
                                            ("Aprobada", "blue"),
                                            ("Pagada", "green"),
                                            ("Anulada", "red"),
                                            "gray"
                                        )
                                    ),
                                ),
                                spacing="4",
                                justify="between"
                            ),
                            width="100%",
                            variant="surface"
                        ),
                        
                        # Totales
                        rx.grid(
                            rx.card(
                                rx.text("Canon Liquidado", size="1", color="gray"),
                                rx.text(
                                    f"${LiquidacionAsesoresState.liquidacion_actual['canon_liquidado']:,}", 
                                    size="4", 
                                    weight="bold"
                                ),
                            ),
                            rx.card(
                                rx.text("Comisión Bruta", size="1", color="gray"),
                                rx.text(
                                    f"${LiquidacionAsesoresState.liquidacion_actual['comision_bruta']:,}", 
                                    size="4", 
                                    weight="bold",
                                    color="blue"
                                ),
                            ),
                            rx.card(
                                rx.text("Descuentos", size="1", color="gray"),
                                rx.text(
                                    f"${LiquidacionAsesoresState.liquidacion_actual['total_descuentos']:,}", 
                                    size="4", 
                                    weight="bold",
                                    color="red"
                                ),
                            ),
                            rx.card(
                                rx.text("Bonificaciones", size="1", color="gray"),
                                rx.text(
                                    f"${LiquidacionAsesoresState.liquidacion_actual['total_bonificaciones']:,}", 
                                    size="4", 
                                    weight="bold",
                                    color="green"
                                ),
                            ),
                            rx.card(
                                rx.text("Valor Neto", size="1", color="gray"),
                                rx.text(
                                    f"${LiquidacionAsesoresState.liquidacion_actual['valor_neto']:,}", 
                                    size="5", 
                                    weight="bold",
                                    color="green"
                                ),
                                variant="classic"
                            ),
                            columns="3",
                            spacing="3",
                            width="100%"
                        ),

                        # Properties Section
                        rx.box(
                            rx.heading("Propiedades a Liquidar", size="3", margin_bottom="2"),
                            rx.cond(
                                LiquidacionAsesoresState.advisor_properties.length() > 0,
                                rx.grid(
                                    rx.foreach(
                                        LiquidacionAsesoresState.advisor_properties,
                                        lambda p: rx.card(
                                            rx.flex(
                                                rx.box(
                                                     rx.text("Propiedad", size="1", color="gray", weight="bold"),
                                                     rx.text(p["DIRECCION_PROPIEDAD"], size="2", weight="medium"),
                                                ),
                                                rx.box(
                                                     rx.text("Canon", size="1", color="gray", weight="bold"),
                                                     rx.text(f"${p['CANON_ARRENDAMIENTO']}", size="2", weight="medium", color="blue"),
                                                ),
                                                justify="between",
                                                align="center"
                                            ),
                                            size="2"
                                        )
                                    ),
                                    columns="2",
                                    spacing="2",
                                    width="100%"
                                ),
                                rx.text("No hay propiedades asociadas", color="gray", style={"font_style": "italic"})
                            ),
                            margin_top="4",
                            width="100%"
                        ),

                        rx.separator(size="4", margin_y="4"),
                        
                        # Descuentos y Bonificaciones
                        rx.box(
                            rx.heading("Descuentos  y Bonificaciones", size="3", margin_bottom="2"),
                            rx.cond(
                                (LiquidacionAsesoresState.descuentos_actuales.length() + LiquidacionAsesoresState.bonificaciones_actuales.length()) > 0,
                                rx.table.root(
                                    rx.table.header(
                                        rx.table.row(
                                            rx.table.column_header_cell("Categoría"),
                                            rx.table.column_header_cell("Tipo"),
                                            rx.table.column_header_cell("Descripción"),
                                            rx.table.column_header_cell("Valor"),
                                            rx.table.column_header_cell("Acciones")
                                        )
                                    ),
                                    rx.table.body(
                                        # Descuentos
                                        rx.foreach(
                                            LiquidacionAsesoresState.descuentos_actuales,
                                            lambda d: rx.table.row(
                                                rx.table.cell(rx.badge("Descuento", color_scheme="red", size="1")),
                                                rx.table.cell(d["tipo"]),
                                                rx.table.cell(d["descripcion"]),
                                                rx.table.cell(f"${d['valor']:,}", color="red"),
                                                rx.table.cell(
                                                    rx.cond(
                                                        LiquidacionAsesoresState.liquidacion_actual["estado"] == "Pendiente",
                                                         rx.icon_button(
                                                             rx.icon("trash-2", size=16),
                                                             on_click=lambda _, id_desc=d["id_descuento"]: LiquidacionAsesoresState.eliminar_descuento(id_desc),
                                                             size="1",
                                                             variant="ghost",
                                                             color_scheme="red"
                                                         ),
                                                        rx.box()
                                                    )
                                                )
                                            )
                                        ),
                                        # Bonificaciones
                                        rx.foreach(
                                            LiquidacionAsesoresState.bonificaciones_actuales,
                                            lambda b: rx.table.row(
                                                rx.table.cell(rx.badge("Bonificación", color_scheme="green", size="1")),
                                                rx.table.cell(b["tipo"]),
                                                rx.table.cell(b["descripcion"]),
                                                rx.table.cell(f"${b['valor']:,}", color="green"),
                                                rx.table.cell(rx.box())  # Sin acciones por ahora
                                            )
                                        )
                                    ),
                                    variant="surface",
                                    width="100%"
                                ),
                                rx.text("No hay descuentos ni bonificaciones aplicados.", color="gray", size="2")
                            ),
                            width="100%"
                        ),
                        
                        direction="column",
                        spacing="4",
                        padding="1"
                    ),
                    rx.center(rx.spinner())
                ),
                max_height="600px",
            ),
            
            rx.flex(
                rx.dialog.close(
                    rx.button("Cerrar", variant="soft", color_scheme="gray")
                ),
                justify="end",
                margin_top="4"
            ),
        ),
        open=LiquidacionAsesoresState.show_detail_modal,
        on_open_change=LiquidacionAsesoresState.set_show_detail_modal,
    )
