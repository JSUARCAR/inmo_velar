"""Página de Contratos - Reflex Elite"""

import reflex as rx
from src.presentacion_reflex import styles
from src.presentacion_reflex.components.layout.dashboard_layout import dashboard_layout
from src.presentacion_reflex.state.auth_state import AuthState
from src.presentacion_reflex.state.contratos_state import ContratosState
from src.presentacion_reflex.components.neuro_elements import (
    neuro_input,
    neuro_select_root,
    neuro_button,
    neuro_icon_action_button,
    neuro_badge,
    neuro_panel,
)
from src.presentacion_reflex.components.tablas import header_cell_sortable
from src.presentacion_reflex.components.contratos.tarjeta_contrato import (
    tarjeta_contrato,
)
from src.presentacion_reflex.components.contratos.badge_grupo_pago import badge_grupo_pago

from src.presentacion_reflex.components.contratos.formulario_contrato_mandato import (
    formulario_contrato_mandato,
)
from src.presentacion_reflex.components.contratos.formulario_contrato_arrendamiento import (
    formulario_contrato_arrendamiento,
)
from src.presentacion_reflex.components.contratos.modal_detalle_contrato import (
    modal_detalle_contrato,
)
from src.presentacion_reflex.components.contratos.modal_incremento_ipc import (
    modal_incremento_ipc,
)
from src.presentacion_reflex.components.contratos.modal_renovacion_contrato import (
    modal_renovacion_contrato,
)
from src.presentacion_reflex.components.shared.elite_gradient_icon import (
    elite_gradient_icon_labeled,
)
from src.presentacion_reflex.state.pdf_state import PDFState


def render_table_view() -> rx.Component:
    """Tabla de contratos con botones del ciclo flat-raised-inset."""

    def _tabla_acciones(c: rx.Var) -> rx.Component:
        return rx.hstack(
            # Detalle
            neuro_icon_action_button(
                "eye",
                color_scheme="blue",
                size="1",
                tooltip_content="Ver Detalle",
                on_click=lambda: ContratosState.open_detail_modal(
                    c.id_contrato, c.tipo_contrato
                ),
            ),
            # Editar
            rx.cond(
                AuthState.check_action("Contratos", "EDITAR"),
                neuro_icon_action_button(
                    "pencil",
                    color_scheme="gray",
                    size="1",
                    tooltip_content="Editar",
                    on_click=lambda: ContratosState.open_edit_modal(
                        c.id_contrato, c.tipo_contrato
                    ),
                ),
            ),
            # Renovar
            rx.cond(
                AuthState.check_action("Contratos", "RENOVAR"),
                neuro_icon_action_button(
                    "refresh-cw",
                    color_scheme="green",
                    size="1",
                    tooltip_content="Renovar Contrato",
                    disabled=c.estado_contrato != "ACTIVO",
                    on_click=lambda: ContratosState.confirm_renewal(
                        c.id_contrato, c.tipo_contrato
                    ),
                ),
            ),
            # IPC — solo Arrendamiento
            rx.cond(
                (c.tipo_contrato == "Arrendamiento")
                & AuthState.check_action("Contratos", "IPC"),
                neuro_icon_action_button(
                    "trending-up",
                    color_scheme="cyan",
                    size="1",
                    tooltip_content="Aplicar IPC",
                    disabled=c.estado_contrato != "ACTIVO",
                    on_click=lambda: ContratosState.open_ipc_modal(c.id_contrato),
                ),
            ),
            # PDF Contrato Oficial
            neuro_icon_action_button(
                "file-check",
                color_scheme="purple",
                size="1",
                tooltip_content="Generar Contrato Oficial",
                on_click=lambda: PDFState.generar_contrato_oficial_elite(
                    c.id_contrato, c.tipo_contrato, False
                ),
            ),
            # Terminar
            rx.cond(
                AuthState.check_action("Contratos", "TERMINAR"),
                neuro_icon_action_button(
                    "ban",
                    color_scheme="red",
                    size="1",
                    tooltip_content="Terminar Contrato",
                    disabled=c.estado_contrato != "ACTIVO",
                    on_click=lambda: ContratosState.toggle_estado(
                        c.id_contrato, c.tipo_contrato, c.estado_contrato
                    ),
                ),
            ),
            spacing="2",
        )

    return rx.table.root(
        rx.table.header(
            rx.table.row(
                header_cell_sortable(
                    "Propiedad",
                    "direccion",
                    ContratosState.sort_by,
                    ContratosState.sort_order,
                    ContratosState.toggle_sort,
                ),
                header_cell_sortable(
                    "Tipo",
                    "tipo_contrato",
                    ContratosState.sort_by,
                    ContratosState.sort_order,
                    ContratosState.toggle_sort,
                ),
                header_cell_sortable(
                    "Estado",
                    "estado_contrato",
                    ContratosState.sort_by,
                    ContratosState.sort_order,
                    ContratosState.toggle_sort,
                ),
                rx.table.column_header_cell("Cumplimiento"),
                header_cell_sortable(
                    "Propietario/Arrendatario",
                    "propietario_nombre",
                    ContratosState.sort_by,
                    ContratosState.sort_order,
                    ContratosState.toggle_sort,
                ),
                header_cell_sortable(
                    "Valor",
                    "valor_canon",
                    ContratosState.sort_by,
                    ContratosState.sort_order,
                    ContratosState.toggle_sort,
                ),
                header_cell_sortable(
                    "Fecha Pago",
                    "fecha_pago",
                    ContratosState.sort_by,
                    ContratosState.sort_order,
                    ContratosState.toggle_sort,
                ),
                header_cell_sortable(
                    "Fechas",
                    "fecha_inicio",
                    ContratosState.sort_by,
                    ContratosState.sort_order,
                    ContratosState.toggle_sort,
                ),
                rx.table.column_header_cell("Acciones"),
            )
        ),
        rx.table.body(
            rx.foreach(
                ContratosState.contratos,
                lambda c: rx.table.row(
                    rx.table.cell(
                        rx.vstack(
                            rx.hstack(
                                rx.icon("hash", size=14, color="var(--gray-9)"),
                                rx.text(
                                    "ID: ",
                                    c.id_contrato.to_string(),
                                    weight="bold",
                                    size="1",
                                    color="var(--gray-11)",
                                ),
                                align="center",
                                spacing="1",
                            ),
                            rx.text(c.propiedad_direccion, weight="bold", size="2"),
                            rx.text(
                                c.propiedad_matricula,
                                size="1",
                                color=styles.TEXT_SECONDARY,
                            ),
                            spacing="1",
                        )
                    ),
                    rx.table.cell(
                        neuro_badge(
                            c.tipo_contrato,
                            color_scheme=rx.cond(
                                c.tipo_contrato == "Mandato", "blue", "green"
                            ),
                        )
                    ),
                    rx.table.cell(
                        neuro_badge(
                            c.estado_contrato,
                            color_scheme=rx.cond(
                                c.estado_contrato == "ACTIVO", "green", "red"
                            ),
                        )
                    ),
                    rx.table.cell(
                        neuro_badge(
                            rx.cond(
                                c.estado_cumplimiento == "AL_DIA",
                                "Al día",
                                rx.cond(
                                    c.estado_cumplimiento == "VENCIDO",
                                    "Vencido",
                                    "Pendiente",
                                ),
                            ),
                            color_scheme=rx.cond(
                                c.estado_cumplimiento == "AL_DIA",
                                "green",
                                rx.cond(
                                    c.estado_cumplimiento == "VENCIDO",
                                    "red",
                                    "yellow",
                                ),
                            ),
                            tooltip=rx.cond(
                                c.estado_cumplimiento == "AL_DIA",
                                "Pago al día",
                                rx.cond(
                                    c.estado_cumplimiento == "VENCIDO",
                                    "Pago vencido",
                                    "Pago pendiente",
                                ),
                            ),
                        )
                    ),
                    rx.table.cell(
                        rx.vstack(
                            rx.text(
                                rx.cond(
                                    c.tipo_contrato == "Mandato",
                                    c.propietario_nombre,
                                    c.arrendatario_nombre,
                                ),
                                size="2",
                            ),
                            rx.text(
                                rx.cond(
                                    c.tipo_contrato == "Mandato",
                                    c.propietario_documento,
                                    c.arrendatario_documento,
                                ),
                                size="1",
                                color=styles.TEXT_SECONDARY,
                            ),
                            rx.cond(
                                c.habitante_nombre != "",
                                rx.hstack(
                                    rx.icon(
                                        "home", size=12, color=styles.TEXT_SECONDARY
                                    ),
                                    rx.text(
                                        c.habitante_nombre,
                                        size="1",
                                        color=styles.TEXT_SECONDARY,
                                    ),
                                    spacing="1",
                                    align="center",
                                ),
                            ),
                            rx.cond(
                                c.asesor_nombre != "",
                                rx.hstack(
                                    rx.icon(
                                        "headset", size=12, color=styles.TEXT_SECONDARY
                                    ),
                                    rx.text(
                                        c.asesor_nombre,
                                        size="1",
                                        color=styles.TEXT_SECONDARY,
                                    ),
                                    spacing="1",
                                    align="center",
                                ),
                            ),
                            spacing="1",
                        )
                    ),
                    rx.table.cell(
                        rx.text("$", c.valor_canon.to_string(), weight="bold")
                    ),
                    rx.table.cell(
                        badge_grupo_pago(c.grupo_operativo, c.fecha_pago)
                    ),
                    rx.table.cell(
                        rx.vstack(
                            rx.text("Inicia: ", c.fecha_inicio, size="1"),
                            rx.text("Vence: ", c.fecha_fin, size="1"),
                            spacing="1",
                        )
                    ),
                    rx.table.cell(_tabla_acciones(c)),
                ),
            )
        ),
        width="100%",
        class_name="neu-table-elite",
    )


def _render_kpi_card(
    title: str, icon: str, total: int, activos: int, inactivos: int, color_scheme: str
) -> rx.Component:
    """Componente para renderizar un KPI de Elite."""
    return neuro_panel(
        rx.hstack(
            rx.box(
                rx.icon(icon, size=24, color=f"var(--{color_scheme}-9)"),
                padding="3",
                border_radius="12px",
                background=f"var(--{color_scheme}-3)",
            ),
            rx.vstack(
                rx.text(title, size="2", color=styles.TEXT_SECONDARY, weight="medium"),
                rx.hstack(
                    rx.text(
                        total.to_string(),
                        size="6",
                        weight="bold",
                        color="var(--gray-12)",
                    ),
                    rx.spacer(),
                    rx.hstack(
                        neuro_badge(
                            f"{activos.to_string()} Activos",
                            color_scheme="green",
                            size="1",
                        ),
                        neuro_badge(
                            f"{inactivos.to_string()} Inactivos",
                            color_scheme="gray",
                            size="1",
                        ),
                        spacing="2",
                    ),
                    align="center",
                    width="100%",
                ),
                width="100%",
                spacing="1",
            ),
            spacing="4",
            align="center",
            width="100%",
        ),
        width="100%",
        min_width="320px",
    )


def contratos_page() -> rx.Component:
    """Componente principal de la página de contratos."""
    return rx.box(
        dashboard_layout(
            rx.vstack(
                # Encabezado
                rx.box(
                    rx.flex(
                        elite_gradient_icon_labeled(
                            "file-text",
                            "Gestión de Contratos",
                            description="Administración de mandatos y arrendamientos",
                            size=28,
                            color_scheme="terracotta",
                        ),
                        rx.cond(
                            AuthState.check_action("Contratos", "CREAR"),
                            rx.flex(
                                neuro_button(
                                    rx.icon("plus", size=18),
                                    "Nuevo Mandato",
                                    on_click=ContratosState.open_create_mandato_modal,
                                    variant="surface",
                                    style={"box_shadow": styles.SHADOW_RAISED_ELITE},
                                    width=rx.breakpoints(initial="100%", md="auto"),
                                ),
                                neuro_button(
                                    rx.icon("plus", size=18),
                                    "Nuevo Arriendo",
                                    on_click=ContratosState.open_create_arrendamiento_modal,
                                    variant="surface",
                                    style={"box_shadow": styles.SHADOW_RAISED_ELITE},
                                    width=rx.breakpoints(initial="100%", md="auto"),
                                ),
                                gap="3",
                                flex_wrap="wrap",
                                justify=rx.breakpoints(initial="start", md="end"),
                                width=rx.breakpoints(initial="100%", md="auto"),
                            ),
                        ),
                        width="100%",
                        padding="5",
                        align=rx.breakpoints(initial="start", md="center"),
                        justify="between",
                        flex_direction=rx.breakpoints(initial="column", md="row"),
                        flex_wrap="wrap",
                        gap="4",
                    ),
                    width="100%",
                ),
                # Contenedor KPIs
                rx.grid(
                    _render_kpi_card(
                        "Mandatos",
                        "briefcase",
                        ContratosState.kpi_mandatos_total,
                        ContratosState.kpi_mandatos_activos,
                        ContratosState.kpi_mandatos_inactivos,
                        "blue",
                    ),
                    _render_kpi_card(
                        "Arrendamientos",
                        "key",
                        ContratosState.kpi_arriendos_total,
                        ContratosState.kpi_arriendos_activos,
                        ContratosState.kpi_arriendos_inactivos,
                        "indigo",
                    ),
                    columns=rx.breakpoints(initial="1", md="2"),
                    spacing="4",
                    width="100%",
                ),
                # Barra de Herramientas (Filtros y Búsqueda)
                neuro_panel(
                    rx.flex(
                        neuro_input(
                            rx.input.slot(rx.icon("search", size=18)),
                            placeholder="Buscar por dirección, nombre o documento...",
                            value=ContratosState.search_text,
                            on_change=ContratosState.set_search,
                            on_key_down=ContratosState.handle_search_key_down,
                            width=["100%", "100%", "400px"],
                            style={"box_shadow": styles.SHADOW_INSET_ELITE},
                        ),
                        # Filtros y acciones agrupados (sin rx.spacer)
                        rx.flex(
                            neuro_select_root(
                                rx.foreach(
                                    ContratosState.asesores_filter_options,
                                    lambda opt: rx.select.item(opt[0], value=opt[1]),
                                ),
                                value=ContratosState.filter_asesor_id,
                                on_change=ContratosState.set_filter_asesor_id,
                                width=["100%", "100%", "200px"],
                                style={
                                    "box_shadow": styles.SHADOW_INSET_ELITE,
                                    "border_radius": "8px",
                                },
                            ),
                            neuro_select_root(
                                rx.foreach(
                                    ContratosState.tipo_options,
                                    lambda opt: rx.select.item(opt, value=opt),
                                ),
                                value=ContratosState.filter_tipo,
                                on_change=ContratosState.set_filter_tipo,
                                width=["100%", "100%", "160px"],
                                style={
                                    "box_shadow": styles.SHADOW_INSET_ELITE,
                                    "border_radius": "8px",
                                },
                            ),
                            neuro_select_root(
                                rx.foreach(
                                    ContratosState.estado_options,
                                    lambda opt: rx.select.item(opt, value=opt),
                                ),
                                value=ContratosState.filter_estado,
                                on_change=ContratosState.set_filter_estado,
                                width=["100%", "100%", "140px"],
                                style={
                                    "box_shadow": styles.SHADOW_INSET_ELITE,
                                    "border_radius": "8px",
                                },
                            ),
                            # Filtro: Mandatos sin arriendo activo
                            rx.cond(
                                ContratosState.filter_tipo != "Arrendamiento",
                                rx.tooltip(
                                    rx.box(
                                        rx.checkbox(
                                            "Sin arriendo",
                                            checked=ContratosState.filter_sin_arrendamiento,
                                            on_change=ContratosState.set_filter_sin_arrendamiento,
                                            size="2",
                                            color_scheme="orange",
                                        ),
                                        padding="8px 12px",
                                        border_radius="8px",
                                        background=rx.cond(
                                            ContratosState.filter_sin_arrendamiento,
                                            "var(--orange-3)",
                                            "transparent",
                                        ),
                                        style={
                                            "box_shadow": rx.cond(
                                                ContratosState.filter_sin_arrendamiento,
                                                styles.SHADOW_INSET_ELITE,
                                                "none",
                                            ),
                                            "transition": "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
                                            "white_space": "nowrap",
                                        },
                                    ),
                                    content="Mostrar solo mandatos sin contrato de arriendo activo",
                                ),
                            ),
                            neuro_button(
                                rx.cond(
                                    ContratosState.is_grid_view,
                                    rx.icon("table"),
                                    rx.icon("layout-grid"),
                                ),
                                on_click=ContratosState.toggle_view,
                            ),
                            rx.tooltip(
                                neuro_button(
                                    rx.icon("file-spreadsheet", size=16),
                                    on_click=ContratosState.exportar_csv,
                                    size="3",
                                    style={"min_width": "44px"},
                                ),
                                content="Exportar a Excel",
                            ),
                            gap="3",
                            flex_wrap="wrap",
                            flex_direction=rx.breakpoints(initial="column", md="row"),
                            align=rx.breakpoints(initial="stretch", md="center"),
                            width=rx.breakpoints(initial="100%", md="auto"),
                        ),
                        width="100%",
                        flex_direction=rx.breakpoints(initial="column", md="row"),
                        align=rx.breakpoints(initial="stretch", md="center"),
                        gap="4",
                    ),
                    width="100%",
                ),
                # Contenido de Datos
                rx.cond(
                    ContratosState.is_loading,
                    rx.center(rx.spinner(size="3"), height="400px", width="100%"),
                    rx.box(
                        rx.cond(
                            ContratosState.total_items == 0,
                            rx.center(
                                rx.vstack(
                                    rx.icon("search-x", size=64, color="var(--gray-6)"),
                                    rx.text(
                                        "No se encontraron contratos",
                                        size="5",
                                        weight="bold",
                                    ),
                                    rx.text(
                                        "Ajusta los filtros o registra uno nuevo",
                                        size="2",
                                        color=styles.TEXT_SECONDARY,
                                    ),
                                    spacing="3",
                                    align="center",
                                ),
                                height="400px",
                                width="100%",
                            ),
                            rx.box(
                                rx.cond(
                                    ContratosState.is_grid_view,
                                    rx.grid(
                                        rx.foreach(
                                            ContratosState.contratos, tarjeta_contrato
                                        ),
                                        columns=rx.breakpoints(
                                            initial="1", sm="2", lg="3"
                                        ),
                                        gap="8",
                                        width="100%",
                                        padding="4",
                                    ),
                                    render_table_view(),
                                ),
                                width="100%",
                            ),
                        ),
                        width="100%",
                    ),
                ),
                # Paginación
                neuro_panel(
                    rx.hstack(
                        neuro_button(
                            rx.icon("chevron-left", size=16),
                            rx.text(
                                "Anterior",
                                display=rx.breakpoints(initial="none", md="block"),
                            ),
                            on_click=ContratosState.prev_page,
                            disabled=ContratosState.current_page == 1,
                        ),
                        rx.text(
                            "Pág. ",
                            ContratosState.current_page,
                            weight="medium",
                            size=rx.breakpoints(initial="2", md="3"),
                        ),
                        neuro_button(
                            rx.text(
                                "Siguiente",
                                display=rx.breakpoints(initial="none", md="block"),
                            ),
                            rx.icon("chevron-right", size=16),
                            on_click=ContratosState.next_page,
                            disabled=ContratosState.current_page
                            * ContratosState.page_size
                            >= ContratosState.total_items,
                        ),
                        justify="center",
                        width="100%",
                        spacing="4",
                        align="center",
                    ),
                    width="100%",
                ),
                spacing="6",
                width="100%",
                padding_x=["4", "6"],
                padding_bottom="8",
            ),
        ),
        # Modales
        formulario_contrato_mandato(),
        formulario_contrato_arrendamiento(),
        modal_detalle_contrato(),
        modal_incremento_ipc(),
        modal_renovacion_contrato(),
    )


# Ruta protegida
@rx.page(route="/contratos", on_load=[AuthState.require_login, ContratosState.on_load])
def contratos():
    return contratos_page()
