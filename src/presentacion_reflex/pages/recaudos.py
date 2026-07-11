"""
Página de Recaudos (Pagos de Arrendatarios)
Gestión completa de pagos recibidos
"""

import reflex as rx
from typing import Any
from src.presentacion_reflex import styles

from src.presentacion_reflex.components.layout.dashboard_layout import dashboard_layout
from src.presentacion_reflex.components.recaudos import (
    modal_detalle_recaudo,
    modal_recaudo,
)
from src.presentacion_reflex.state.auth_state import AuthState
from src.presentacion_reflex.state.pdf_state import PDFState
from src.presentacion_reflex.state.recaudos_state import RecaudosState


from src.presentacion_reflex.components.neuro_elements import (
    neuro_floating_input,
    neuro_floating_select,
    neuro_button,
)
from src.presentacion_reflex.components.shared.advanced_filter_bar import advanced_filter_bar


def render_estado_badge(estado: rx.Var) -> rx.Component:
    """Renderiza badge con color según estado."""
    return rx.match(
        estado,
        ("Pendiente", rx.badge("Pendiente", color_scheme="yellow", variant="solid")),
        ("Aplicado", rx.badge("Aplicado", color_scheme="green", variant="solid")),
        ("Reversado", rx.badge("Reversado", color_scheme="red", variant="solid")),
        ("Vencido", rx.badge("Vencido", color_scheme="red", variant="solid")),
        rx.badge(estado, color_scheme="gray", variant="soft"),
    )


def multi_select_popover(
    label: str,
    options: Any,
    selected_values: Any,
    on_toggle: Any,
) -> rx.Component:
    """Componente para multi-select usando popover y checkboxes."""
    
    # Texto a mostrar en el trigger
    trigger_text = rx.cond(
        selected_values.length() > 0,
        rx.cond(
            selected_values.contains("Todos") & (selected_values.length() == 1),
            "Todos",
            f"{selected_values.length()} seleccionados"
        ),
        "Todos"
    )
    
    return rx.box(
        rx.text(label, style=styles.NEU_FILTER_LABEL_STYLE),
        rx.popover.root(
            rx.popover.trigger(
                rx.button(
                    rx.text(trigger_text, truncate=True),
                    rx.icon("chevron-down", size=16),
                    variant="surface",
                    style=styles.NEU_FILTER_INPUT_STYLE,
                    width="100%",
                    justify_content="space-between",
                    color=styles.TEXT_PRIMARY,
                )
            ),
            rx.popover.content(
                rx.scroll_area(
                    rx.vstack(
                        rx.foreach(
                            options,
                            lambda opt: rx.checkbox(
                                opt,
                                checked=rx.cond(
                                    selected_values.length() == 0,
                                    opt == "Todos",
                                    selected_values.contains(opt)
                                ),
                                on_change=lambda c: on_toggle(c, opt),
                                size="2"
                            )
                        ),
                        align_items="start",
                    ),
                    type="auto",
                    scrollbars="vertical",
                    style={"max_height": "250px", "padding": "10px"},
                ),
                width="200px",
                style={"z_index": styles.Z_POPOVER, "pointer_events": "auto"}
            )
        ),
        width=["100%", "100%", "150px"]
    )


def recaudos_toolbar() -> rx.Component:
    """Barra de herramientas con filtros y búsqueda (Elite)."""
    return advanced_filter_bar(
        # Filtro Estado
        rx.box(
            rx.text("Estado", style=styles.NEU_FILTER_LABEL_STYLE),
            rx.select(
                ["Todos", "Pendiente", "Vencido", "Aplicado", "Reversado"],
                value=RecaudosState.filter_estado,
                on_change=RecaudosState.set_filter_estado,
                placeholder="Estado",
                style=styles.NEU_FILTER_SELECT_STYLE,
            ),
            width=["100%", "100%", "150px"]
        ),
        # Filtro Pago Contrato
        multi_select_popover(
            label="Pago Contrato",
            options=RecaudosState.dias_pago_options,
            selected_values=RecaudosState.filter_dia_pago,
            on_toggle=RecaudosState.toggle_filter_dia_pago,
        ),
        # Filtro Ciclo Operativo
        multi_select_popover(
            label="Ciclo Operativo",
            options=RecaudosState.ciclo_operativo_options,
            selected_values=RecaudosState.filter_ciclo_operativo,
            on_toggle=RecaudosState.toggle_filter_ciclo_operativo,
        ),
        # Filtro Fecha Desde
        rx.box(
            rx.text("Desde", style=styles.NEU_FILTER_LABEL_STYLE),
            rx.input(
                type="date",
                value=RecaudosState.filter_fecha_desde,
                on_change=RecaudosState.set_filter_fecha_desde,
                style=styles.NEU_FILTER_INPUT_STYLE,
            ),
            width=["100%", "100%", "150px"]
        ),
        # Filtro Fecha Hasta
        rx.box(
            rx.text("Hasta", style=styles.NEU_FILTER_LABEL_STYLE),
            rx.input(
                type="date",
                value=RecaudosState.filter_fecha_hasta,
                on_change=RecaudosState.set_filter_fecha_hasta,
                style=styles.NEU_FILTER_INPUT_STYLE,
            ),
            width=["100%", "100%", "150px"]
        ),
        search_placeholder="Buscar por propiedad, arrendatario, matrícula...",
        on_search=RecaudosState.set_search,
        search_value=RecaudosState.search_text,
        on_key_down=RecaudosState.handle_search_key_down,
        on_clear=RecaudosState.clear_filters,
        active_filter_count=RecaudosState.active_filter_count,
        action_buttons=[
            # Botón Registrar Pago
            rx.cond(
                AuthState.check_action("Recaudos", "CREAR"),
                rx.tooltip(
                    rx.icon_button(
                        rx.icon("plus", size=18),
                        color_scheme="green",
                        style=styles.NEU_FILTER_ICON_BUTTON_STYLE,
                        on_click=RecaudosState.open_create_modal,
                    ),
                    content="Registrar Pago",
                ),
            ),
            # Botón Generar Pagos Masivos
            rx.cond(
                AuthState.check_action("Recaudos", "CREAR"),
                rx.tooltip(
                    rx.icon_button(
                        rx.icon("copy_plus", size=18),
                        color_scheme="blue",
                        style=styles.NEU_FILTER_ICON_BUTTON_STYLE,
                        on_click=RecaudosState.generar_pagos_masivos,
                    ),
                    content="Generar Pagos Masivos",
                ),
            ),
            # Botón Exportar Recibos ZIP
            rx.cond(
                AuthState.check_action("Recaudos", "CREAR"),
                rx.tooltip(
                    rx.icon_button(
                        rx.icon("file_archive", size=18),
                        color_scheme="cyan",
                        style=styles.NEU_FILTER_ICON_BUTTON_STYLE,
                        on_click=RecaudosState.abrir_modal_exportar_recibos,
                        loading=RecaudosState.exportando_recibos,
                    ),
                    content="Exportar Recibos (ZIP)",
                ),
            ),
            # Botón Exportar CSV
            rx.tooltip(
                rx.icon_button(
                    rx.icon("file_spreadsheet", size=18),
                    color_scheme="green",
                    style=styles.NEU_FILTER_ICON_BUTTON_STYLE,
                    on_click=RecaudosState.exportar_csv,
                ),
                content="Exportar a Excel",
            ),
            # Botón Refresh
            rx.tooltip(
                rx.icon_button(
                    rx.icon("refresh_cw", size=18),
                    style=styles.NEU_FILTER_ICON_BUTTON_STYLE,
                    on_click=RecaudosState.load_recaudos,
                ),
                content="Recargar",
            ),
        ]
    )


def header_cell_sortable(label: str, column_id: str) -> rx.Component:
    """Renderiza celda de encabezado con capacidad de ordenamiento."""
    is_active = RecaudosState.sort_by == column_id

    return rx.table.column_header_cell(
        rx.hstack(
            rx.text(label, weight="bold"),
            rx.cond(
                is_active,
                rx.cond(
                    RecaudosState.sort_order == "desc",
                    rx.icon("chevron-down", size=16),
                    rx.icon("chevron-up", size=16),
                ),
                rx.icon("chevrons-up-down", size=14, opacity=0.3),
            ),
            spacing="2",
            align="center",
            cursor="pointer",
            on_click=lambda: RecaudosState.toggle_sort(column_id),
            _hover={"opacity": 0.8},
        ),
        style={"font-weight": "600"},
    )


def recaudos_table() -> rx.Component:
    """Tabla de recaudos."""
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                header_cell_sortable("ID", "id_recaudo"),
                header_cell_sortable("Fecha Pago", "fecha_pago"),
                header_cell_sortable("Pago Contrato", "fecha_pago_contrato"),
                header_cell_sortable("Ciclo Operativo", "ciclo_operativo"),
                header_cell_sortable("Propiedad", "direccion"),
                header_cell_sortable("Arrendatario", "arrendatario"),
                header_cell_sortable("Habitante", "habitante"),
                header_cell_sortable("Valor", "valor_total"),
                rx.table.column_header_cell("Método", style={"font-weight": "600"}),
                header_cell_sortable("Estado", "estado"),
                rx.table.column_header_cell(
                    "Acciones", width="150px", style={"font-weight": "600"}
                ),
            ),
        ),
        rx.table.body(
            rx.foreach(
                RecaudosState.recaudos,
                lambda rec: rx.table.row(
                    rx.table.cell(rec["id_recaudo"]),
                    rx.table.cell(rec["fecha_pago"]),
                    rx.table.cell(
                        rx.badge(
                            rec["fecha_pago_contrato"],
                            variant="surface",
                            color_scheme="indigo",
                        )
                    ),
                    rx.table.cell(
                        rx.cond(
                            rec["ciclo_operativo"] == "-",
                            rx.text("-", color="gray"),
                            rx.text(rec["ciclo_operativo"]),
                        )
                    ),
                    rx.table.cell(
                        rx.vstack(
                            rx.text(rec["direccion"], size="2", weight="medium"),
                            rx.text(
                                "Matrícula: ",
                                rec["matricula"],
                                size="1",
                                color="gray",
                            ),
                            spacing="1",
                            align="start",
                        )
                    ),
                    rx.table.cell(
                        rx.vstack(
                            rx.hstack(
                                rx.icon("phone", size=12, color="gray"),
                                rx.cond(
                                    rec["telefono_arrendatario"] != "",
                                    rx.text(
                                        rec["telefono_arrendatario"],
                                        size="1",
                                        color="gray",
                                    ),
                                    rx.text(
                                        "Sin registro",
                                        size="1",
                                        color="gray",
                                        font_style="italic",
                                    ),
                                ),
                                spacing="1",
                                align="center",
                            ),
                            rx.text(rec["arrendatario"], size="2", weight="medium"),
                            spacing="1",
                            align="start",
                        )
                    ),
                    rx.table.cell(
                        rx.cond(
                            rec["habitante"] != "",
                            rx.vstack(
                                rx.hstack(
                                    rx.icon("phone", size=12, color="gray"),
                                    rx.cond(
                                        rec["telefono_habitante"] != "",
                                        rx.text(
                                            rec["telefono_habitante"],
                                            size="1",
                                            color="gray",
                                        ),
                                        rx.text(
                                            "Sin registro",
                                            size="1",
                                            color="gray",
                                            font_style="italic",
                                        ),
                                    ),
                                    spacing="1",
                                    align="center",
                                ),
                                rx.text(rec["habitante"], size="2", weight="medium"),
                                spacing="1",
                                align="start",
                            ),
                            rx.text("—", size="2", color="gray"),
                        ),
                        display=rx.breakpoints(initial="none", md="table-cell"),
                    ),
                    rx.table.cell(
                        rx.text(
                            rec["valor_total_view"],
                            weight="bold",
                            color="green",
                        )
                    ),
                    rx.table.cell(rx.badge(rec["metodo_pago"], variant="soft")),
                    rx.table.cell(render_estado_badge(rec["estado"])),
                    rx.table.cell(
                        rx.hstack(
                            # Tooltip móvil: Info del habitante
                            rx.cond(
                                rec["habitante"] != "",
                                rx.tooltip(
                                    rx.icon(
                                        "user",
                                        size=14,
                                        display=rx.breakpoints(
                                            initial="block", md="none"
                                        ),
                                    ),
                                    content=rx.cond(
                                        rec["telefono_habitante"] != "",
                                        rec["habitante"].to_string()
                                        + " \u2022 "
                                        + rec["telefono_habitante"].to_string(),
                                        rec["habitante"].to_string(),
                                    ),
                                ),
                                rx.box(),
                            ),
                            # PDF Recibo de Pago
                            rx.tooltip(
                                rx.icon_button(
                                    rx.icon("file-text"),
                                    on_click=lambda: PDFState.generar_recibo_pago_pdf(
                                        rec["id_recaudo"]
                                    ),
                                    size="2",
                                    variant="ghost",
                                    color_scheme="green",
                                    loading=PDFState.generating,
                                    cursor="pointer",
                                ),
                                content="Generar Recibo de Pago PDF",
                            ),
                            # Ver Detalle (siempre visible)
                            rx.tooltip(
                                rx.icon_button(
                                    rx.icon("eye"),
                                    on_click=lambda: RecaudosState.open_detail_modal(
                                        rec["id_recaudo"]
                                    ),
                                    size="2",
                                    variant="ghost",
                                    color_scheme="gray",
                                ),
                                content="Ver detalle",
                            ),
                            # Aplicar Pago (Pendientes o Vencidos)
                            rx.cond(
                                (
                                    (rec["estado"] == "Pendiente")
                                    | (rec["estado"] == "Vencido")
                                )
                                & AuthState.check_action("Recaudos", "APLICAR"),
                                rx.tooltip(
                                    rx.icon_button(
                                        rx.icon("thumbs-up"),
                                        on_click=lambda: RecaudosState.aplicar_pago(
                                            rec["id_recaudo"]
                                        ),
                                        size="2",
                                        variant="ghost",
                                        color_scheme="green",
                                    ),
                                    content="Aplicar pago",
                                ),
                                rx.box(),
                            ),
                            # Reversar Pago (solo Aplicados)
                            rx.cond(
                                (rec["estado"] == "Aplicado")
                                & AuthState.check_action("Recaudos", "REVERSAR"),
                                rx.tooltip(
                                    rx.icon_button(
                                        rx.icon("rotate-ccw"),
                                        on_click=lambda: RecaudosState.reversar_pago(
                                            rec["id_recaudo"]
                                        ),
                                        size="2",
                                        variant="ghost",
                                        color_scheme="orange",
                                    ),
                                    content="Reversar pago",
                                ),
                                rx.box(),
                            ),
                            # Editar (Pendientes o Vencidos)
                            rx.cond(
                                (
                                    (rec["estado"] == "Pendiente")
                                    | (rec["estado"] == "Vencido")
                                )
                                & AuthState.check_action("Recaudos", "EDITAR"),
                                rx.tooltip(
                                    rx.icon_button(
                                        rx.icon("pencil"),
                                        on_click=lambda: RecaudosState.open_edit_modal(
                                            rec["id_recaudo"]
                                        ),
                                        size="2",
                                        variant="ghost",
                                        color_scheme="blue",
                                    ),
                                    content="Editar recaudo",
                                ),
                                rx.box(),
                            ),
                            # Eliminar (Pendientes o Vencidos)
                            rx.cond(
                                (
                                    (rec["estado"] == "Pendiente")
                                    | (rec["estado"] == "Vencido")
                                )
                                & AuthState.check_action("Recaudos", "ELIMINAR"),
                                rx.tooltip(
                                    rx.icon_button(
                                        rx.icon("trash-2"),
                                        on_click=lambda: RecaudosState.eliminar_recaudo(
                                            rec["id_recaudo"]
                                        ),
                                        size="2",
                                        variant="ghost",
                                        color_scheme="red",
                                    ),
                                    content="Eliminar recaudo",
                                ),
                                rx.box(),
                            ),
                            spacing="1",
                        )
                    ),
                ),
            ),
        ),
        width="100%",
        variant="surface",
    )


def pagination_controls() -> rx.Component:
    """Controles de paginación Premium."""
    return rx.card(
        rx.hstack(
            rx.button(
                rx.icon("chevron-left", size=16),
                rx.text("Anterior", display=rx.breakpoints(initial="none", md="block")),
                on_click=RecaudosState.prev_page,
                disabled=RecaudosState.current_page == 1,
                variant="soft",
                size="3",
                _hover={
                    "transform": "translateX(-2px)",
                },
                transition="transform 0.2s ease",
            ),
            rx.vstack(
                rx.text(
                    "Página ",
                    RecaudosState.current_page,
                    size=rx.breakpoints(initial="2", md="3"),
                    weight="medium",
                ),
                rx.text(
                    "Mostrando ",
                    (RecaudosState.current_page - 1) * RecaudosState.page_size + 1,
                    "-",
                    rx.cond(
                        (RecaudosState.current_page * RecaudosState.page_size)
                        > RecaudosState.total_items,
                        RecaudosState.total_items,
                        RecaudosState.current_page * RecaudosState.page_size,
                    ),
                    " de ",
                    RecaudosState.total_items,
                    size="1",
                    color="var(--gray-10)",
                    display=rx.breakpoints(initial="none", md="block"),
                ),
                spacing="0",
                align="center",
            ),
            rx.button(
                rx.text(
                    "Siguiente", display=rx.breakpoints(initial="none", md="block")
                ),
                rx.icon("chevron-right", size=16),
                on_click=RecaudosState.next_page,
                disabled=RecaudosState.current_page * RecaudosState.page_size
                >= RecaudosState.total_items,
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
            "background": styles.BG_PANEL,
        },
    )


def modal_exportar_recibos_periodo() -> rx.Component:
    """Modal para seleccionar período y exportar recibos de recaudo como ZIP."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.hstack(
                    rx.icon("file-archive", size=20, color="#667eea"),
                    rx.text("Exportar Recibos de Recaudo"),
                    spacing="2",
                    align="center",
                ),
            ),
            rx.dialog.description(
                "Seleccione el período contable para generar y descargar "
                "todos los recibos de recaudo en un archivo ZIP.",
                size="2",
                color="gray",
            ),
            rx.separator(margin_y="12px"),
            rx.vstack(
                neuro_floating_input(
                    label="Período",
                    placeholder="YYYY-MM",
                    type="month",
                    value=RecaudosState.periodo_exportar_recibos,
                    on_change=RecaudosState.set_periodo_exportar,
                    width="100%",
                    size="3",
                ),
                rx.text(
                    "Se generarán los recibos PDF individuales y se empaquetarán en un ZIP.",
                    size="1",
                    color="gray",
                ),
                spacing="2",
                width="100%",
            ),
            rx.separator(margin_y="12px"),
            rx.flex(
                rx.dialog.close(
                    neuro_button(
                        rx.text("Cancelar"),
                        variant="soft",
                        color_scheme="gray",
                        on_click=RecaudosState.cerrar_modal_exportar_recibos,
                    ),
                ),
                neuro_button(
                    rx.hstack(
                        rx.icon("download", size=16),
                        rx.text("Generar y Descargar ZIP"),
                    ),
                    on_click=RecaudosState.exportar_recibos_zip,
                    loading=RecaudosState.exportando_recibos,
                    color_scheme="indigo",
                ),
                spacing="3",
                justify="end",
                width="100%",
            ),
            max_width="450px",
        ),
        open=RecaudosState.mostrar_modal_exportar_recibos,
        on_open_change=lambda open: rx.cond(
            open,
            RecaudosState.abrir_modal_exportar_recibos,
            RecaudosState.cerrar_modal_exportar_recibos,
        ),
    )


def recaudos_page() -> rx.Component:
    """Página principal de recaudos."""
    return rx.vstack(
        # Header
        rx.vstack(
            rx.heading(
                "Recaudos - Pagos de Arrendatarios",
                size="8",
                weight="bold",
                background="linear-gradient(to right, #667eea, #764ba2)",
                background_clip="text",
                color="transparent",
            ),
            rx.text(
                "Registro y gestión de pagos recibidos de contratos de arrendamiento",
                size="4",
                color=styles.TEXT_SECONDARY,
                weight="medium",
            ),
            spacing="2",
            margin_bottom="2rem",
        ),
        # Toolbar
        recaudos_toolbar(),
        # Error message
        rx.cond(
            RecaudosState.error_message,
            rx.callout(
                RecaudosState.error_message,
                icon="triangle-alert",
                color_scheme="red",
                role="alert",
            ),
            rx.box(),
        ),
        # Loading o Tabla
        rx.cond(
            RecaudosState.is_loading,
            rx.center(
                rx.spinner(size="3"),
                min_height="400px",
            ),
            rx.vstack(
                recaudos_table(),
                pagination_controls(),
                width="100%",
                spacing="4",
            ),
        ),
        # Modal de formulario
        modal_recaudo(),
        # Modal de detalle
        modal_detalle_recaudo(),
        # Modal exportación masiva recibos
        modal_exportar_recibos_periodo(),
        width="100%",
        spacing="4",
        padding="2em",
    )


@rx.page(
    route="/recaudos",
    title="Recaudos | Inmobiliaria Velar",
    on_load=[AuthState.require_login, RecaudosState.on_load],
)
def recaudos() -> rx.Component:
    """Página de recaudos con layout."""
    return dashboard_layout(recaudos_page())
