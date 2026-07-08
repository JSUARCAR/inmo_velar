"""
Página de Propiedades - Reflex
Gestión de inventario inmobiliario con filtros, vista cards/tabla, y paginación.
"""

import reflex as rx

from src.presentacion_reflex.components.table_utils import header_cell_sortable
from src.presentacion_reflex.components.layout.dashboard_layout import dashboard_layout
from src.presentacion_reflex.components.propiedades.modal_form import modal_propiedad
from src.presentacion_reflex.components.propiedades.property_card import (
    tarjeta_propiedad,
)
from src.presentacion_reflex.state.auth_state import AuthState
from src.presentacion_reflex.state.propiedades_state import PropiedadesState
from src.presentacion_reflex.components.neuro_elements import (
    neuro_floating_input,
    neuro_floating_select,
    neuro_button,
    neuro_switch,
    neuro_spinner,
    neuro_badge,
    neuro_panel,
)
from src.presentacion_reflex.components.shared.advanced_filter_bar import advanced_filter_bar
from src.presentacion_reflex import styles


def render_property_actions(prop: rx.Var) -> rx.Component:
    """Renderiza los botones de acción para una propiedad con estilo neumórfico."""
    return rx.hstack(
        rx.cond(
            AuthState.check_action("Propiedades", "EDITAR"),
            rx.hstack(
                rx.tooltip(
                    neuro_button(
                        rx.icon("refresh-ccw", size=14),
                        size="1",
                        on_click=lambda: PropiedadesState.toggle_disponibilidad(
                            prop.id_propiedad,
                            rx.cond(prop.disponibilidad == 1, 0, 1),
                        ),
                        style={"min_width": "32px", "height": "32px", "padding": "0"},
                    ),
                    content="Cambiar Estado",
                ),
                rx.tooltip(
                    neuro_button(
                        rx.icon("pencil", size=14),
                        size="1",
                        on_click=lambda: PropiedadesState.open_edit_modal(
                            prop.id_propiedad
                        ),
                        style={"min_width": "32px", "height": "32px", "padding": "0"},
                    ),
                    content="Editar",
                ),
                rx.tooltip(
                    rx.cond(
                        prop.estado_registro,
                        neuro_button(
                            rx.icon("power-off", size=14),
                            size="1",
                            on_click=lambda: PropiedadesState.toggle_activa(
                                prop.id_propiedad, 1
                            ),
                            style={
                                "min_width": "32px",
                                "height": "32px",
                                "padding": "0",
                                "color": "var(--red-9)",
                            },
                        ),
                        neuro_button(
                            rx.icon("power", size=14),
                            size="1",
                            on_click=lambda: PropiedadesState.toggle_activa(
                                prop.id_propiedad, 0
                            ),
                            style={
                                "min_width": "32px",
                                "height": "32px",
                                "padding": "0",
                                "color": "var(--brand-primary)",
                            },
                        ),
                    ),
                    content=rx.cond(prop.estado_registro, "Desactivar", "Activar"),
                ),
                spacing="3",
            ),
        ),
    )


def _render_kpi_card(
    title: str, icon: str, total: int, activas: int, inactivas: int, color_scheme: str
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
                            f"{activas.to_string()} Activas",
                            color_scheme="orange",
                            size="1",
                        ),
                        neuro_badge(
                            f"{inactivas.to_string()} Inactivas",
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


def propiedades_page() -> rx.Component:
    """
    Página principal de Propiedades con filtros y CRUD.
    """

    return rx.box(
        dashboard_layout(
            rx.vstack(
                # --- Elite Header ---
                # --- Elite Header with Gradient (Personas Style) ---
                rx.box(
                    rx.flex(
                        rx.vstack(
                            rx.heading(
                                "Gestión de Propiedades",
                                size="8",
                                weight="bold",
                                color=styles.TEXT_PRIMARY,
                            ),
                            rx.text("Inventario inmobiliario", size="3"),
                            rx.hstack(
                                rx.icon("building-2", size=18, color="var(--gray-9)"),
                                rx.text(
                                    "Total: ",
                                    PropiedadesState.total_items,
                                    " propiedades",
                                    size="2",
                                    weight="medium",
                                    color=styles.TEXT_SECONDARY,
                                ),
                                spacing="2",
                                align="center",
                            ),
                            spacing="1",
                            align="start",
                        ),
                        rx.cond(
                            AuthState.check_action("Propiedades", "CREAR"),
                            rx.tooltip(
                                neuro_button(
                                    rx.hstack(
                                        rx.icon("plus", size=18),
                                        rx.text("Nueva Propiedad"),
                                        spacing="2",
                                        align="center",
                                    ),
                                    on_click=PropiedadesState.open_create_modal,
                                    size="3",
                                    variant="solid",
                                    width=["100%", "100%", "auto"],
                                    style={
                                        "background": "var(--brand-primary)",
                                        "color": "white",
                                        "padding": "0 2rem",
                                    },
                                ),
                                content="Crear nueva propiedad",
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
                    padding_bottom="2",
                    border_radius="16px",
                    style=styles.NEU_PANEL_STYLE,
                ),
                # --- KPIs ---
                rx.grid(
                    _render_kpi_card(
                        "Disponibles",
                        "home",
                        PropiedadesState.kpi_disponibles_total,
                        PropiedadesState.kpi_disponibles_activas,
                        PropiedadesState.kpi_disponibles_inactivas,
                        "orange",
                    ),
                    _render_kpi_card(
                        "Ocupadas",
                        "key",
                        PropiedadesState.kpi_ocupadas_total,
                        PropiedadesState.kpi_ocupadas_activas,
                        PropiedadesState.kpi_ocupadas_inactivas,
                        "gray",
                    ),
                    columns=rx.breakpoints(initial="1", md="2"),
                    spacing="4",
                    width="100%",
                ),
                # --- Main Content Area ---
                rx.vstack(
                    # --- Elite Toolbar ---
                    advanced_filter_bar(
                        # Tipo filter
                        rx.box(
                            rx.text("Tipo", style=styles.NEU_FILTER_LABEL_STYLE),
                            rx.select(
                                PropiedadesState.tipos_options,
                                value=PropiedadesState.filter_tipo,
                                on_change=PropiedadesState.set_filter_tipo,
                                placeholder="Tipo",
                                style=styles.NEU_FILTER_SELECT_STYLE,
                            ),
                            width=["100%", "100%", "160px"]
                        ),
                        # Disponibilidad filter
                        rx.box(
                            rx.text("Disponibilidad", style=styles.NEU_FILTER_LABEL_STYLE),
                            rx.select(
                                ["Todos", "Disponible", "Ocupada"],
                                value=PropiedadesState.filter_disponibilidad,
                                on_change=PropiedadesState.set_filter_disponibilidad,
                                placeholder="Disponibilidad",
                                style=styles.NEU_FILTER_SELECT_STYLE,
                            ),
                            width=["100%", "100%", "180px"]
                        ),
                        # Toggles
                        rx.hstack(
                            rx.text("Solo Activas", style=styles.NEU_FILTER_LABEL_STYLE, margin_bottom="0"),
                            neuro_switch(
                                checked=PropiedadesState.solo_activas,
                                on_change=PropiedadesState.toggle_solo_activas,
                                color_scheme="orange",
                            ),
                            align="center",
                            spacing="2",
                        ),
                        search_placeholder="Buscar por matrícula, dirección...",
                        on_search=PropiedadesState.set_search,
                        search_value=PropiedadesState.search_text,
                        on_key_down=PropiedadesState.handle_search_key_down,
                        on_clear=PropiedadesState.clear_filters,
                        active_filter_count=PropiedadesState.active_filter_count,
                        action_buttons=[
                            rx.tooltip(
                                rx.icon_button(
                                    rx.cond(
                                        PropiedadesState.vista_tipo == "cards",
                                        rx.icon("table", size=18),
                                        rx.icon("layout_grid", size=18),
                                    ),
                                    on_click=PropiedadesState.toggle_vista,
                                    style=styles.NEU_FILTER_ICON_BUTTON_STYLE,
                                    color_scheme="gray",
                                ),
                                content=rx.cond(
                                    PropiedadesState.vista_tipo == "cards",
                                    "Cambiar a vista de tabla",
                                    "Cambiar a vista de cards",
                                ),
                            ),
                            rx.tooltip(
                                rx.icon_button(
                                    rx.icon("file_spreadsheet", size=18),
                                    color_scheme="green",
                                    style=styles.NEU_FILTER_ICON_BUTTON_STYLE,
                                    on_click=PropiedadesState.exportar_csv,
                                ),
                                content="Exportar a Excel",
                            ),
                            rx.tooltip(
                                rx.icon_button(
                                    rx.icon("refresh_cw", size=18),
                                    style=styles.NEU_FILTER_ICON_BUTTON_STYLE,
                                    on_click=PropiedadesState.load_propiedades,
                                ),
                                content="Recargar",
                            ),
                        ]
                    ),
                    # Stats/Counter
                    rx.flex(
                        rx.text(
                            "Mostrando ",
                            PropiedadesState.propiedades.length(),
                            " de ",
                            PropiedadesState.total_items,
                            " propiedades",
                            size="2",
                            weight="medium",
                            color="var(--gray-10)",
                        ),
                        width="100%",
                        padding_x="2",
                        justify="between",
                        align="center",
                        flex_wrap="wrap",
                        gap="3",
                    ),
                    # Content Area (Grid or Table)
                    rx.cond(
                        PropiedadesState.is_loading,
                        rx.center(
                            rx.vstack(
                                neuro_spinner(size="3"),
                                rx.text(
                                    "Cargando inventario...", color="var(--gray-10)"
                                ),
                                spacing="4",
                            ),
                            height="400px",
                            width="100%",
                        ),
                        rx.box(
                            rx.cond(
                                PropiedadesState.propiedades.length() == 0,
                                rx.center(
                                    rx.vstack(
                                        rx.icon(
                                            "search-x", size=64, color="var(--gray-6)"
                                        ),
                                        rx.text(
                                            "No se encontraron propiedades",
                                            size="5",
                                            weight="bold",
                                            color="var(--gray-10)",
                                        ),
                                        rx.text(
                                            "Intenta ajustar los filtros o registra una nueva propiedad.",
                                            size="3",
                                            color="var(--gray-9)",
                                            text_align="center",
                                        ),
                                        spacing="4",
                                        align="center",
                                    ),
                                    height="400px",
                                    width="100%",
                                    border="2px dashed var(--gray-6)",
                                    border_radius="16px",
                                    background="var(--gray-2)",
                                ),
                                # Result Views
                                rx.cond(
                                    PropiedadesState.vista_tipo == "cards",
                                    # Grid View
                                    rx.grid(
                                        rx.foreach(
                                            PropiedadesState.propiedades,
                                            lambda prop: tarjeta_propiedad(
                                                id_propiedad=prop.id_propiedad,
                                                matricula=prop.matricula_inmobiliaria,
                                                direccion=prop.direccion_propiedad,
                                                tipo=prop.tipo_propiedad,
                                                municipio=prop.municipio_nombre,
                                                disponibilidad=prop.disponibilidad,
                                                valor_canon=prop.valor_canon,
                                                valor_canon_view=prop.valor_canon_view,
                                                area_metros=prop.area_metros,
                                                area_metros_view=prop.area_metros_view,
                                                habitaciones=prop.habitaciones,
                                                banos=prop.banos,
                                                parqueadero=prop.parqueadero,
                                                valor_venta=prop.valor_venta,
                                                valor_venta_view=prop.valor_venta_view,
                                                comision_venta=prop.comision_venta,
                                                comision_venta_valor_view=prop.comision_venta_valor_view,
                                                codigo_energia=prop.codigo_energia,
                                                codigo_agua=prop.codigo_agua,
                                                codigo_gas=prop.codigo_gas,
                                                imagen_id=prop.imagen_id,
                                                estado_registro=prop.estado_registro,
                                                on_edit=PropiedadesState.open_edit_modal,
                                                on_toggle_disponibilidad=PropiedadesState.toggle_disponibilidad,
                                                on_toggle_activa=PropiedadesState.toggle_activa,
                                            ),
                                        ),
                                        columns=rx.breakpoints(
                                            initial="1", sm="2", lg="3"
                                        ),
                                        gap="3rem",
                                        width="100%",
                                    ),
                                    # Table View (Premium)
                                    rx.box(
                                        rx.table.root(
                                            rx.table.header(
                                                rx.table.row(
                                                    header_cell_sortable(
                                                        "Propiedad",
                                                        "direccion",
                                                        PropiedadesState.sort_by,
                                                        PropiedadesState.sort_order,
                                                        PropiedadesState.toggle_sort,
                                                    ),
                                                    header_cell_sortable(
                                                        "Tipo",
                                                        "tipo",
                                                        PropiedadesState.sort_by,
                                                        PropiedadesState.sort_order,
                                                        PropiedadesState.toggle_sort,
                                                    ),
                                                    header_cell_sortable(
                                                        "Municipio",
                                                        "ciudad",
                                                        PropiedadesState.sort_by,
                                                        PropiedadesState.sort_order,
                                                        PropiedadesState.toggle_sort,
                                                    ),
                                                    header_cell_sortable(
                                                        "Estado",
                                                        "disponibilidad",
                                                        PropiedadesState.sort_by,
                                                        PropiedadesState.sort_order,
                                                        PropiedadesState.toggle_sort,
                                                    ),
                                                    header_cell_sortable(
                                                        "Canon",
                                                        "canon_estimado",
                                                        PropiedadesState.sort_by,
                                                        PropiedadesState.sort_order,
                                                        PropiedadesState.toggle_sort,
                                                    ),
                                                    header_cell_sortable(
                                                        "Venta / Comisión",
                                                        "valor_venta",
                                                        PropiedadesState.sort_by,
                                                        PropiedadesState.sort_order,
                                                        PropiedadesState.toggle_sort,
                                                    ),
                                                    rx.table.column_header_cell(
                                                        "Servicios"
                                                    ),
                                                    rx.table.column_header_cell(
                                                        "Acciones"
                                                    ),
                                                ),
                                            ),
                                            rx.table.body(
                                                rx.foreach(
                                                    PropiedadesState.propiedades,
                                                    lambda prop: rx.table.row(
                                                        rx.table.cell(
                                                            rx.hstack(
                                                                rx.box(
                                                                    rx.icon(
                                                                        "home",
                                                                        size=20,
                                                                        color=styles.ACCENT_COLOR,
                                                                    ),
                                                                    padding="8px",
                                                                    background=styles.ACCENT_BG_SOFT,
                                                                    border_radius="8px",
                                                                ),
                                                                rx.vstack(
                                                                    rx.text(
                                                                        prop.direccion_propiedad,
                                                                        weight="bold",
                                                                        size="2",
                                                                    ),
                                                                    rx.text(
                                                                        prop.matricula_inmobiliaria,
                                                                        size="1",
                                                                        color=styles.TEXT_TERTIARY,
                                                                    ),
                                                                    spacing="1",
                                                                ),
                                                                spacing="3",
                                                                align="center",
                                                            )
                                                        ),
                                                        rx.table.cell(
                                                            neuro_badge(  # Converted to neuro_badge
                                                                prop.tipo_propiedad,
                                                                color_scheme="orange",
                                                            )
                                                        ),
                                                        rx.table.cell(
                                                            prop.municipio_nombre
                                                        ),
                                                        rx.table.cell(
                                                            rx.cond(
                                                                prop.disponibilidad,
                                                                neuro_badge(
                                                                    "Disponible",
                                                                    color_scheme="orange",
                                                                ),  # Converted to neuro_badge
                                                                neuro_badge(
                                                                    "Ocupada",
                                                                    color_scheme="gray",
                                                                ),  # Converted to neuro_badge
                                                            )
                                                        ),
                                                        rx.table.cell(
                                                            rx.text(
                                                                prop.valor_canon_view,
                                                                weight="bold",
                                                                style={
                                                                    "font_variant_numeric": "tabular-nums"
                                                                },
                                                            )
                                                        ),
                                                        rx.table.cell(
                                                            rx.vstack(
                                                                rx.text(
                                                                    prop.valor_venta_view,
                                                                    weight="bold",
                                                                    size="2",
                                                                    style={
                                                                        "font_variant_numeric": "tabular-nums"
                                                                    },
                                                                ),
                                                                rx.text(
                                                                    "(",
                                                                    prop.comision_venta_valor_view,
                                                                    ")",
                                                                    size="1",
                                                                    color=styles.TEXT_TERTIARY,
                                                                    style={
                                                                        "font_variant_numeric": "tabular-nums"
                                                                    },
                                                                ),
                                                                spacing="0",
                                                                align="start",
                                                            )
                                                        ),
                                                        rx.table.cell(
                                                            rx.hstack(
                                                                rx.cond(
                                                                    prop.codigo_energia
                                                                    != "",
                                                                    rx.tooltip(
                                                                        rx.icon(
                                                                            "zap",
                                                                            size=14,
                                                                            color="var(--yellow-9)",
                                                                        ),
                                                                        content=prop.energia_tooltip,
                                                                    ),
                                                                ),
                                                                rx.cond(
                                                                    prop.codigo_agua
                                                                    != "",
                                                                    rx.tooltip(
                                                                        rx.icon(
                                                                            "droplet",
                                                                            size=14,
                                                                            color="var(--brand-primary)",
                                                                        ),
                                                                        content=prop.agua_tooltip,
                                                                    ),
                                                                ),
                                                                rx.cond(
                                                                    prop.codigo_gas
                                                                    != "",
                                                                    rx.tooltip(
                                                                        rx.icon(
                                                                            "flame",
                                                                            size=14,
                                                                            color="var(--orange-9)",
                                                                        ),
                                                                        content=prop.gas_tooltip,
                                                                    ),
                                                                ),
                                                                spacing="2",
                                                            )
                                                        ),
                                                        rx.table.cell(
                                                            render_property_actions(
                                                                prop
                                                            )
                                                        ),
                                                    ),
                                                ),
                                            ),
                                            variant="surface",
                                            width="100%",
                                        ),
                                        style={
                                            **styles.NEU_PANEL_STYLE,
                                            "padding": "0",
                                            "overflow": "hidden",
                                        },
                                        width="100%",
                                    ),
                                ),
                            ),
                            width="100%",
                        ),
                    ),
                    # --- Premium Pagination ---
                    rx.box(
                        rx.hstack(
                            neuro_button(
                                rx.icon("chevron-left", size=16),
                                rx.text(
                                    "Anterior",
                                    display=rx.breakpoints(initial="none", md="block"),
                                ),
                                on_click=PropiedadesState.prev_page,
                                disabled=PropiedadesState.current_page == 1,
                                size="3",
                            ),
                            rx.vstack(
                                rx.text(
                                    "Página ",
                                    PropiedadesState.current_page,
                                    size=rx.breakpoints(initial="2", md="3"),
                                    weight="medium",
                                    color=styles.TEXT_PRIMARY,
                                ),
                                rx.text(
                                    "Mostrando ",
                                    (PropiedadesState.current_page - 1)
                                    * PropiedadesState.page_size
                                    + 1,
                                    " - ",
                                    rx.cond(
                                        PropiedadesState.current_page
                                        * PropiedadesState.page_size
                                        > PropiedadesState.total_items,
                                        PropiedadesState.total_items,
                                        PropiedadesState.current_page
                                        * PropiedadesState.page_size,
                                    ),
                                    " de ",
                                    PropiedadesState.total_items,
                                    size="1",
                                    color=styles.TEXT_SECONDARY,
                                    display=rx.breakpoints(initial="none", md="block"),
                                ),
                                spacing="0",
                                align="center",
                            ),
                            neuro_button(
                                rx.text(
                                    "Siguiente",
                                    display=rx.breakpoints(initial="none", md="block"),
                                ),
                                rx.icon("chevron-right", size=16),
                                on_click=PropiedadesState.next_page,
                                disabled=(
                                    PropiedadesState.current_page
                                    * PropiedadesState.page_size
                                )
                                >= PropiedadesState.total_items,
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
                            **styles.NEU_PANEL_STYLE,
                            "margin_top": "24px",
                            "border": "none",
                        },
                    ),
                    spacing="6",
                    width="100%",
                    padding_x=["4", "6"],
                    padding_bottom="8",
                ),
                # Modal
                modal_propiedad(),
                spacing="0",
                width="100%",
            )
        ),
    )


# Ruta protegida
@rx.page(
    route="/propiedades", on_load=[AuthState.require_login, PropiedadesState.on_load]
)
def propiedades():
    return propiedades_page()
