import reflex as rx
from src.presentacion_reflex.components.layout.sidebar import sidebar
from src.presentacion_reflex.components.layout.dashboard_layout import dashboard_layout
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
        rx.input(
            placeholder="Buscar reportes...",
            on_change=ReportesState.set_search_query,
            icon="search",
            size="2",
            width="100%",
        ),
        rx.divider(margin_y="2"),
        rx.accordion.root(
            rx.foreach(
                ReportesState.filtered_grouped_reports,
                lambda category: rx.accordion.item(
                    header=rx.hstack(
                        rx.icon(category.icon, size=16, color=category.color),
                        rx.text(category.name, size="2", weight="bold", color=category.color),
                        spacing="2",
                        align_items="center",
                        width="100%"
                    ),
                    content=rx.vstack(
                        rx.foreach(
                            category.reports,
                            lambda report: report_item_sidebar(
                                report,
                                report.id == ReportesState.selected_report_id
                            )
                        ),
                        spacing="1",
                        padding_left="2",
                        width="100%",
                        padding_top="2"
                    ),
                )
            ),
            type="multiple",
            collapsible=True,
            width="100%",
            variant="ghost"
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
                ReportesState.active_report["description"], 
                size="2", 
                color="#64748b"
            ),
            rx.hstack(
                # Filtros Rápidos
                rx.select(
                    ReportesState.estado_options,
                    placeholder="Estado",
                    on_change=ReportesState.set_filter_activo,
                    value=ReportesState.filter_estado,
                    size="2",
                    width="150px",
                ),
                rx.input(
                    placeholder="Filtrar en tabla...",
                    icon="search",
                    on_change=ReportesState.set_filter_busqueda,
                    value=ReportesState.filter_busqueda_tabla,
                    size="2",
                    width="250px",
                ),
                rx.spacer(),
                rx.button(
                    rx.icon("download", size=18),
                    "Exportar CSV",
                    on_click=ReportesState.download_csv,
                    variant="solid",
                    color_scheme="green",
                    size="2",
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
                icon="triangle_alert",
                color_scheme="red",
                width="100%",
                margin_y="2",
            ),
        ),

        # Tabla de Previsualización
        rx.cond(
            ReportesState.is_loading,
            rx.center(rx.spinner(), padding="4", width="100%"),
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.foreach(
                            ReportesState.preview_headers,
                            lambda h: rx.table.column_header_cell(h)
                        )
                    )
                ),
                rx.table.body(
                   rx.foreach(
                       ReportesState.preview_data,
                       lambda row: rx.table.row(
                           rx.foreach(
                               ReportesState.preview_headers,
                               lambda h: rx.table.cell(row[h])
                           )
                       )
                   ) 
                ),
                variant="surface",
                size="1",
                width="100%",
            )
        ),

        # Paginación (Preview)
        rx.hstack(
            rx.text(
                f"Mostrando {ReportesState.preview_data.length()} registros (Total: {ReportesState.total_records}) - Previsualización limitada",
                size="1", 
                color="#64748b"
            ),
            rx.spacer(),
            rx.button(
                "Anterior", 
                on_click=ReportesState.prev_page, 
                disabled=ReportesState.current_page <= 1,
                size="1",
                variant="soft"
            ),
            rx.text(f"Página {ReportesState.current_page}", size="1"),
            rx.button(
                "Siguiente", 
                on_click=ReportesState.next_page,
                disabled=(ReportesState.current_page * ReportesState.page_size) >= ReportesState.total_records,
                size="1",
                variant="soft"
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

@rx.page(route="/reportes", title="Reportes - Inmobiliaria Velar", on_load=ReportesState.load_preview_data)
def reportes_page() -> rx.Component:
    """Página principal del módulo de Reportes."""
    return dashboard_layout(
        rx.box(
            # Mobile Sidebar Drawer (Visible only on mobile)
            rx.box(
                rx.drawer.root(
                    rx.drawer.trigger(
                        rx.button(
                            rx.icon("menu", size=24),
                            "Menú Reportes",
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
                display=["block", "block", "none", "none", "none"], # Show only on mobile/tablet
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
