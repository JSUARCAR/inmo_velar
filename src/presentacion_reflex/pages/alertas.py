"""
Página: Dashboard de Alertas Tempranas
=====================================
Vista dedicada para la gestión y resolución de alertas operativas.

Autor: Sistema de Gestión Inmobiliaria
Fecha: 2026-05-10
"""

import reflex as rx

from src.presentacion_reflex.state.alertas_dashboard_state import AlertasDashboardState
from src.presentacion_reflex.components.layout.dashboard_layout import dashboard_layout
from src.presentacion_reflex.components.neuro_elements import (
    neuro_panel,
    neuro_button,
    neuro_badge,
    neuro_select_root,
    neuro_spinner,
)
from src.presentacion_reflex import styles


def render_alerta_row(alerta: dict) -> rx.Component:
    """Renderiza una fila de la tabla de alertas."""
    prioridad = alerta.get("prioridad", "Media")
    color_prioridad = rx.cond(
        prioridad == "Alta", "red",
        rx.cond(prioridad == "Media", "orange", "blue")
    )

    estado = alerta.get("estado_alerta", "Pendiente")
    color_estado = rx.cond(
        estado == "Pendiente", "orange",
        rx.cond(estado == "En Proceso", "blue", "green")
    )

    return rx.table.row(
        rx.table.cell(
            rx.vstack(
                rx.text(alerta.get("tipo_alerta"), weight="bold", size="2"),
                rx.text(alerta.get("descripcion_alerta"), size="1", color=styles.TEXT_SECONDARY),
                spacing="1",
            )
        ),
        rx.table.cell(
            neuro_badge(prioridad, color_scheme=color_prioridad)
        ),
        rx.table.cell(
            rx.text(rx.cond(alerta.get("fecha_vencimiento_alerta"), alerta.get("fecha_vencimiento_alerta"), "N/A"), size="2")
        ),
        rx.table.cell(
            neuro_badge(estado, color_scheme=color_estado)
        ),
        rx.table.cell(
            rx.cond(
                estado == "Pendiente",
                neuro_button(
                    "Resolver",
                    on_click=lambda: AlertasDashboardState.resolver_alerta(alerta["id_alertas"]),
                    size="1",
                    variant="soft",
                    color_scheme="green",
                ),
                rx.text("---", size="2", color=styles.TEXT_TERTIARY)
            )
        ),
    )


def alertas_page() -> rx.Component:
    """Vista principal del Dashboard de Alertas."""
    return dashboard_layout(
        rx.vstack(
            # HEADER
            rx.box(
                rx.hstack(
                    rx.vstack(
                        rx.heading("Alertas Tempranas", size="7", font_family=styles.FONT_DISPLAY),
                        rx.text("Gestión proactiva de vencimientos y eventos críticos", size="2", color=styles.TEXT_SECONDARY),
                        spacing="1",
                    ),
                    rx.spacer(),
                    rx.hstack(
                        neuro_button(
                            "Exportar",
                            icon="file_spreadsheet",
                            on_click=AlertasDashboardState.exportar_csv,
                            variant="soft",
                            color_scheme="green",
                        ),
                        neuro_button(
                            "Sincronizar Ahora",
                            icon="refresh-cw",
                            on_click=AlertasDashboardState.sincronizar_ahora,
                            is_loading=AlertasDashboardState.is_loading,
                        ),
                        spacing="3",
                    ),
                    width="100%",
                    align="center",
                ),
                padding="6",
                background=styles.BG_PANEL,
                border_bottom=f"1px solid {styles.BORDER_DEFAULT}",
                width="100%",
            ),

            # CONTENIDO
            rx.vstack(
                # FILTROS
                rx.hstack(
                    neuro_select_root(
                        ["Todas", "Pendiente", "En Proceso", "Resuelta", "Archivada"],
                        value=AlertasDashboardState.filtro_estado,
                        on_change=AlertasDashboardState.set_filtro_estado,
                        placeholder="Estado",
                    ),
                    neuro_select_root(
                        ["Todas", "Alta", "Media", "Baja"],
                        value=AlertasDashboardState.filtro_prioridad,
                        on_change=AlertasDashboardState.set_filtro_prioridad,
                        placeholder="Prioridad",
                    ),
                    spacing="4",
                    width="100%",
                ),

                # TABLA DE ALERTAS
                neuro_panel(
                    rx.cond(
                        AlertasDashboardState.is_loading,
                        rx.center(neuro_spinner(), width="100%", padding="40px"),
                        rx.table.root(
                            rx.table.header(
                                rx.table.row(
                                    rx.table.column_header_cell("Tipo y Descripción"),
                                    rx.table.column_header_cell("Prioridad"),
                                    rx.table.column_header_cell("Vencimiento"),
                                    rx.table.column_header_cell("Estado"),
                                    rx.table.column_header_cell("Acciones"),
                                )
                            ),
                            rx.table.body(
                                rx.foreach(
                                    AlertasDashboardState.alertas,
                                    render_alerta_row
                                )
                            ),
                            width="100%",
                            variant="surface",
                        ),
                    ),
                    width="100%",
                ),
                
                # PAGINACIÓN (Simplificada)
                rx.hstack(
                    rx.text(f"Total: {AlertasDashboardState.total_alertas} alertas"),
                    rx.spacer(),
                    rx.hstack(
                        neuro_button(
                            "Anterior",
                            on_click=lambda: AlertasDashboardState.set_page(AlertasDashboardState.page - 1),
                            variant="soft",
                            size="1",
                        ),
                        neuro_button(
                            "Siguiente",
                            on_click=lambda: AlertasDashboardState.set_page(AlertasDashboardState.page + 1),
                            variant="soft",
                            size="1",
                        ),
                        spacing="2",
                    ),
                    width="100%",
                    padding_top="4",
                ),

                width="100%",
                padding="6",
                spacing="6",
            ),
            width="100%",
            background=styles.BG_APP,
            min_height="100vh",
        )
    )

# Ruta protegida
@rx.page(
    route="/alertas",
    on_load=[AlertasDashboardState.load_alertas],
)
def alertas():
    return alertas_page()
