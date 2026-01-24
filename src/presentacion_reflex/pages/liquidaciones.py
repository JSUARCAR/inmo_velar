"""
Página de Liquidaciones de Propietarios
Gestión completa de estados de cuenta mensuales
"""

import reflex as rx
from src.presentacion_reflex.state.liquidaciones_state import LiquidacionesState
from src.presentacion_reflex.state.auth_state import AuthState
from src.presentacion_reflex.state.pdf_state import PDFState
from src.presentacion_reflex.components.layout.dashboard_layout import dashboard_layout
from src.presentacion_reflex.components.liquidaciones import (
    liquidacion_detail_modal,
    liquidacion_create_form,
    liquidacion_edit_form,
    payment_form,
    bulk_liquidacion_form,
    cancel_modal,
    reverse_confirm_dialog,
)


def format_currency(amount: rx.Var) -> rx.Component:
    """Formatea valores monetarios."""
    # En Reflex usamos rx.cond para formatear condicionalmente
    return rx.text(f"${amount:,}".replace(",", "."))


def render_estado_badge(estado: rx.Var) -> rx.Component:
    """Renderiza badge con color según estado."""
    return rx.match(
        estado,
        ("En Proceso", rx.badge("En Proceso", color_scheme="yellow", variant="solid")),
        ("Aprobada", rx.badge("Aprobada", color_scheme="blue", variant="solid")),
        ("Pagada", rx.badge("Pagada", color_scheme="green", variant="solid")),
        ("Cancelada", rx.badge("Cancelada", color_scheme="red", variant="solid")),
        rx.badge(estado, color_scheme="gray", variant="soft"),  # fallback
    )


def liquidaciones_toolbar() -> rx.Component:
    """Barra de herramientas con filtros y búsqueda."""
    return rx.hstack(
        # Toggle Vista Agrupada
        rx.hstack(
            rx.switch(
                checked=LiquidacionesState.vista_agrupada,
                on_change=LiquidacionesState.toggle_vista_agrupada,
                color_scheme="blue",
            ),
            rx.text(
                rx.cond(
                    LiquidacionesState.vista_agrupada,
                    "Vista Por Propietario",
                    "Vista Individual"
                ),
                weight="medium",
                size="2"
            ),
            spacing="2",
            padding="0.5em",
            background="#f0f9ff",
            border_radius="6px",
        ),
        
        # Búsqueda
        rx.input(
            placeholder="Buscar...",
            value=LiquidacionesState.search_text,
            on_change=LiquidacionesState.set_search,
            on_key_down=lambda key: LiquidacionesState.handle_search_key_down(key),
            width="250px",
        ),
        
        # Filtro Período
        rx.select(
            LiquidacionesState.periodos_select_options,
            placeholder="Período",
            value=LiquidacionesState.filter_periodo,
            on_change=LiquidacionesState.set_filter_periodo,
            width="130px",
        ),
        
        # Filtro Estado
        rx.select(
            LiquidacionesState.estado_options,
            placeholder="Estado",
            value=LiquidacionesState.filter_estado,
            on_change=LiquidacionesState.set_filter_estado,
            width="130px",
        ),
        
        rx.spacer(),
        
        # Botón Nueva Liquidación Individual o Masiva
        rx.cond(
            LiquidacionesState.vista_agrupada,
            rx.cond(
                AuthState.check_action("Liquidaciones", "CREAR"),
                rx.button(
                    rx.icon("users"),
                    "Nueva Liquidación Masiva",
                    on_click=LiquidacionesState.open_bulk_create_modal,
                    color_scheme="violet",
                )
            ),
            rx.cond(
                AuthState.check_action("Liquidaciones", "CREAR"),
                rx.button(
                    rx.icon("plus"),
                    "Nueva Liquidación",
                    on_click=LiquidacionesState.open_create_modal,
                    color_scheme="blue",
                )
            ),
        ),
        
        # Botón Refresh
        rx.button(
            rx.icon("refresh-cw"),
            on_click=LiquidacionesState.load_liquidaciones,
            variant="soft",
        ),
        
        width="100%",
        padding="1em",
        background="white",
        border_radius="8px",
        box_shadow="sm",
        spacing="3",
    )


def liquidaciones_table() -> rx.Component:
    """Tabla de liquidaciones."""
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("ID", style={"font-weight": "600"}),
                rx.table.column_header_cell("Período", style={"font-weight": "600"}),
                rx.table.column_header_cell("Propiedad", style={"font-weight": "600"}),
                rx.table.column_header_cell("Canon", style={"font-weight": "600"}),
                rx.table.column_header_cell("Neto a Pagar", style={"font-weight": "600"}),
                rx.table.column_header_cell("Estado", style={"font-weight": "600"}),
                rx.table.column_header_cell("Acciones", width="200px", style={"font-weight": "600"}),
            ),
        ),
        rx.table.body(
            rx.foreach(
                LiquidacionesState.liquidaciones,
                lambda liq: rx.table.row(
                    rx.table.cell(liq["id"]),
                    rx.table.cell(liq["periodo"]),
                    rx.table.cell(liq["contrato"]),
                    rx.table.cell(f"${liq['canon']:,}"),
                    rx.table.cell(
                        rx.text(
                            f"${liq['neto']:,}",
                            weight="bold",
                            color="green",
                        )
                    ),
                    rx.table.cell(render_estado_badge(liq["estado"])),
                    rx.table.cell(
                        rx.hstack(
                            # Ver Detalle
                            rx.tooltip(
                                rx.icon_button(
                                    rx.icon("eye", size=18),
                                    on_click=lambda: LiquidacionesState.open_detail_modal(liq["id"]),
                                    size="2",
                                    variant="ghost",
                                ),
                                content="Ver detalle"
                            ),
                            
                            # Botón PDF Estado de Cuenta
                            rx.tooltip(
                                rx.icon_button(
                                    rx.icon("file-spreadsheet", size=18),
                                    on_click=lambda: PDFState.generar_estado_cuenta_elite(
                                        liquidacion_id=liq["id"]
                                    ),
                                    size="2",
                                    variant="ghost",
                                    color_scheme="green",
                                    loading=PDFState.generating,
                                ),
                                content="Estado de Cuenta PDF"
                            ),
                            # Editar (solo En Proceso)
                            rx.cond(
                                (liq["estado"] == "En Proceso") & AuthState.check_action("Liquidaciones", "EDITAR"),
                                rx.tooltip(
                                    rx.icon_button(
                                        rx.icon("pencil", size=18),
                                        on_click=lambda: LiquidacionesState.open_edit_modal(liq["id"]),
                                        size="2",
                                        variant="ghost",
                                        color_scheme="blue",
                                    ),
                                    content="Editar liquidación"
                                ),
                                rx.box(),  # Empty si no aplica
                            ),
                            # Aprobar (solo En Proceso)
                            rx.cond(
                                (liq["estado"] == "En Proceso") & AuthState.check_action("Liquidaciones", "APROBAR"),
                                rx.tooltip(
                                    rx.icon_button(
                                        rx.icon("thumbs-up", size=18),
                                        on_click=lambda: LiquidacionesState.aprobar_liquidacion(liq["id"]),
                                        size="2",
                                        variant="ghost",
                                        color_scheme="green",
                                    ),
                                    content="Aprobar liquidación"
                                ),
                                rx.box(),
                            ),
                            # Marcar Pago (solo Aprobada)
                            rx.cond(
                                (liq["estado"] == "Aprobada") & AuthState.check_action("Liquidaciones", "PAGAR"),
                                rx.tooltip(
                                    rx.icon_button(
                                        rx.icon("dollar-sign", size=18),
                                        on_click=lambda: LiquidacionesState.open_payment_modal(liq["id"]),
                                        size="2",
                                        variant="ghost",
                                        color_scheme="violet",
                                    ),
                                    content="Registrar pago"
                                ),
                                rx.box(),
                            ),
                            spacing="2",
                        )
                    ),
                ),
            ),
        ),
        width="100%",
        variant="surface",
    )


def liquidaciones_table_agrupada() -> rx.Component:
    """Tabla de liquidaciones agrupadas por propietario."""
    return rx.box(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("Período", style={"font-weight": "600"}),
                    rx.table.column_header_cell("Propietario", style={"font-weight": "600"}),
                    rx.table.column_header_cell("Propiedades", text_align="center", style={"font-weight": "600"}),
                    rx.table.column_header_cell("Canon Total", style={"font-weight": "600"}),
                    rx.table.column_header_cell("Neto Total", text_align="right", style={"font-weight": "600"}),
                    rx.table.column_header_cell("Estado", text_align="center", style={"font-weight": "600"}),
                    rx.table.column_header_cell("Acciones", width="200px", style={"font-weight": "600"}),
                ),
            ),
            rx.table.body(
                rx.foreach(
                    LiquidacionesState.liquidaciones,
                    lambda liq: rx.table.row(
                        rx.table.cell(liq["periodo"]),
                        rx.table.cell(
                            rx.vstack(
                                rx.text(liq["propietario"], weight="medium"),
                                rx.text(liq["documento"], size="1", color="gray"),
                                spacing="0",
                                align="start"
                            )
                        ),
                        rx.table.cell(
                            rx.badge(liq["cantidad_propiedades"], color_scheme="blue"),
                            text_align="center"
                        ),
                        rx.table.cell(f"${liq['canon']:,}"),
                        rx.table.cell(
                            rx.text(
                                f"${liq['neto']:,}",
                                weight="bold",
                                color="green",
                            ),
                            text_align="right"
                        ),
                        rx.table.cell(
                            render_estado_badge(liq["estado"]),
                            text_align="center"
                        ),
                        rx.table.cell(
                            rx.hstack(
                                # Ver Detalle Consolidado
                                rx.tooltip(
                                    rx.icon_button(
                                        rx.icon("eye", size=18),
                                        on_click=lambda: LiquidacionesState.open_detail_consolidated(
                                            liq["id_propietario"],
                                            liq["periodo"]
                                        ),
                                        size="2",
                                        variant="ghost",
                                    ),
                                    content="Ver detalle consolidado"
                                ),
                                
                                # Botón PDF Estado de Cuenta (Vista Agrupada)
                                # Note: En vista agrupada, necesitaríamos buscar la primera liquidación
                                # Por ahora usamos el método legacy por propietario/período
                                rx.tooltip(
                                    rx.icon_button(
                                        rx.icon("file-spreadsheet", size=18),
                                        on_click=lambda: PDFState.generar_estado_cuenta_elite(
                                            propietario_id=liq["id_propietario"],
                                            periodo=liq["periodo"]
                                        ),
                                        size="2",
                                        variant="ghost",
                                        color_scheme="green",
                                        loading=PDFState.generating,
                                    ),
                                    content="Estado de Cuenta PDF"
                                ),
                                # Aprobar Todas (solo En Proceso)
                                rx.cond(
                                    (liq["estado"] == "En Proceso") & AuthState.check_action("Liquidaciones", "APROBAR"),
                                    rx.tooltip(
                                        rx.icon_button(
                                            rx.icon("thumbs-up", size=18),
                                            on_click=lambda: LiquidacionesState.aprobar_liquidacion_masiva(
                                                liq["id_propietario"],
                                                liq["periodo"]
                                            ),
                                            size="2",
                                            variant="ghost",
                                            color_scheme="green",
                                        ),
                                        content="Aprobar todas las liquidaciones"
                                    ),
                                    rx.box(),
                                ),
                                # Marcar Pago Masivo (solo Aprobada)
                                rx.cond(
                                    (liq["estado"] == "Aprobada") & AuthState.check_action("Liquidaciones", "PAGAR"),
                                    rx.tooltip(
                                        rx.icon_button(
                                            rx.icon("dollar-sign", size=18),
                                            on_click=lambda: LiquidacionesState.open_payment_modal_bulk(liq["id_propietario"], liq["periodo"]),
                                            size="2",
                                            variant="ghost",
                                            color_scheme="violet",
                                        ),
                                        content="Registrar pago masivo"
                                    ),
                                    rx.box(),
                                ),
                                spacing="2",
                            )
                        ),
                    ),
                ),
            ),
            width="100%",
            variant="surface",
        ),
        width="100%",
        overflow_x="auto",
    )


def pagination_controls() -> rx.Component:
    """Controles de paginación Premium."""
    return rx.card(
        rx.hstack(
            rx.button(
                rx.icon("chevron-left", size=16),
                "Anterior",
                on_click=LiquidacionesState.prev_page,
                disabled=LiquidacionesState.current_page == 1,
                variant="soft",
                size="3",
                _hover={
                    "transform": "translateX(-2px)",
                },
                transition="transform 0.2s ease",
            ),
            rx.vstack(
                rx.text(
                    f"Página {LiquidacionesState.current_page}",
                    size="3",
                    weight="medium",
                ),
                rx.text(
                    f"Mostrando {(LiquidacionesState.current_page - 1) * LiquidacionesState.page_size + 1}-"
                    f"{rx.cond(LiquidacionesState.current_page * LiquidacionesState.page_size > LiquidacionesState.total_items, LiquidacionesState.total_items, LiquidacionesState.current_page * LiquidacionesState.page_size)} "
                    f"de {LiquidacionesState.total_items}",
                    size="1",
                    color="var(--gray-10)",
                ),
                spacing="0",
                align="center",
            ),
            rx.button(
                "Siguiente",
                rx.icon("chevron-right", size=16),
                on_click=LiquidacionesState.next_page,
                disabled=LiquidacionesState.current_page * LiquidacionesState.page_size >= LiquidacionesState.total_items,
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
    )


def liquidaciones_page() -> rx.Component:
    """Página principal de liquidaciones."""
    return rx.vstack(
        # Header
        rx.vstack(
            rx.heading(
                "Liquidaciones de Propietarios",
                size="8",
                weight="bold",
                background="linear-gradient(to right, #667eea, #764ba2)",
                background_clip="text",
                color="transparent",
            ),
            rx.text(
                "Gestión de estados de cuenta mensuales y pagos a propietarios",
                size="4",
                color="gray",
                weight="medium",
            ),
            spacing="2",
            margin_bottom="2rem",
        ),
        
        # Toolbar
        liquidaciones_toolbar(),
        
        # Error message (si existe)
        rx.cond(
            LiquidacionesState.error_message != "",
            rx.callout(
                LiquidacionesState.error_message,
                icon="circle-alert",
                color_scheme="red",
                role="alert",
            ),
            rx.box(),
        ),
        
        # Loading o Tabla
        rx.cond(
            LiquidacionesState.is_loading,
            rx.center(
                rx.spinner(size="3"),
                min_height="400px",
            ),
            rx.vstack(
                # Tabla condicional: Individual o Agrupada
                rx.cond(
                    LiquidacionesState.vista_agrupada,
                    liquidaciones_table_agrupada(),
                    liquidaciones_table(),
                ),
                pagination_controls(),
                width="100%",
                spacing="4",
            ),
        ),
        
        # Modales
        liquidacion_detail_modal(),
        liquidacion_create_form(),
        liquidacion_edit_form(),
        payment_form(),
        # Modal para liquidaciones masivas
        rx.cond(
            LiquidacionesState.show_bulk_create_modal,
            bulk_liquidacion_form(
                form_data=LiquidacionesState.form_data,
                propietarios_options=LiquidacionesState.propietarios_select_options,
                on_submit=LiquidacionesState.generar_liquidacion_masiva,
                on_cancel=LiquidacionesState.close_modal,
                is_loading=LiquidacionesState.is_loading
            ),
            rx.box()
        ),
        
        # Cancel Modal
        cancel_modal(),
        
        # Reverse Confirm Dialog  
        reverse_confirm_dialog(),
        
        width="100%",
        spacing="4",
        padding="2em",
    )


@rx.page(route="/liquidaciones", title="Liquidaciones", on_load=LiquidacionesState.on_load)
def liquidaciones() -> rx.Component:
    """Página de liquidaciones con layout."""
    return rx.fragment(
        rx.toast.provider(),
        dashboard_layout(liquidaciones_page())
    )
