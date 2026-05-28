"""
Página de Liquidaciones de Propietarios
Gestión completa de estados de cuenta mensuales
"""

import reflex as rx

from src.presentacion_reflex.components.layout.dashboard_layout import dashboard_layout
from src.presentacion_reflex.components.contratos.badge_grupo_pago import badge_grupo_pago
from src.presentacion_reflex.components.liquidaciones import (
    bulk_liquidacion_form,
    cancel_modal,
    liquidacion_create_form,
    liquidacion_detail_modal,
    liquidacion_edit_form,
    payment_form,
    reverse_confirm_dialog,
    modal_exportar_liquidaciones_periodo,
)
from src.presentacion_reflex.state.auth_state import AuthState
from src.presentacion_reflex.state.liquidaciones_state import LiquidacionesState
from src.presentacion_reflex.state.pdf_state import PDFState
from src.presentacion_reflex.components.neuro_elements import (
    neuro_input,
    neuro_button,
    neuro_select_root,
)
from src.presentacion_reflex import styles


def format_currency(amount: rx.Var) -> rx.Component:
    """Formatea valores monetarios."""
    return rx.text("$", amount)


def render_estado_badge(estado: rx.Var) -> rx.Component:
    """Renderiza badge con color según estado."""
    return rx.match(
        estado,
        ("En Proceso", rx.badge("En Proceso", color_scheme="yellow", variant="solid")),
        ("Aprobada", rx.badge("Aprobada", color_scheme="blue", variant="solid")),
        ("Pagada", rx.badge("Pagada", color_scheme="green", variant="solid")),
        ("Cancelada", rx.badge("Cancelada", color_scheme="red", variant="solid")),
        rx.badge(estado, color_scheme="gray", variant="soft"),
    )


def render_estado_recaudo_badge(estado_recaudo: rx.Var) -> rx.Component:
    """Renderiza badge con color según estado del recaudo."""
    return rx.match(
        estado_recaudo,
        ("Aplicado", rx.badge("Aplicado", color_scheme="green", variant="soft")),
        ("Pendiente", rx.badge("Pendiente", color_scheme="yellow", variant="soft")),
        ("Vencido", rx.badge("Vencido", color_scheme="orange", variant="soft")),
        ("Reversado", rx.badge("Reversado", color_scheme="red", variant="soft")),
        rx.badge("Sin Recaudo", color_scheme="gray", variant="soft"),
    )


def liquidaciones_toolbar() -> rx.Component:
    """Barra de herramientas con filtros y búsqueda con diseño neumórfico."""
    return rx.flex(
        # Botón Exportar Lote Periodo ZIP
        rx.cond(
            AuthState.check_action("Liquidaciones", "CREAR"),
            rx.tooltip(
                neuro_button(
                    rx.icon("file-archive", size=20),
                    on_click=LiquidacionesState.open_export_modal,
                    loading=LiquidacionesState.exportando_periodo,
                ),
                content="Exportar Periodo (ZIP)",
            ),
        ),
        # Toggle Vista Agrupada
        rx.flex(
            rx.switch(
                checked=LiquidacionesState.vista_agrupada,
                on_change=LiquidacionesState.toggle_vista_agrupada,
                color_scheme="blue",
            ),
            rx.text(
                rx.cond(
                    LiquidacionesState.vista_agrupada,
                    "Vista Por Propietario",
                    "Vista Individual",
                ),
                weight="medium",
                size="2",
                color=styles.TEXT_PRIMARY,
            ),
            gap="2",
            align="center",
            padding="0.5em",
            background=styles.BG_PANEL,
            border_radius="10px",
            style={"box_shadow": styles.NEU_INSET},
            flex_shrink="0",
        ),
        # Búsqueda
        neuro_input(
            placeholder="Buscar...",
            value=LiquidacionesState.search_text,
            on_change=LiquidacionesState.set_search,
            on_key_down=lambda key: LiquidacionesState.handle_search_key_down(key),
            width=["100%", "100%", "250px"],
        ),
        # Filtro Período
        neuro_select_root(
            rx.foreach(
                LiquidacionesState.periodos_select_options,
                lambda opt: rx.select.item(opt, value=opt),
            ),
            placeholder="Período",
            value=LiquidacionesState.filter_periodo,
            on_change=LiquidacionesState.set_filter_periodo,
            width=["100%", "100%", "150px"],
        ),
        # Filtro Estado
        neuro_select_root(
            rx.foreach(
                LiquidacionesState.estado_options,
                lambda opt: rx.select.item(opt, value=opt),
            ),
            placeholder="Estado",
            value=LiquidacionesState.filter_estado,
            on_change=LiquidacionesState.set_filter_estado,
            width=["100%", "100%", "150px"],
        ),
        # Filtro Asesor
        neuro_select_root(
            rx.foreach(
                LiquidacionesState.asesores_select_options,
                lambda opt: rx.select.item(opt, value=opt),
            ),
            placeholder="Asesor",
            value=LiquidacionesState.filter_asesor_id,
            on_change=LiquidacionesState.set_filter_asesor,
            width=["100%", "100%", "200px"],
        ),
        # Grupo de acciones (sin rx.spacer)
        rx.flex(
            # Botón Nueva Liquidación Individual o Masiva
            rx.cond(
                LiquidacionesState.vista_agrupada,
                rx.cond(
                    AuthState.check_action("Liquidaciones", "CREAR"),
                    neuro_button(
                        rx.hstack(rx.icon("users"), rx.text("Liquidación Masiva")),
                        on_click=LiquidacionesState.open_bulk_create_modal,
                        width=rx.breakpoints(initial="100%", md="auto"),
                    ),
                ),
                rx.cond(
                    AuthState.check_action("Liquidaciones", "CREAR"),
                    neuro_button(
                        rx.hstack(rx.icon("plus"), rx.text("Nueva Liquidación")),
                        on_click=LiquidacionesState.open_create_modal,
                        width=rx.breakpoints(initial="100%", md="auto"),
                    ),
                ),
            ),
            # Botón Refresh
            neuro_button(
                rx.icon("refresh-cw"),
                on_click=LiquidacionesState.load_liquidaciones,
            ),
            gap="3",
            align="center",
            flex_wrap="wrap",
            justify=rx.breakpoints(initial="start", md="end"),
            width=rx.breakpoints(initial="100%", md="auto"),
        ),
        width="100%",
        padding="1em",
        background=styles.BG_PANEL,
        border_radius="16px",
        style={"box_shadow": styles.NEU_SHADOW},
        gap="3",
        flex_direction=rx.breakpoints(initial="column", md="row"),
        flex_wrap="wrap",
        align=rx.breakpoints(initial="stretch", md="center"),
    )


def pagination_controls() -> rx.Component:
    """Controles de paginación Premium."""
    return rx.card(
        rx.hstack(
            neuro_button(
                rx.icon("chevron-left", size=16),
                rx.text("Anterior", display=rx.breakpoints(initial="none", md="block")),
                on_click=LiquidacionesState.prev_page,
                disabled=LiquidacionesState.current_page == 1,
                size="3",
            ),
            rx.vstack(
                rx.text(
                    "Página ",
                    LiquidacionesState.current_page,
                    size=rx.breakpoints(initial="2", md="3"),
                    weight="medium",
                    color=styles.TEXT_PRIMARY,
                ),
                rx.text(
                    "Mostrando ",
                    (LiquidacionesState.current_page - 1) * LiquidacionesState.page_size
                    + 1,
                    "-",
                    rx.cond(
                        LiquidacionesState.current_page * LiquidacionesState.page_size
                        > LiquidacionesState.total_items,
                        LiquidacionesState.total_items,
                        LiquidacionesState.current_page * LiquidacionesState.page_size,
                    ),
                    " de ",
                    LiquidacionesState.total_items,
                    size="1",
                    color=styles.TEXT_SECONDARY,
                    display=rx.breakpoints(initial="none", md="block"),
                ),
                spacing="0",
                align="center",
            ),
            neuro_button(
                rx.text(
                    "Siguiente", display=rx.breakpoints(initial="none", md="block")
                ),
                rx.icon("chevron-right", size=16),
                on_click=LiquidacionesState.next_page,
                disabled=LiquidacionesState.current_page * LiquidacionesState.page_size
                >= LiquidacionesState.total_items,
                size="3",
            ),
            justify="center",
            width="100%",
            padding="4",
            align="center",
            spacing="4",
        ),
        width="100%",
        style={
            "background": styles.BG_PANEL,
            "box_shadow": styles.NEU_SHADOW,
            "border": "none",
            "border_radius": "16px",
            "margin_top": "24px",
        },
    )


def header_cell_sortable(label: str, column_id: str) -> rx.Component:
    """Renderiza celda de encabezado con capacidad de ordenamiento."""
    is_active = LiquidacionesState.sort_by == column_id

    return rx.table.column_header_cell(
        rx.hstack(
            rx.text(label, weight="bold"),
            rx.cond(
                is_active,
                rx.cond(
                    LiquidacionesState.sort_order == "desc",
                    rx.icon("chevron-down", size=16),
                    rx.icon("chevron-up", size=16),
                ),
                rx.icon("chevrons-up-down", size=14, opacity=0.3),
            ),
            spacing="2",
            align="center",
            cursor="pointer",
            on_click=lambda: LiquidacionesState.toggle_sort(column_id),
            _hover={"opacity": 0.8},
        ),
        style={"font-weight": "600"},
    )


def liquidaciones_table() -> rx.Component:
    """Tabla de liquidaciones."""
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                header_cell_sortable("ID", "id"),
                header_cell_sortable("Período", "periodo"),
                header_cell_sortable("Propiedad", "contrato"),
                rx.table.column_header_cell("Ciclo Operativo", style={"font-weight": "600"}),
                header_cell_sortable("Canon", "canon"),
                header_cell_sortable("Neto a Pagar", "neto"),
                header_cell_sortable("Estado Recaudo", "estado_recaudo"),
                header_cell_sortable("Estado", "estado"),
                rx.table.column_header_cell(
                    "Acciones", width="200px", style={"font-weight": "600"}
                ),
            ),
        ),
        rx.table.body(
            rx.foreach(
                LiquidacionesState.liquidaciones,
                lambda liq: rx.table.row(
                    rx.table.cell(liq["id"]),
                    rx.table.cell(liq["periodo"]),
                    rx.table.cell(liq["contrato"]),
                    rx.table.cell(badge_grupo_pago(liq["grupo_operativo"])),
                    rx.table.cell(liq["canon_view"]),
                    rx.table.cell(
                        rx.text(
                            liq["neto_view"],
                            weight="bold",
                            color="green",
                        )
                    ),
                    rx.table.cell(render_estado_recaudo_badge(liq["estado_recaudo"])),
                    rx.table.cell(render_estado_badge(liq["estado"])),
                    rx.table.cell(
                        rx.hstack(
                            # Ver Detalle
                            rx.tooltip(
                                rx.icon_button(
                                    rx.icon("eye", size=18),
                                    on_click=lambda: (
                                        LiquidacionesState.open_detail_modal(liq["id"])
                                    ),
                                    size="2",
                                    variant="ghost",
                                ),
                                content="Ver detalle",
                            ),
                            # Botón PDF Estado de Cuenta
                            rx.tooltip(
                                rx.icon_button(
                                    rx.icon("file-spreadsheet", size=18),
                                    on_click=lambda: (
                                        PDFState.generar_estado_cuenta_elite(
                                            liquidacion_id=liq["id"]
                                        )
                                    ),
                                    size="2",
                                    variant="ghost",
                                    color_scheme="green",
                                    loading=PDFState.generating,
                                ),
                                content="Estado de Cuenta PDF",
                            ),
                            # Editar (solo En Proceso)
                            rx.cond(
                                (liq["estado"] == "En Proceso")
                                & AuthState.check_action("Liquidaciones", "EDITAR"),
                                rx.tooltip(
                                    rx.icon_button(
                                        rx.icon("pencil", size=18),
                                        on_click=lambda: (
                                            LiquidacionesState.open_edit_modal(
                                                liq["id"]
                                            )
                                        ),
                                        size="2",
                                        variant="ghost",
                                        color_scheme="blue",
                                    ),
                                    content="Editar liquidación",
                                ),
                                rx.box(),
                            ),
                            # Aprobar (solo En Proceso)
                            rx.cond(
                                (liq["estado"] == "En Proceso")
                                & AuthState.check_action("Liquidaciones", "APROBAR"),
                                rx.tooltip(
                                    rx.icon_button(
                                        rx.icon("thumbs-up", size=18),
                                        on_click=lambda: (
                                            LiquidacionesState.aprobar_liquidacion(
                                                liq["id"]
                                            )
                                        ),
                                        size="2",
                                        variant="ghost",
                                        color_scheme="green",
                                    ),
                                    content="Aprobar liquidación",
                                ),
                                rx.box(),
                            ),
                            # Marcar Pago (solo Aprobada)
                            rx.cond(
                                (liq["estado"] == "Aprobada")
                                & AuthState.check_action("Liquidaciones", "PAGAR"),
                                rx.tooltip(
                                    rx.icon_button(
                                        rx.icon("dollar-sign", size=18),
                                        on_click=lambda: (
                                            LiquidacionesState.open_payment_modal(
                                                liq["id"]
                                            )
                                        ),
                                        size="2",
                                        variant="ghost",
                                        color_scheme="violet",
                                    ),
                                    content="Registrar pago",
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
                    header_cell_sortable("Período", "periodo"),
                    header_cell_sortable("Propietario", "propietario"),
                    header_cell_sortable("Propiedades", "cantidad_propiedades"),
                    header_cell_sortable("Canon Total", "canon"),
                    header_cell_sortable("Neto Total", "neto"),
                    rx.table.column_header_cell(
                        "Estado Recaudo", style={"font-weight": "600"}
                    ),
                    header_cell_sortable("Estado", "estado"),
                    rx.table.column_header_cell(
                        "Acciones", width="200px", style={"font-weight": "600"}
                    ),
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
                                align="start",
                            )
                        ),
                        rx.table.cell(
                            rx.badge(liq["cantidad_propiedades"], color_scheme="blue"),
                            text_align="center",
                        ),
                        rx.table.cell(liq["canon_view"]),
                        rx.table.cell(
                            rx.text(
                                liq["neto_view"],
                                weight="bold",
                                color="green",
                            ),
                            text_align="right",
                        ),
                        rx.table.cell(
                            render_estado_recaudo_badge(liq["estado_recaudo"]),
                            text_align="center",
                        ),
                        rx.table.cell(
                            render_estado_badge(liq["estado"]), text_align="center"
                        ),
                        rx.table.cell(
                            rx.hstack(
                                # Ver Detalle Consolidado
                                rx.tooltip(
                                    rx.icon_button(
                                        rx.icon("eye", size=18),
                                        on_click=lambda: (
                                            LiquidacionesState.open_detail_consolidated(
                                                liq["id_propietario"], liq["periodo"]
                                            )
                                        ),
                                        size="2",
                                        variant="ghost",
                                    ),
                                    content="Ver detalle consolidado",
                                ),
                                # Botón PDF Estado de Cuenta (Vista Agrupada)
                                rx.tooltip(
                                    rx.icon_button(
                                        rx.icon("file-spreadsheet", size=18),
                                        on_click=lambda: (
                                            PDFState.generar_estado_cuenta_elite(
                                                propietario_id=liq["id_propietario"],
                                                periodo=liq["periodo"],
                                            )
                                        ),
                                        size="2",
                                        variant="ghost",
                                        color_scheme="green",
                                        loading=PDFState.generating,
                                    ),
                                    content="Estado de Cuenta PDF",
                                ),
                                # Aprobar Todas (solo En Proceso)
                                rx.cond(
                                    (liq["estado"] == "En Proceso")
                                    & AuthState.check_action(
                                        "Liquidaciones", "APROBAR"
                                    ),
                                    rx.tooltip(
                                        rx.icon_button(
                                            rx.icon("thumbs-up", size=18),
                                            on_click=lambda: (
                                                LiquidacionesState.aprobar_liquidacion_masiva(
                                                    liq["id_propietario"],
                                                    liq["periodo"],
                                                )
                                            ),
                                            size="2",
                                            variant="ghost",
                                            color_scheme="green",
                                        ),
                                        content="Aprobar todas las liquidaciones",
                                    ),
                                    rx.box(),
                                ),
                                # Marcar Pago Masivo (solo Aprobada)
                                rx.cond(
                                    (liq["estado"] == "Aprobada")
                                    & AuthState.check_action("Liquidaciones", "PAGAR"),
                                    rx.tooltip(
                                        rx.icon_button(
                                            rx.icon("dollar-sign", size=18),
                                            on_click=lambda: (
                                                LiquidacionesState.open_payment_modal_bulk(
                                                    liq["id_propietario"],
                                                    liq["periodo"],
                                                )
                                            ),
                                            size="2",
                                            variant="ghost",
                                            color_scheme="violet",
                                        ),
                                        content="Registrar pago masivo",
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


def liquidaciones_page() -> rx.Component:
    """Página principal de liquidaciones."""
    return rx.vstack(
        # Header
        rx.vstack(
            rx.heading(
                "Liquidaciones de Propietarios",
                size="8",
                weight="bold",
                color=styles.TEXT_PRIMARY,
            ),
            rx.text(
                "Gestión de estados de cuenta mensuales y pagos a propietarios",
                size="4",
                color=styles.TEXT_SECONDARY,
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
                icon="alert-triangle",
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
                on_submit=LiquidacionesState.generar_liquidacion_masiva,
                on_cancel=LiquidacionesState.close_modal,
                is_loading=LiquidacionesState.is_loading,
            ),
            rx.box(),
        ),
        cancel_modal(),
        reverse_confirm_dialog(),
        modal_exportar_liquidaciones_periodo(),
        width="100%",
        spacing="4",
        padding="2em",
    )


@rx.page(
    route="/liquidaciones",
    title="Liquidaciones",
    on_load=[AuthState.require_login, LiquidacionesState.on_load],
)
def liquidaciones() -> rx.Component:
    """Página de liquidaciones con layout."""
    return rx.box(dashboard_layout(liquidaciones_page()))
