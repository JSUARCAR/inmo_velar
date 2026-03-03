"""
Componentes de Tablas de Vencimientos para Dashboard - Reflex
Muestra las listas detalladas de contratos próximos a vencer.
"""
import reflex as rx
from src.presentacion_reflex.state.dashboard_state import DashboardState
from src.presentacion_reflex import styles

def badge_dias(dias: int) -> rx.Component:
    """Retorna un badge de color según los días restantes."""
    return rx.cond(
        dias <= 30,
        rx.badge(dias.to(str), " días", color_scheme="red", variant="soft"),
        rx.cond(
            dias <= 60,
            rx.badge(dias.to(str), " días", color_scheme="orange", variant="soft"),
            rx.badge(dias.to(str), " días", color_scheme="amber", variant="soft"),
        )
    )

from src.presentacion_reflex.components.neuro_elements import neuro_table_container, neuro_tooltip

def _tabla_vencimientos(titulo: str, icon: str, color_scheme: str, lista_estado, tooltip_text: str = "") -> rx.Component:
    """Componente genérico de tabla para mostrar vencimientos."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon(icon, color=rx.color(color_scheme, 9), size=20),
                rx.hstack(
                    rx.text(titulo, size="4", weight="bold", color=styles.TEXT_PRIMARY),
                    rx.cond(
                        tooltip_text != "",
                        neuro_tooltip(
                            content=tooltip_text,
                            children=rx.icon("info", size=16, color="gray.8", cursor="help")
                        )
                    ),
                    align="center",
                    spacing="2",
                ),
                rx.spacer(),
                align="center",
                spacing="2",
            ),
            rx.divider(),
            neuro_table_container(
                rx.cond(
                    lista_estado.length() > 0,
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("Contratante", color=styles.TEXT_SECONDARY, weight="medium"),
                                rx.table.column_header_cell("Propiedad", color=styles.TEXT_SECONDARY, weight="medium"),
                                rx.table.column_header_cell("Fecha Fin", color=styles.TEXT_SECONDARY, weight="medium"),
                                rx.table.column_header_cell("Vence En", color=styles.TEXT_SECONDARY, weight="medium"),
                            )
                        ),
                        rx.table.body(
                            rx.foreach(
                                lista_estado,
                                lambda item: rx.table.row(
                                    rx.table.cell(rx.text(item["parte_contratante"], size="2", weight="medium")),
                                    rx.table.cell(rx.text(item["direccion"], size="2", color=styles.TEXT_SECONDARY)),
                                    rx.table.cell(rx.text(item["fecha_fin"], size="2")),
                                    rx.table.cell(badge_dias(item["dias_restantes"].to(int))),
                                    align="center",
                                )
                            )
                        ),
                        variant="ghost",
                        size="1",
                        width="100%",
                    ),
                    rx.center(
                        rx.text("No hay contratos próximos a vencer en este rango.", size="2", color=styles.TEXT_SECONDARY),
                        padding="4",
                        width="100%",
                    ),
                ),
            ),
            spacing="3",
            width="100%",
        ),
        size="2",
        bg=styles.BG_PANEL,
        width="100%",
        height="100%",
    )

def tablas_vencimientos_detalle() -> rx.Component:
    """Contenedor principal para las dos tablas de vencimientos."""
    return rx.grid(
        _tabla_vencimientos(
            "Vencimientos de Mandato (90 Días)", 
            "briefcase", 
            "blue", 
            DashboardState.contratos_vencer_mandato_view,
            "Contratos de mandato (propietarios) que finalizan o requieren renovación temprana."
        ),
        _tabla_vencimientos(
            "Vencimientos de Arrendamiento (90 Días)", 
            "home", 
            "green", 
            DashboardState.contratos_vencer_arrendamiento_view,
            "Contratos de arrendamiento (inquilinos) próximos a finalizar su período vigente."
        ),
        columns=rx.breakpoints(initial="1", md="2"),
        spacing="4",
        width="100%",
    )
