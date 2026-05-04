import reflex as rx

from src.presentacion_reflex.components.layout.dashboard_layout import dashboard_layout
from src.presentacion_reflex.state.auth_state import AuthState
from src.presentacion_reflex.state.liquidacion_asesores_state import (
    LiquidacionAsesoresState,
)
from src.presentacion_reflex.state.pdf_state import PDFState
from src.presentacion_reflex.components.neuro_elements import (
    neuro_input,
    neuro_button,
    neuro_select_root,
)
from src.presentacion_reflex.components.tablas import header_cell_sortable
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
                rx.hstack(
                    neuro_button(
                        rx.hstack(rx.icon("refresh-cw", size=18), rx.text("Recargar")),
                        on_click=LiquidacionAsesoresState.load_liquidaciones,
                        size="3",
                    ),
                    rx.cond(
                        AuthState.check_action("Liquidaciones Asesores", "LIQUIDAR"),
                        neuro_button(
                            rx.hstack(rx.icon("plus"), rx.text("Nueva Liquidación")),
                            on_click=LiquidacionAsesoresState.open_create_modal,
                            color_scheme="green",
                            size="3",
                        ),
                    ),
                    spacing="3",
                    width=rx.breakpoints(initial="100%", md="auto"),
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
        rx.card(
            rx.flex(
                neuro_input(
                    rx.input.slot(rx.icon("search", size=18)),
                    placeholder="Buscar asesor o contrato...",
                    value=LiquidacionAsesoresState.search_text,
                    on_change=LiquidacionAsesoresState.set_search,
                    width=rx.breakpoints(initial="100%", md="350px"),
                    size="3",
                ),
                neuro_select_root(
                    rx.foreach(
                        LiquidacionAsesoresState.periodo_options,
                        lambda opt: rx.select.item(opt, value=opt),
                    ),
                    value=LiquidacionAsesoresState.filter_periodo,
                    on_change=LiquidacionAsesoresState.set_filter_periodo,
                    placeholder="Período",
                    width=rx.breakpoints(initial="100%", md="150px"),
                ),
                rx.cond(
                    AuthState.check_action("Liquidaciones Asesores", "LIQUIDAR"),
                    neuro_button(
                        rx.hstack(
                            rx.icon("calculator"), rx.text("Generar Masivamente")
                        ),
                        on_click=LiquidacionAsesoresState.open_bulk_modal,
                        color_scheme="blue",
                        width=rx.breakpoints(initial="100%", md="auto"),
                    ),
                ),
                gap="3",
                width="100%",
                align=rx.breakpoints(initial="stretch", md="center"),
                flex_direction=rx.breakpoints(initial="column", md="row"),
                flex_wrap="wrap",
            ),
            width="100%",
            style={
                "background": styles.BG_PANEL,
                "box_shadow": styles.NEU_SHADOW,
                "border": "none",
                "border_radius": "16px",
                "padding": "1.2rem",
            },
        ),
        # Table
        rx.cond(
            LiquidacionAsesoresState.is_loading,
            rx.center(rx.spinner(size="3"), height="300px", width="100%"),
            rx.card(
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            header_cell_sortable(
                                "Asesor",
                                "nombre_asesor",
                                LiquidacionAsesoresState.sort_by,
                                LiquidacionAsesoresState.sort_order,
                                LiquidacionAsesoresState.toggle_sort,
                            ),
                            header_cell_sortable(
                                "Período",
                                "periodo_liquidacion",
                                LiquidacionAsesoresState.sort_by,
                                LiquidacionAsesoresState.sort_order,
                                LiquidacionAsesoresState.toggle_sort,
                            ),
                            header_cell_sortable(
                                "Estado",
                                "estado_liquidacion",
                                LiquidacionAsesoresState.sort_by,
                                LiquidacionAsesoresState.sort_order,
                                LiquidacionAsesoresState.toggle_sort,
                            ),
                            header_cell_sortable(
                                "Comisión Bruta",
                                "comision_bruta",
                                LiquidacionAsesoresState.sort_by,
                                LiquidacionAsesoresState.sort_order,
                                LiquidacionAsesoresState.toggle_sort,
                            ),
                            rx.table.column_header_cell("Descuentos"),
                            rx.table.column_header_cell("Bonificaciones"),
                            header_cell_sortable(
                                "Neto",
                                "valor_neto_asesor",
                                LiquidacionAsesoresState.sort_by,
                                LiquidacionAsesoresState.sort_order,
                                LiquidacionAsesoresState.toggle_sort,
                            ),
                            rx.table.column_header_cell("Acciones"),
                        )
                    ),
                    rx.table.body(
                        rx.foreach(
                            LiquidacionAsesoresState.liquidaciones,
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
                                                        LiquidacionAsesoresState.open_edit_modal(
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
                                                        LiquidacionAsesoresState.aprobar_liquidacion(
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
                    on_click=LiquidacionAsesoresState.prev_page,
                    disabled=LiquidacionAsesoresState.current_page == 1,
                    size="3",
                ),
                rx.vstack(
                    rx.text(
                        "Página ",
                        LiquidacionAsesoresState.current_page,
                        size=rx.breakpoints(initial="2", md="3"),
                        weight="medium",
                        color=styles.TEXT_PRIMARY,
                    ),
                    rx.text(
                        "Mostrando ",
                        (LiquidacionAsesoresState.current_page - 1)
                        * LiquidacionAsesoresState.page_size
                        + 1,
                        "-",
                        rx.cond(
                            LiquidacionAsesoresState.current_page
                            * LiquidacionAsesoresState.page_size
                            > LiquidacionAsesoresState.total_items,
                            LiquidacionAsesoresState.total_items,
                            LiquidacionAsesoresState.current_page
                            * LiquidacionAsesoresState.page_size,
                        ),
                        " de ",
                        LiquidacionAsesoresState.total_items,
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
                    on_click=LiquidacionAsesoresState.next_page,
                    disabled=LiquidacionAsesoresState.current_page
                    * LiquidacionAsesoresState.page_size
                    >= LiquidacionAsesoresState.total_items,
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
            is_open=LiquidacionAsesoresState.show_bulk_modal,
            on_open_change=LiquidacionAsesoresState.set_show_bulk_modal,
            form_data=LiquidacionAsesoresState.form_data,
            on_submit=LiquidacionAsesoresState.generar_liquidacion_masiva,
            is_loading=LiquidacionAsesoresState.is_loading,
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
