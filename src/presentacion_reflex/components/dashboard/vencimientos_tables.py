"""
Componentes de Tablas de Vencimientos para Dashboard - Reflex
Muestra las listas detalladas de contratos próximos a vencer.
"""
import reflex as rx
from src.presentacion_reflex.state.dashboard_state import DashboardState
from src.presentacion_reflex import styles

def _vencimiento_badge(dias: rx.Var[int]) -> rx.Component:
    """Retorna un badge de color según los días restantes."""
    # Convertimos la variable de Reflex a string y concatenamos
    texto = dias.to_string() + " días"
    return rx.cond(
        dias <= 30,
        rx.badge(texto, color_scheme="red", variant="soft"),
        rx.cond(
            dias <= 60,
            rx.badge(texto, color_scheme="orange", variant="soft"),
            rx.badge(texto, color_scheme="amber", variant="soft"),
        )
    )

def _tabla_vencimientos(titulo: str, icon: str, color_scheme: str, lista_estado) -> rx.Component:
    """Componente genérico de tabla para mostrar vencimientos."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon(icon, color=rx.color(color_scheme, 9), size=20),
                rx.text(titulo, size="4", weight="bold", color=styles.TEXT_PRIMARY),
                rx.spacer(),
                rx.text(rx.cond(lista_estado.length() > 0, "DATA OK", "DATA EMPTY"), color="gray", size="1"),
                align="center",
                spacing="2",
            ),
            rx.divider(),
            rx.box(
                rx.cond(
                    lista_estado.length() > 0,
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("Contratante", color=styles.TEXT_MUTED),
                                rx.table.column_header_cell("Propiedad", color=styles.TEXT_MUTED),
                                rx.table.column_header_cell("Fecha Fin", color=styles.TEXT_MUTED),
                                rx.table.column_header_cell("Vence En", color=styles.TEXT_MUTED),
                            )
                        ),
                        rx.table.body(
                            rx.foreach(
                                lista_estado,
                                lambda item: rx.table.row(
                                    rx.table.cell(rx.text(item["parte_contratante"], size="2", weight="medium")),
                                    rx.table.cell(rx.text(item["direccion"], size="2", color=styles.TEXT_MUTED)),
                                    rx.table.cell(rx.text(item["fecha_fin"], size="2")),
                                    rx.table.cell(_vencimiento_badge(item["dias_restantes"])),
                                    align="center",
                                )
                            )
                        ),
                        variant="surface",
                        size="1",
                        width="100%",
                    ),
                    rx.center(
                        rx.text("No hay contratos próximos a vencer en este rango.", size="2", color=styles.TEXT_MUTED),
                        padding="4",
                        width="100%",
                    ),
                ),
                width="100%",
                overflow_x="auto",
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
            DashboardState.contratos_vencer_mandato_view
        ),
        _tabla_vencimientos(
            "Vencimientos de Arrendamiento (90 Días)", 
            "home", 
            "green", 
            DashboardState.contratos_vencer_arrendamiento_view
        ),
        columns=rx.breakpoints(initial="1", md="2"),
        spacing="4",
        width="100%",
    )
