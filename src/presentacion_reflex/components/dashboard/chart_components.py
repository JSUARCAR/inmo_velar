"""
Componentes de Gráficos para Dashboard - Reflex
Wrappers para gráficos usando Recharts con datos del estado.
"""

import reflex as rx
from reflex.vars.base import Var
from src.presentacion_reflex.utils.formatters import format_currency

from src.presentacion_reflex.state.dashboard_state import DashboardState
from src.presentacion_reflex.components.neuro_elements import neuro_panel
from src.presentacion_reflex import styles


def _info_header(title: str, tooltip_text: str) -> rx.Component:
    """Genera un encabezado estándar con ícono de información y tooltip neumático."""
    return rx.hstack(
        rx.text(title, size="4", weight="bold", color=styles.TEXT_PRIMARY),
        rx.hover_card.root(
            rx.hover_card.trigger(rx.icon("info", size=16, color=styles.TEXT_TERTIARY, cursor="help")),
            rx.hover_card.content(
                rx.text(tooltip_text, size="2", color=styles.TEXT_SECONDARY),
                side="top",
                align="center",
                side_offset=5,
                style=styles.NEU_PANEL_STYLE,
                padding="12px",
                max_width="250px",
            )
        ),
        align="center",
        spacing="2",
    )



def vencimientos_chart() -> rx.Component:
    """
    Gráfico de barras para contratos por vencer con estilo neumático.
    """
    return neuro_panel(
        rx.vstack(
            _info_header(
                "Contratos por Vencer (90 Días)",
                "Distribución de contratos que finalizarán en los próximos 30, 60 y 90 días."
            ),
            rx.box(
                rx.recharts.bar_chart(
                    rx.recharts.bar(
                        data_key="value",
                        stroke=styles.ACCENT_COLOR,
                        fill=styles.ACCENT_COLOR,
                        radius=[4, 4, 0, 0],
                    ),
                    rx.recharts.x_axis(data_key="name", axis_line=False, tick_line=False),
                    rx.recharts.y_axis(hide=True),
                    rx.recharts.cartesian_grid(
                        stroke_dasharray="3 3", vertical=False, stroke=styles.BORDER_DEFAULT
                    ),
                    rx.recharts.tooltip(),
                    data=DashboardState.vencimiento_chart_data,
                    height=250,
                    width="100%",
                ),
                width="100%",
                height="250px",
            ),
            spacing="2",
            width="100%",
        ),
        width="100%",
    )


def evolucion_chart() -> rx.Component:
    """
    Gráfico de área para evolución de recaudos con estilo neumático.
    """
    return neuro_panel(
        rx.vstack(
            _info_header(
                "Evolución de Recaudos (6 Meses)",
                "Histórico del recaudo total efectivo durante los últimos 6 meses."
            ),
            rx.box(
                rx.recharts.area_chart(
                    rx.recharts.area(
                        data_key="recaudo",
                        stroke="#10b981",
                        fill="#10b981",
                        fill_opacity=0.3,
                        type_="monotone",
                    ),
                    rx.recharts.x_axis(
                        data_key="name",
                        axis_line=False,
                        tick_line=False,
                    ),
                    rx.recharts.y_axis(
                        axis_line=False, tick_line=False
                    ),
                    rx.recharts.cartesian_grid(
                        stroke_dasharray="3 3", vertical=False, stroke=styles.BORDER_DEFAULT
                    ),
                    rx.recharts.tooltip(),
                    data=DashboardState.evolucion_chart_data,
                    height=250,
                    width="100%",
                ),
                width="100%",
                height="250px",
            ),
            spacing="2",
            width="100%",
        ),
        width="100%",
    )


def propiedades_tipo_chart() -> rx.Component:
    """
    Gráfico de barras de propiedades por tipo con estilo neumático.
    """
    return neuro_panel(
        rx.vstack(
            _info_header(
                "Propiedades por Tipo",
                "Distribución del portafolio activo según la destinación del inmueble."
            ),
            rx.box(
                rx.recharts.bar_chart(
                    rx.recharts.bar(
                        data_key="value",
                        stroke=styles.ACCENT_COLOR,
                        fill=styles.ACCENT_COLOR,
                        radius=[4, 4, 0, 0],
                    ),
                    rx.recharts.x_axis(
                        data_key="name",
                        stroke=styles.TEXT_TERTIARY,
                        font_size=10,
                        axis_line=False,
                        tick_line=False,
                    ),
                    rx.recharts.y_axis(
                        stroke=styles.TEXT_TERTIARY, font_size=10, axis_line=False, tick_line=False,
                    ),
                    rx.recharts.cartesian_grid(
                        stroke_dasharray="3 3", vertical=False, stroke=styles.BORDER_DEFAULT
                    ),
                    rx.recharts.tooltip(),
                    data=DashboardState.propiedades_tipo_chart_data,
                    height=250,
                    width="100%",
                    bar_category_gap="30%",
                ),
                width="100%",
                height="250px",
            ),
            spacing="2",
            width="100%",
        ),
        width="100%",
    )


def incidentes_pie_chart() -> rx.Component:
    """
    Gráfico de torta para incidentes con estilo neumático.
    """
    return neuro_panel(
        rx.vstack(
            _info_header(
                "Incidentes por Estado",
                "Proporción de incidentes reportados clasificados por su estado actual de resolución."
            ),
            rx.box(
                rx.recharts.pie_chart(
                    rx.recharts.pie(
                        data=DashboardState.incidentes_chart_data,
                        data_key="value",
                        name_key="name",
                        outer_radius=80,
                    ),
                    rx.recharts.tooltip(),
                    rx.recharts.legend(vertical_align="bottom", height=36, icon_type="circle"),
                    height=250,
                    width="100%",
                ),
                width="100%",
                height="250px",
                display="flex",
                justify_content="center",
            ),
            spacing="2",
            width="100%",
        ),
        width="100%",
    )


def top_asesores_chart() -> rx.Component:
    """Gráfico de ranking de asesores por revenue con estilo neumático."""
    return neuro_panel(
        rx.vstack(
            _info_header(
                "Top Asesores (Revenue)",
                "Clasificación de asesores basada en los ingresos generados por comisiones."
            ),
            rx.box(
                rx.recharts.bar_chart(
                    rx.recharts.bar(
                        data_key="revenue",
                        radius=[0, 4, 4, 0],
                    ),
                    rx.recharts.x_axis(type_="number", hide=True),
                    rx.recharts.y_axis(
                        data_key="name",
                        type_="category",
                        width=80,
                        axis_line=False,
                        tick_line=False,
                    ),
                    rx.recharts.tooltip(),
                    layout="vertical",
                    data=DashboardState.top_asesores_chart_data,
                    height=250,
                    width="100%",
                ),
                width="100%",
                height="250px",
            ),
            spacing="2",
            width="100%",
        ),
        width="100%",
    )


def tunel_vencimientos_chart() -> rx.Component:
    """Gráfico de túnel de vencimientos (Riesgo) con estilo neumático."""
    return neuro_panel(
        rx.vstack(
            _info_header(
                "Túnel de Vencimientos (12 Meses)",
                "Proyección del canon en riesgo por contratos que expiran en los próximos 12 meses."
            ),
            rx.box(
                rx.recharts.area_chart(
                    rx.recharts.area(
                        data_key="riesgo",
                        stroke="#f59e0b",
                        fill="#f59e0b",
                        fill_opacity=0.4,
                        type_="monotone",
                    ),
                    rx.recharts.x_axis(
                        data_key="name",
                        axis_line=False,
                        tick_line=False,
                    ),
                    rx.recharts.y_axis(
                        axis_line=False, tick_line=False
                    ),
                    rx.recharts.tooltip(),
                    data=DashboardState.tunel_chart_data,
                    height=250,
                    width="100%",
                ),
                width="100%",
                height="250px",
            ),
            spacing="2",
            width="100%",
        ),
        width="100%",
    )


