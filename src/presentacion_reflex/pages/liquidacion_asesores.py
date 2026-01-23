import reflex as rx
from src.presentacion_reflex.state.liquidacion_asesores_state import LiquidacionAsesoresState
from src.presentacion_reflex.state.auth_state import AuthState
from src.presentacion_reflex.state.pdf_state import PDFState
from src.presentacion_reflex.components.layout.dashboard_layout import dashboard_layout
from src.presentacion_reflex.components.liquidacion_asesores.modal_form import modal_form
from src.presentacion_reflex.components.liquidacion_asesores.detail_modal import detail_modal
from src.presentacion_reflex.components.liquidacion_asesores.discount_modal import discount_modal
from src.presentacion_reflex.components.liquidacion_asesores.annul_modal import annul_modal



def liquidacion_asesores_content() -> rx.Component:
    """Página principal de liquidaciones de asesores."""
    return rx.box(
        # Encabezado
        # Encabezado Elite
        rx.vstack(
            rx.heading(
                "Liquidaciones de Asesores",
                size="8",
                weight="bold",
                background="linear-gradient(to right, #667eea, #764ba2)",
                background_clip="text",
                color="transparent",
            ),
            rx.text(
                "Gestión de comisiones y pagos a asesores inmobiliarios",
                size="4",
                color="gray",
                weight="medium",
            ),
            spacing="2",
            margin_bottom="2rem",
        ),
        
        # Barra de búsqueda y filtros
        rx.hstack(
            # Búsqueda
            rx.input(
                placeholder="Buscar por asesor, período...",
                value=LiquidacionAsesoresState.search_text,
                on_change=LiquidacionAsesoresState.set_search,
                on_key_down=lambda key: LiquidacionAsesoresState.handle_search_key_down(key),
                width="300px"
            ),
            rx.button(
                rx.icon("search", size=18),
                on_click=LiquidacionAsesoresState.search_liquidaciones,
                variant="soft"
            ),
            
            # Filtro por estado
            rx.select(
                LiquidacionAsesoresState.estado_options,
                value=LiquidacionAsesoresState.filter_estado,
                on_change=LiquidacionAsesoresState.set_filter_estado,
                placeholder="Estado"
            ),
            
            # Filtro por período
            rx.select(
                LiquidacionAsesoresState.periodo_options,
                value=LiquidacionAsesoresState.filter_periodo,
                on_change=LiquidacionAsesoresState.set_filter_periodo,
                placeholder="Período"
            ),
            
            # Filtro por asesor
            rx.select(
                LiquidacionAsesoresState.asesores_select_options,
                value=LiquidacionAsesoresState.filter_asesor,
                on_change=LiquidacionAsesoresState.set_filter_asesor,
                placeholder="Asesor"
            ),
            
            # Botón limpiar filtros
            rx.tooltip(
                rx.icon_button(
                    rx.icon("eraser", size=18),
                    on_click=LiquidacionAsesoresState.limpiar_filtros,
                    variant="soft",
                    color_scheme="gray",
                    size="2"
                ),
                content="Limpiar filtros"
            ),
            
            rx.spacer(),
            
            # Botón nueva liquidación
            rx.cond(
                AuthState.check_action("Liquidación Asesores", "CREAR"),
                rx.button(
                    rx.icon("plus", size=18),
                    "Nueva Liquidación",
                    on_click=LiquidacionAsesoresState.open_create_modal,
                    color_scheme="blue"
                )
            ),
            
            # Refresh
            rx.button(
                rx.icon("refresh-cw", size=18),
                on_click=LiquidacionAsesoresState.load_liquidaciones,
                variant="soft"
            ),
            
            width="100%",
            spacing="3",
            margin_bottom="1.5rem"
        ),
        
        # Mensaje de error
        rx.cond(
            LiquidacionAsesoresState.error_message != "",
            rx.callout(
                LiquidacionAsesoresState.error_message,
                icon="triangle_alert",
                color_scheme="red",
                role="alert",
                margin_bottom="1rem"
            )
        ),
        
        # Loading spinner
        rx.cond(
            LiquidacionAsesoresState.is_loading,
            rx.center(
                rx.spinner(size="3"),
                padding="2rem"
            ),
            # Tabla de liquidaciones
            rx.box(
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Período", style={"font-weight": "600"}),
                            rx.table.column_header_cell("Asesor", style={"font-weight": "600"}),
                            rx.table.column_header_cell("Canon", style={"font-weight": "600"}),
                            rx.table.column_header_cell("%", style={"font-weight": "600"}),
                            rx.table.column_header_cell("Comisión Bruta", style={"font-weight": "600"}),
                            rx.table.column_header_cell("Descuentos", style={"font-weight": "600"}),
                            rx.table.column_header_cell("Bonificaciones", style={"font-weight": "600"}),
                            rx.table.column_header_cell("Valor Neto", style={"font-weight": "600"}),
                            rx.table.column_header_cell("Estado", style={"font-weight": "600"}),
                            rx.table.column_header_cell("Acciones", width="150px", style={"font-weight": "600"})
                        )
                    ),
                    rx.table.body(
                        rx.foreach(
                            LiquidacionAsesoresState.liquidaciones,
                            lambda liq: rx.table.row(
                                rx.table.cell(liq["periodo"]),
                                rx.table.cell(liq["asesor"]),
                                rx.table.cell(f"${liq['canon_liquidado']:,}"),
                                rx.table.cell(f"{liq['porcentaje']:.1f}%"),
                                rx.table.cell(
                                    f"${liq['comision_bruta']:,}",
                                    font_weight="bold"
                                ),
                                rx.table.cell(
                                    f"${liq['total_descuentos']:,}",
                                    color="red"
                                ),
                                rx.table.cell(
                                    f"${liq['total_bonificaciones']:,}",
                                    color="blue"
                                ),
                                rx.table.cell(
                                    f"${liq['valor_neto']:,}",
                                    font_weight="bold",
                                    color="green"
                                ),
                                rx.table.cell(
                                    rx.badge(
                                        liq["estado"],
                                        color_scheme=rx.cond(
                                            liq["estado"] == "Pendiente",
                                            "yellow",
                                            rx.cond(
                                                liq["estado"] == "Aprobada",
                                                "blue",
                                                rx.cond(
                                                    liq["estado"] == "Pagada",
                                                    "green",
                                                    "red"  # Anulada
                                                )
                                            )
                                        )
                                    )
                                ),
                                rx.table.cell(
                                    rx.hstack(
                                        # PDF Cuenta de Cobro
                                        rx.tooltip(
                                            rx.icon_button(
                                                rx.icon("file-spreadsheet", size=18),
                                                on_click=lambda: PDFState.generar_liquidacion_asesor_pdf(
                                                    liq["id_liquidacion"]
                                                ),
                                                size="2",
                                                variant="ghost",
                                                color_scheme="green",
                                                loading=PDFState.generating,
                                                cursor="pointer"
                                            ),
                                            content="Generar PDF Cuenta de Cobro"
                                        ),
                                        # Ver detalles
                                        rx.tooltip(
                                            rx.icon_button(
                                                rx.icon("eye", size=18),
                                                on_click=LiquidacionAsesoresState.open_detail_modal(liq["id_liquidacion"]),
                                                size="2",
                                                variant="ghost",
                                                color_scheme="blue",
                                                cursor="pointer"
                                            ),
                                            content="Ver detalle"
                                        ),
                                        # Aprobar (solo si Pendiente)
                                        rx.cond(
                                            (liq["estado"] == "Pendiente") & AuthState.check_action("Liquidación Asesores", "APROBAR"),
                                            rx.tooltip(
                                                rx.icon_button(
                                                    rx.icon("thumbs-up", size=18),
                                                    on_click=LiquidacionAsesoresState.aprobar_liquidacion(liq["id_liquidacion"]),
                                                    size="2",
                                                    variant="ghost",
                                                    color_scheme="green",
                                                    cursor="pointer"
                                                ),
                                                content="Aprobar liquidación"
                                            )
                                        ),
                                        # Editar liquidación / Gestionar descuentos (solo si Pendiente)
                                        rx.cond(
                                            (liq["estado"] == "Pendiente") & AuthState.check_action("Liquidación Asesores", "EDITAR"),
                                            rx.tooltip(
                                                rx.icon_button(
                                                    rx.icon("pencil", size=18),
                                                    on_click=LiquidacionAsesoresState.open_edit_modal(liq["id_liquidacion"]),
                                                    size="2",
                                                    variant="ghost",
                                                    color_scheme="orange",
                                                    cursor="pointer"
                                                ),
                                                content="Editar liquidación"
                                            )
                                        ),
                                        # Marcar como pagada (solo si Aprobada)
                                        rx.cond(
                                            (liq["estado"] == "Aprobada") & AuthState.check_action("Liquidación Asesores", "PAGAR"),
                                            rx.tooltip(
                                                rx.icon_button(
                                                    rx.icon("dollar-sign", size=18),
                                                    on_click=LiquidacionAsesoresState.marcar_como_pagada(liq["id_liquidacion"]),
                                                    size="2",
                                                    variant="ghost",
                                                    color_scheme="blue",
                                                    cursor="pointer"
                                                ),
                                                content="Registrar pago"
                                            )
                                        ),
                                        # Anular (si no está Anulada/Pagada)
                                        rx.cond(
                                            (liq["estado"] != "Anulada") & (liq["estado"] != "Pagada") & AuthState.check_action("Liquidación Asesores", "ANULAR"),
                                            rx.tooltip(
                                                rx.icon_button(
                                                    rx.icon("ban", size=18),
                                                    on_click=LiquidacionAsesoresState.open_annul_modal(liq["id_liquidacion"]),
                                                    size="2",
                                                    variant="ghost",
                                                    color_scheme="red",
                                                    cursor="pointer"
                                                ),
                                                content="Anular liquidación"
                                            )
                                        ),
                                        spacing="2"
                                    )
                                )
                            )
                        )
                    ),
                    width="100%",
                    variant="surface"
                ),
                
                # Mensaje sin resultados
                rx.cond(
                    (LiquidacionAsesoresState.total_items == 0) & ~LiquidacionAsesoresState.is_loading,
                    rx.center(
                        rx.text(
                            "No se encontraron liquidaciones",
                            color="gray",
                            padding="2rem"
                        )
                    )
                ),
                
                margin_bottom="1rem"
            )
        ),
        
        # Premium Pagination
        rx.card(
            rx.hstack(
                rx.button(
                    rx.icon("chevron-left", size=16),
                    "Anterior",
                    on_click=LiquidacionAsesoresState.prev_page,
                    disabled=LiquidacionAsesoresState.current_page == 1,
                    variant="soft",
                    size="3",
                    _hover={
                        "transform": "translateX(-2px)",
                    },
                    transition="transform 0.2s ease",
                ),
                rx.vstack(
                    rx.text(
                        f"Página {LiquidacionAsesoresState.current_page}",
                        size="3",
                        weight="medium",
                    ),
                    rx.text(
                        f"Mostrando {(LiquidacionAsesoresState.current_page - 1) * LiquidacionAsesoresState.page_size + 1}-"
                        f"{rx.cond(LiquidacionAsesoresState.current_page * LiquidacionAsesoresState.page_size > LiquidacionAsesoresState.total_items, LiquidacionAsesoresState.total_items, LiquidacionAsesoresState.current_page * LiquidacionAsesoresState.page_size)} "
                        f"de {LiquidacionAsesoresState.total_items}",
                        size="1",
                        color="var(--gray-10)",
                    ),
                    spacing="0",
                    align="center",
                ),
                rx.button(
                    "Siguiente",
                    rx.icon("chevron-right", size=16),
                    on_click=LiquidacionAsesoresState.next_page,
                    disabled=LiquidacionAsesoresState.current_page * LiquidacionAsesoresState.page_size >= LiquidacionAsesoresState.total_items,
                    variant="soft",
                    size="3",
                    _hover={
                        "transform": "translateX(2px)",
                    },
                    transition="transform 0.2s ease",
                ),
                justify="center",
                width="100%",
                padding="4",
                align="center",
                spacing="4",
            ),
            width="100%",
            style={
                "background": "var(--color-panel-solid)",
            }
        ),
        
        
        # Modales
        modal_form(),
        detail_modal(),
        discount_modal(),
        annul_modal(),

        
        padding="2rem",
        width="100%",
        on_mount=LiquidacionAsesoresState.on_load
    )


def liquidacion_asesores_page() -> rx.Component:
    """Página de liquidaciones de asesores con layout."""
    return dashboard_layout(liquidacion_asesores_content())
