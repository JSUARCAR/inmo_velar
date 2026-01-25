"""
Página de Recaudos (Pagos de Arrendatarios)
Gestión completa de pagos recibidos
"""

import reflex as rx

from src.presentacion_reflex.components.layout.dashboard_layout import dashboard_layout
from src.presentacion_reflex.components.recaudos import modal_detalle_recaudo, modal_recaudo
from src.presentacion_reflex.state.auth_state import AuthState
from src.presentacion_reflex.state.pdf_state import PDFState
from src.presentacion_reflex.state.recaudos_state import RecaudosState


def render_estado_badge(estado: rx.Var) -> rx.Component:
    """Renderiza badge con color según estado."""
    return rx.match(
        estado,
        ("Pendiente", rx.badge("Pendiente", color_scheme="yellow", variant="solid")),
        ("Aplicado", rx.badge("Aplicado", color_scheme="green", variant="solid")),
        ("Reversado", rx.badge("Reversado", color_scheme="red", variant="solid")),
        rx.badge(estado, color_scheme="gray", variant="soft"),
    )


def recaudos_toolbar() -> rx.Component:
    """Barra de herramientas con filtros y búsqueda."""
    return rx.hstack(
        # Búsqueda
        rx.input(
            placeholder="Buscar por propiedad, arrendatario, matrícula...",
            value=RecaudosState.search_text,
            on_change=RecaudosState.set_search,
            on_key_down=lambda key: RecaudosState.handle_search_key_down(key),
            width="350px",
        ),
        # Filtro Estado
        rx.select(
            RecaudosState.estado_options,
            placeholder="Estado",
            value=RecaudosState.filter_estado,
            on_change=RecaudosState.set_filter_estado,
            width="150px",
        ),
        # Filtro Fecha Desde
        rx.input(
            placeholder="Desde",
            type="date",
            value=RecaudosState.filter_fecha_desde,
            on_change=RecaudosState.set_filter_fecha_desde,
            width="150px",
        ),
        # Filtro Fecha Hasta
        rx.input(
            placeholder="Hasta",
            type="date",
            value=RecaudosState.filter_fecha_hasta,
            on_change=RecaudosState.set_filter_fecha_hasta,
            width="150px",
        ),
        rx.spacer(),
        # Botón Registrar Pago
        rx.cond(
            AuthState.check_action("Recaudos", "CREAR"),
            rx.button(
                rx.icon("plus"),
                "Registrar Pago",
                on_click=RecaudosState.open_create_modal,
                color_scheme="green",
            ),
        ),
        # Botón Generar Pagos Masivos
        rx.cond(
            AuthState.check_action("Recaudos", "CREAR"),
            rx.tooltip(
                rx.button(
                    rx.icon("copy-plus"),
                    "Generar Masivos",
                    on_click=RecaudosState.generar_pagos_masivos,
                    color_scheme="blue",
                    variant="soft",
                ),
                content="Genera pagos para todos los contratos activos con fecha de hoy, valor del canon y método Efectivo",
            ),
        ),
        # Botón Refresh
        rx.button(
            rx.icon("refresh-cw"),
            on_click=RecaudosState.load_recaudos,
            variant="soft",
        ),
        width="100%",
        padding="1em",
        background="white",
        border_radius="8px",
        box_shadow="sm",
        spacing="3",
    )


def recaudos_table() -> rx.Component:
    """Tabla de recaudos."""
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("ID", style={"font-weight": "600"}),
                rx.table.column_header_cell("Fecha Pago", style={"font-weight": "600"}),
                rx.table.column_header_cell("Propiedad", style={"font-weight": "600"}),
                rx.table.column_header_cell("Arrendatario", style={"font-weight": "600"}),
                rx.table.column_header_cell("Valor", style={"font-weight": "600"}),
                rx.table.column_header_cell("Método", style={"font-weight": "600"}),
                rx.table.column_header_cell("Estado", style={"font-weight": "600"}),
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
                        rx.vstack(
                            rx.text(rec["direccion"], size="2", weight="medium"),
                            rx.text(
                                f"Matrícula: {rec['matricula']}",
                                size="1",
                                color="gray",
                            ),
                            spacing="1",
                            align="start",
                        )
                    ),
                    rx.table.cell(rec["arrendatario"]),
                    rx.table.cell(
                        rx.text(
                            f"${rec['valor_total']:,}",
                            weight="bold",
                            color="green",
                        )
                    ),
                    rx.table.cell(rx.badge(rec["metodo_pago"], variant="soft")),
                    rx.table.cell(render_estado_badge(rec["estado"])),
                    rx.table.cell(
                        rx.hstack(
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
                            # Aplicar Pago (solo Pendientes)
                            rx.cond(
                                (rec["estado"] == "Pendiente")
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
                            # Editar (solo Pendientes)
                            rx.cond(
                                (rec["estado"] == "Pendiente")
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
                            # Eliminar (solo Pendientes)
                            rx.cond(
                                (rec["estado"] == "Pendiente")
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
                "Anterior",
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
                    f"Página {RecaudosState.current_page}",
                    size="3",
                    weight="medium",
                ),
                rx.text(
                    f"Mostrando {(RecaudosState.current_page - 1) * RecaudosState.page_size + 1}-"
                    f"{rx.cond((RecaudosState.current_page * RecaudosState.page_size) > RecaudosState.total_items, RecaudosState.total_items, RecaudosState.current_page * RecaudosState.page_size)} "
                    f"de {RecaudosState.total_items}",
                    size="1",
                    color="var(--gray-10)",
                ),
                spacing="0",
                align="center",
            ),
            rx.button(
                "Siguiente",
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
            "background": "var(--color-panel-solid)",
        },
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
                color="gray",
                weight="medium",
            ),
            spacing="2",
            margin_bottom="2rem",
        ),
        # Toolbar
        recaudos_toolbar(),
        # Error message
        rx.cond(
            RecaudosState.error_message != "",
            rx.callout(
                RecaudosState.error_message,
                icon="circle-alert",
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
        width="100%",
        spacing="4",
        padding="2em",
    )


@rx.page(
    route="/recaudos", title="Recaudos", on_load=[AuthState.require_login, RecaudosState.on_load]
)
def recaudos() -> rx.Component:
    """Página de recaudos con layout."""
    return dashboard_layout(recaudos_page())
