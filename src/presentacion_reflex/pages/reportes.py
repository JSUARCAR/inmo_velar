import reflex as rx
from src.presentacion_reflex.components.layout.dashboard_layout import dashboard_layout
from src.presentacion_reflex.components.neuro_elements import (
    neuro_floating_input,
    neuro_floating_select,
    neuro_button,
    neuro_icon_action_button,
)
from src.presentacion_reflex.state.reportes_state import ReportesState, ReportItem
from src.presentacion_reflex import styles


def report_item_sidebar(report: ReportItem, is_selected: bool):
    """Item individual del sidebar de reportes."""
    return rx.hstack(
        rx.icon("file-text", size=16, color=rx.cond(is_selected, "#2563eb", "#64748b")),
        rx.text(
            report.name,
            size="2",
            weight=rx.cond(is_selected, "bold", "medium"),
            color=rx.cond(is_selected, "#1e293b", "#64748b"),
        ),
        spacing="2",
        padding="2",
        border_radius="8px",
        background=rx.cond(is_selected, "rgba(37, 99, 235, 0.1)", "transparent"),
        cursor="pointer",
        _hover={"background": "rgba(37, 99, 235, 0.05)"},
        # report.id access
        on_click=lambda: ReportesState.select_report(report.id),
        width="100%",
        align_items="center",
    )


def reports_sidebar():
    """Sidebar de navegación interna de reportes."""
    return rx.vstack(
        neuro_floating_input(
            label="Buscar reportes...",
            value="",
            on_change=ReportesState.set_search_query,
        ),
        rx.divider(margin_y="2"),
        rx.accordion.root(
            rx.foreach(
                ReportesState.filtered_grouped_reports,
                lambda category: rx.accordion.item(
                    header=rx.hstack(
                        rx.icon(category.icon, size=16, color=category.color),
                        rx.text(
                            category.name, size="2", weight="bold", color=category.color
                        ),
                        spacing="2",
                        align_items="center",
                        width="100%",
                    ),
                    content=rx.vstack(
                        rx.foreach(
                            category.reports,
                            lambda report: report_item_sidebar(
                                report, report.id == ReportesState.selected_report_id
                            ),
                        ),
                        spacing="1",
                        padding_left="2",
                        width="100%",
                        padding_top="2",
                    ),
                ),
            ),
            type="multiple",
            collapsible=True,
            width="100%",
            variant="ghost",
        ),
        width="100%",
        height="100%",
        padding="4",
        border_right=f"1px solid {styles.BORDER_DEFAULT}",
        background_color=styles.BG_PANEL,
    )


def reports_content():
    """Área principal con filtros y tabla."""
    return rx.vstack(
        # Header + Filtros
        rx.vstack(
            rx.heading(
                ReportesState.active_report["name"],
                size="6",
                color=styles.TEXT_PRIMARY,
            ),
            rx.text(
                ReportesState.active_report["description"], size="2", color="#64748b"
            ),
            rx.hstack(
                # Filtros Rápidos (Reporte General)
                rx.cond(
                    ReportesState.selected_report_id == "reporte_consolidado",
                    rx.hstack(
                        neuro_floating_input(
                            label="Fecha pago inicio (YYYY-MM-DD)",
                            value=ReportesState.filter_fecha_pago_inicio,
                            on_change=lambda v: ReportesState.set_filter_fecha_pago(
                                v, ReportesState.filter_fecha_pago_fin
                            ),
                            width="180px",
                            debounce_time=500,
                        ),
                        neuro_floating_input(
                            label="Fecha pago fin (YYYY-MM-DD)",
                            value=ReportesState.filter_fecha_pago_fin,
                            on_change=lambda v: ReportesState.set_filter_fecha_pago(
                                ReportesState.filter_fecha_pago_inicio, v
                            ),
                            width="180px",
                            debounce_time=500,
                        ),
                        neuro_floating_select(
                            label="Estado contrato",
                            options=rx.foreach(
                                ReportesState.estado_contrato_options,
                                lambda opt: rx.select.item(opt, value=opt),
                            ),
                            value=ReportesState.filter_estado_contrato,
                            on_change=ReportesState.set_filter_estado_contrato,
                            placeholder="Estado contrato",
                            width="140px",
                        ),
                        neuro_floating_select(
                            label="Estado liquidación",
                            options=rx.foreach(
                                ReportesState.estado_liquidacion_options,
                                lambda opt: rx.select.item(opt, value=opt),
                            ),
                            value=ReportesState.filter_estado_liquidacion,
                            on_change=ReportesState.set_filter_estado_liquidacion,
                            placeholder="Estado liquidación",
                            width="140px",
                        ),
                        neuro_floating_select(
                            label="Asesor",
                            options=rx.foreach(
                                ReportesState.asesor_options,
                                lambda opt: rx.select.item(opt, value=opt),
                            ),
                            value=ReportesState.filter_asesor_id,
                            on_change=ReportesState.set_filter_asesor,
                            placeholder="Asesor",
                            width="180px",
                        ),
                        neuro_floating_input(
                            label="Propietario...",
                            value=ReportesState.filter_propietario_buscar,
                            on_change=ReportesState.set_filter_propietario,
                            width="180px",
                            debounce_time=500,
                        ),
                        spacing="2",
                    ),
                    rx.hstack(
                        neuro_floating_select(
                            label="Estado",
                            options=rx.foreach(
                                ReportesState.estado_options,
                                lambda opt: rx.select.item(opt, value=opt),
                            ),
                            value=ReportesState.filter_estado,
                            on_change=ReportesState.set_filter_activo,
                            placeholder="Estado",
                            width="150px",
                        ),
                        rx.cond(
                            ReportesState.selected_report_id == "liquidaciones",
                            neuro_floating_select(
                                label="Asesor",
                                options=rx.foreach(
                                    ReportesState.asesor_options,
                                    lambda opt: rx.select.item(opt, value=opt),
                                ),
                                value=ReportesState.filter_asesor_id,
                                on_change=ReportesState.set_filter_asesor,
                                placeholder="Asesor",
                                width="200px",
                            ),
                        ),
                        rx.cond(
                            ReportesState.selected_report_id == "recaudos",
                            rx.hstack(
                                neuro_floating_select(
                                    label="Estado Recaudo",
                                    options=rx.foreach(
                                        ReportesState.estado_recaudo_options,
                                        lambda opt: rx.select.item(opt, value=opt),
                                    ),
                                    value=ReportesState.filter_estado_recaudo,
                                    on_change=ReportesState.set_filter_estado_recaudo,
                                    placeholder="Estado Recaudo",
                                    width="160px",
                                ),
                                neuro_floating_select(
                                    label="Método Pago",
                                    options=rx.foreach(
                                        ReportesState.metodo_pago_options,
                                        lambda opt: rx.select.item(opt, value=opt),
                                    ),
                                    value=ReportesState.filter_metodo_pago,
                                    on_change=ReportesState.set_filter_metodo_pago,
                                    placeholder="Método Pago",
                                    width="160px",
                                ),
                                neuro_floating_input(
                                    label="Periodo inicio (YYYY-MM)",
                                    value=ReportesState.filter_periodo_inicio,
                                    on_change=lambda v: ReportesState.set_filter_periodo(
                                        v, ReportesState.filter_periodo_fin
                                    ),
                                    width="180px",
                                    debounce_time=500,
                                ),
                                neuro_floating_input(
                                    label="Periodo fin (YYYY-MM)",
                                    value=ReportesState.filter_periodo_fin,
                                    on_change=lambda v: ReportesState.set_filter_periodo(
                                        ReportesState.filter_periodo_inicio, v
                                    ),
                                    width="180px",
                                    debounce_time=500,
                                ),
                                spacing="2",
                            ),
                        ),
                        spacing="2",
                    ),
                ),
                neuro_floating_input(
                    label="Filtrar en tabla...",
                    value=ReportesState.filter_busqueda_tabla,
                    on_change=ReportesState.set_filter_busqueda,
                    width="250px",
                    debounce_time=500,
                ),
                rx.spacer(),
                neuro_button(
                    rx.icon("download", size=18),
                    "Exportar CSV",
                    tooltip_content="Exportar datos a CSV",
                    on_click=ReportesState.download_csv,
                    variant="solid",
                    color_scheme="green",
                ),
                width="100%",
                margin_top="4",
                align_items="center",
            ),
            width="100%",
            padding_bottom="4",
            border_bottom="1px solid #e5e7eb",
        ),
        # Mensaje de Error
        rx.cond(
            ReportesState.error_message != "",
            rx.callout(
                ReportesState.error_message,
                icon="triangle-alert",
                color_scheme="red",
                width="100%",
                margin_y="2",
            ),
        ),
        # Tabla de Previsualización
        rx.cond(
            ReportesState.is_loading,
            rx.center(rx.spinner(), padding="4", width="100%"),
            rx.box(
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.foreach(
                                ReportesState.preview_headers,
                                lambda h: rx.table.column_header_cell(h),
                            )
                        )
                    ),
                    rx.table.body(
                        rx.foreach(
                            ReportesState.preview_data,
                            lambda row: rx.table.row(
                                rx.foreach(
                                    ReportesState.preview_headers,
                                    lambda h: rx.table.cell(row[h]),
                                )
                            ),
                        )
                    ),
                    variant="surface",
                    size="1",
                    width="100%",
                ),
                width="100%",
                overflow_x="auto",
            ),
        ),
        # Paginación (Preview)
        rx.hstack(
            rx.text(
                "Mostrando ",
                ReportesState.preview_data.length(),
                " registros (Total: ",
                ReportesState.total_records,
                ") - Previsualización limitada",
                size="1",
                color="#64748b",
            ),
            rx.spacer(),
            neuro_button(
                "Anterior",
                tooltip_content="Página anterior",
                on_click=ReportesState.prev_page,
                disabled=ReportesState.current_page <= 1,
                size="1",
                variant="soft",
            ),
            rx.text("Página ", ReportesState.current_page, size="1"),
            neuro_button(
                "Siguiente",
                tooltip_content="Página siguiente",
                on_click=ReportesState.next_page,
                disabled=(ReportesState.current_page * ReportesState.page_size)
                >= ReportesState.total_records,
                size="1",
                variant="soft",
            ),
            width="100%",
            padding_top="4",
            align_items="center",
        ),
        padding="6",
        flex="1",
        width="100%",
        height="100%",
        overflow="auto",
    )


@rx.page(
    route="/reportes",
    title="Reportes - Inmobiliaria Velar",
    on_load=ReportesState.load_preview_data,
)
def reportes_page() -> rx.Component:
    """Página principal del módulo de Reportes."""
    return dashboard_layout(
        rx.box(
            # Mobile Sidebar Drawer (Visible only on mobile)
            rx.box(
                rx.drawer.root(
                    rx.drawer.trigger(
                        neuro_button(
                            rx.icon("menu", size=24),
                            "Menú Reportes",
                            tooltip_content="Abrir menú de navegación",
                            variant="soft",
                            color_scheme="gray",
                            size="3",
                            margin_bottom="4",
                        )
                    ),
                    rx.drawer.overlay(background_color="rgba(0, 0, 0, 0.5)"),
                    rx.drawer.portal(
                        rx.drawer.content(
                            rx.vstack(
                                rx.heading("Navegación", size="4", margin_bottom="4"),
                                reports_sidebar(),
                                padding="4",
                                height="100%",
                                width="100%",
                                background_color=styles.BG_PANEL,
                            ),
                            top="0",
                            left="0",
                            height="100%",
                            width="280px",
                            background_color=styles.BG_PANEL,
                            padding="0",
                        )
                    ),
                    direction="left",
                ),
                display=[
                    "block",
                    "block",
                    "none",
                    "none",
                    "none",
                ],  # Show only on mobile/tablet
                width="100%",
                padding_x="4",
                padding_top="4",
            ),
            rx.hstack(
                # Desktop Sidebar (Original - Visible only on desktop)
                rx.box(
                    reports_sidebar(),
                    display=["none", "none", "block", "block", "block"],
                    width="250px",
                    height="100%",
                    flex_shrink="0",
                ),
                # Main Content Area
                reports_content(),
                height="calc(100vh - 80px)",
                width="100%",
                spacing="0",
                align_items="start",
            ),
            width="100%",
        )
    )
