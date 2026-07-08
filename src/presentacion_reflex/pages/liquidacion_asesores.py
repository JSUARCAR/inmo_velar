import reflex as rx

from src.presentacion_reflex.components.layout.dashboard_layout import dashboard_layout
from src.presentacion_reflex.state.auth_state import AuthState
from src.presentacion_reflex.state.liquidacion_asesores_state import (
    LiquidacionAsesoresState,
)
from src.presentacion_reflex.state.liquidacion_asesores.filtros_state import (
    LiquidacionFiltrosState,
)
from src.presentacion_reflex.state.liquidacion_asesores.grid_state import (
    LiquidacionGridState,
)
from src.presentacion_reflex.state.liquidacion_asesores.form_state import (
    LiquidacionFormState,
)
from src.presentacion_reflex.state.pdf_state import PDFState
from src.presentacion_reflex.components.neuro_elements import (
    neuro_floating_input,
    neuro_floating_select,
    neuro_button,
)
from src.presentacion_reflex.components.tablas import header_cell_sortable
from src.presentacion_reflex.components.shared.advanced_filter_bar import advanced_filter_bar
from src.presentacion_reflex import styles

# Importar modales
from src.presentacion_reflex.components.liquidacion_asesores.modal_form import (
    modal_form,
)
from src.presentacion_reflex.components.liquidacion_asesores.bulk_modal_form import (
    bulk_modal_form,
)
from src.presentacion_reflex.components.liquidacion_asesores.detail_modal import (
    detail_modal,
)
from src.presentacion_reflex.components.liquidacion_asesores.annul_modal import (
    annul_modal,
)
from src.presentacion_reflex.components.liquidacion_asesores.discount_modal import (
    discount_modal,
)


def liquidacion_asesores_content() -> rx.Component:
    return rx.vstack(
        # Header
        rx.box(
            rx.flex(
                rx.vstack(
                    rx.heading(
                        "Liquidaciones de Asesores",
                        size="8",
                        weight="bold",
                        color=styles.TEXT_PRIMARY,
                    ),
                    rx.text(
                        "Cálculo de comisiones y bonificaciones para el equipo comercial",
                        size="3",
                    ),
                    spacing="1",
                    align="start",
                ),
                rx.cond(
                    LiquidacionGridState.error_message != "",
                    rx.callout(
                        LiquidacionGridState.error_message,
                        icon="circle-alert",
                        color_scheme="red",
                        role="alert",
                        width="100%",
                        margin_bottom="1rem",
                    ),
                ),
                rx.cond(
                    LiquidacionFormState.error_message != "",
                    rx.callout(
                        LiquidacionFormState.error_message,
                        icon="triangle-alert",
                        color_scheme="red",
                        role="alert",
                        width="100%",
                        margin_bottom="1rem",
                    ),
                ),
                width="100%",
                padding="5",
                justify="between",
                align=rx.breakpoints(initial="start", md="center"),
                flex_direction=rx.breakpoints(initial="column", md="row"),
                flex_wrap="wrap",
                gap="4",
            ),
            width="100%",
            padding_bottom="2",
            border_radius="12px",
            margin_bottom="1.5rem",
            style={
                "background": "linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%)",
                "backdrop_filter": "blur(10px)",
            },
        ),
        # Toolbar
        advanced_filter_bar(
            # Período filter
            rx.box(
                rx.text("Período", style=styles.NEU_FILTER_LABEL_STYLE),
                rx.select(
                    LiquidacionFiltrosState.periodo_options,
                    value=LiquidacionFiltrosState.filter_periodo,
                    on_change=LiquidacionFiltrosState.set_filter_periodo,
                    placeholder="Período",
                    style=styles.NEU_FILTER_SELECT_STYLE,
                ),
                width=["100%", "100%", "150px"]
            ),
            # Estado filter (exposed)
            rx.box(
                rx.text("Estado", style=styles.NEU_FILTER_LABEL_STYLE),
                rx.select(
                    LiquidacionFiltrosState.estado_options,
                    value=LiquidacionFiltrosState.filter_estado,
                    on_change=LiquidacionFiltrosState.set_filter_estado,
                    placeholder="Estado",
                    style=styles.NEU_FILTER_SELECT_STYLE,
                ),
                width=["100%", "100%", "150px"]
            ),
            search_placeholder="Buscar asesor o contrato...",
            on_search=LiquidacionFiltrosState.set_search,
            search_value=LiquidacionFiltrosState.search_text,
            on_clear=LiquidacionFiltrosState.clear_filters,
            active_filter_count=LiquidacionFiltrosState.active_filter_count,
            action_buttons=[
                # Bulk Generate
                rx.cond(
                    AuthState.check_action("Liquidaciones Asesores", "LIQUIDAR"),
                    rx.tooltip(
                        rx.icon_button(
                            rx.icon("calculator", size=18),
                            color_scheme="blue",
                            style=styles.NEU_FILTER_ICON_BUTTON_STYLE,
                            on_click=LiquidacionFormState.open_bulk_modal,
                        ),
                        content="Generar Masivamente",
                    ),
                ),
                # New Liquidacion
                rx.cond(
                    AuthState.check_action("Liquidaciones Asesores", "LIQUIDAR"),
                    rx.tooltip(
                        rx.icon_button(
                            rx.icon("plus", size=18),
                            color_scheme="green",
                            style=styles.NEU_FILTER_ICON_BUTTON_STYLE,
                            on_click=LiquidacionFormState.open_create_modal,
                        ),
                        content="Nueva Liquidación",
                    ),
                ),
                # Refresh
                rx.tooltip(
                    rx.icon_button(
                        rx.icon("refresh_cw", size=18),
                        style=styles.NEU_FILTER_ICON_BUTTON_STYLE,
                        on_click=LiquidacionGridState.load_liquidaciones,
                    ),
                    content="Recargar",
                ),
            ]
        ),
        # Table
        rx.cond(
            LiquidacionGridState.is_loading,
            rx.center(rx.spinner(size="3"), height="300px", width="100%"),
            rx.card(
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            header_cell_sortable(
                                "Asesor",
                                "nombre_asesor",
                                LiquidacionGridState.sort_by,
                                LiquidacionGridState.sort_order,
                                LiquidacionGridState.toggle_sort,
                            ),
                            header_cell_sortable(
                                "Período",
                                "periodo_liquidacion",
                                LiquidacionGridState.sort_by,
                                LiquidacionGridState.sort_order,
                                LiquidacionGridState.toggle_sort,
                            ),
                            header_cell_sortable(
                                "Estado",
                                "estado_liquidacion",
                                LiquidacionGridState.sort_by,
                                LiquidacionGridState.sort_order,
                                LiquidacionGridState.toggle_sort,
                            ),
                            header_cell_sortable(
                                "Comisión Bruta",
                                "comision_bruta",
                                LiquidacionGridState.sort_by,
                                LiquidacionGridState.sort_order,
                                LiquidacionGridState.toggle_sort,
                            ),
                            rx.table.column_header_cell("Descuentos"),
                            rx.table.column_header_cell("Bonificaciones"),
                            header_cell_sortable(
                                "Neto",
                                "valor_neto_asesor",
                                LiquidacionGridState.sort_by,
                                LiquidacionGridState.sort_order,
                                LiquidacionGridState.toggle_sort,
                            ),
                            rx.table.column_header_cell("Acciones"),
                        )
                    ),
                    rx.table.body(
                        rx.foreach(
                            LiquidacionGridState.liquidaciones,
                            lambda liq: rx.table.row(
                                rx.table.cell(liq["asesor"]),
                                rx.table.cell(liq["periodo"]),
                                rx.table.cell(
                                    rx.badge(
                                        liq["estado"],
                                        variant="soft",
                                        color_scheme=rx.match(
                                            liq["estado"],
                                            ("Pendiente", "amber"),
                                            ("Aprobada", "blue"),
                                            ("Pagada", "green"),
                                            ("Anulada", "red"),
                                            "gray",
                                        ),
                                    )
                                ),
                                rx.table.cell(
                                    rx.text(liq["comision_bruta_view"], weight="bold")
                                ),
                                rx.table.cell(
                                    rx.text(liq["total_descuentos_view"], color="red")
                                ),
                                rx.table.cell(
                                    rx.text(
                                        liq["total_bonificaciones_view"], color="blue"
                                    )
                                ),
                                rx.table.cell(
                                    rx.text(
                                        liq["valor_neto_view"],
                                        weight="bold",
                                        color="green",
                                    )
                                ),
                                rx.table.cell(
                                    rx.hstack(
                                        rx.tooltip(
                                            rx.icon_button(
                                                rx.icon("eye", size=16),
                                                variant="ghost",
                                                on_click=lambda: (
                                                    LiquidacionAsesoresState.open_detail_modal(
                                                        liq["id_liquidacion"]
                                                    )
                                                ),
                                            ),
                                            content="Ver Detalles",
                                        ),
                                        rx.cond(
                                            liq["estado"] != "Anulada",
                                            rx.tooltip(
                                                rx.icon_button(
                                                    rx.icon("file-text", size=16),
                                                    variant="ghost",
                                                    color_scheme="blue",
                                                    on_click=lambda: (
                                                        PDFState.generar_liquidacion_asesor_pdf(
                                                            liq["id_liquidacion"]
                                                        )
                                                    ),
                                                ),
                                                content="Descargar PDF",
                                            ),
                                        ),
                                        rx.cond(
                                            liq["estado"] == "Pendiente",
                                            rx.tooltip(
                                                rx.icon_button(
                                                    rx.icon("pencil", size=16),
                                                    variant="ghost",
                                                    on_click=lambda: (
                                                        LiquidacionFormState.open_edit_modal(
                                                            liq["id_liquidacion"]
                                                        )
                                                    ),
                                                ),
                                                content="Editar",
                                            ),
                                        ),
                                        rx.cond(
                                            liq["estado"] == "Pendiente",
                                            rx.tooltip(
                                                rx.icon_button(
                                                    rx.icon("check", size=18),
                                                    variant="ghost",
                                                    color="#51cf66",
                                                    on_click=lambda: (
                                                        LiquidacionFormState.aprobar_liquidacion(
                                                            liq["id_liquidacion"]
                                                        )
                                                    ),
                                                ),
                                                content="Aprobar Liquidación",
                                            ),
                                        ),
                                        spacing="2",
                                    )
                                ),
                            ),
                        )
                    ),
                    width="100%",
                    variant="surface",
                ),
                width="100%",
                style={"padding": "0"},
            ),
        ),
        # Pagination
        rx.card(
            rx.hstack(
                neuro_button(
                    rx.icon("chevron-left", size=16),
                    rx.text(
                        "Anterior", display=rx.breakpoints(initial="none", md="block")
                    ),
                    on_click=LiquidacionGridState.prev_page,
                    disabled=LiquidacionGridState.current_page == 1,
                    size="3",
                ),
                rx.vstack(
                    rx.text(
                        "Página ",
                        LiquidacionGridState.current_page,
                        size=rx.breakpoints(initial="2", md="3"),
                        weight="medium",
                        color=styles.TEXT_PRIMARY,
                    ),
                    rx.text(
                        "Mostrando ",
                        (LiquidacionGridState.current_page - 1)
                        * LiquidacionGridState.page_size
                        + 1,
                        "-",
                        rx.cond(
                            LiquidacionGridState.current_page
                            * LiquidacionGridState.page_size
                            > LiquidacionGridState.total_items,
                            LiquidacionGridState.total_items,
                            LiquidacionGridState.current_page
                            * LiquidacionGridState.page_size,
                        ),
                        " de ",
                        LiquidacionGridState.total_items,
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
                    on_click=LiquidacionGridState.next_page,
                    disabled=LiquidacionGridState.current_page
                    * LiquidacionGridState.page_size
                    >= LiquidacionGridState.total_items,
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
        ),
        # Modales
        modal_form(),
        bulk_modal_form(
            is_open=LiquidacionFormState.show_bulk_modal,
            on_open_change=LiquidacionFormState.set_show_bulk_modal,
            form_data=LiquidacionFormState.form_data,
            on_submit=LiquidacionFormState.generar_liquidacion_masiva,
            is_loading=LiquidacionGridState.is_loading,
        ),
        detail_modal(),
        annul_modal(),
        discount_modal(),
        spacing="4",
        width="100%",
        padding="2em",
    )


@rx.page(
    route="/liquidacion-asesores",
    title="Liquidaciones de Asesores | Inmobiliaria Velar",
    on_load=[AuthState.require_login, LiquidacionAsesoresState.on_load],
)
def liquidacion_asesores_page() -> rx.Component:
    """Página de liquidaciones de asesores con layout."""
    return dashboard_layout(liquidacion_asesores_content())
