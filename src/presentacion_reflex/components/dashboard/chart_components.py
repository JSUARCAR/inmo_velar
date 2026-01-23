"""
Componentes de Gráficos para Dashboard - Reflex
Wrappers para gráficos usando Recharts con datos del estado.
"""

import reflex as rx
from src.presentacion_reflex.state.dashboard_state import DashboardState

def vencimientos_chart() -> rx.Component:
    """
    Gráfico de barras para contratos por vencer.
    """
    return rx.card(
        rx.vstack(
            rx.text("Contratos por Vencer (90 Días)", size="4", weight="bold"),
            rx.box(
                rx.recharts.bar_chart(
                    rx.recharts.bar(
                        data_key="value",
                        stroke="#8884d8",
                        fill="#8884d8",
                    ),
                    rx.recharts.x_axis(data_key="name"),
                    rx.recharts.y_axis(),
                    rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
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
        size="2",
        width="100%",
    )


def evolucion_chart() -> rx.Component:
    """
    Gráfico de área para evolución de recaudos.
    """
    return rx.card(
        rx.vstack(
            rx.text("Evolución de Recaudos (6 Meses)", size="4", weight="bold"),
            rx.box(
                rx.recharts.area_chart(
                    rx.recharts.area(
                        data_key="recaudo",
                        stroke="#82ca9d",
                        fill="#82ca9d",
                    ),
                    rx.recharts.x_axis(data_key="name"),
                    rx.recharts.y_axis(),
                    rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
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
        size="2",
        width="100%",
    )


def propiedades_tipo_chart() -> rx.Component:
    """
    Gráfico de barras de propiedades por tipo.
    Estilo "Experto Elite".
    """
    return rx.card(
        rx.vstack(
            rx.text("Propiedades por Tipo", size="4", weight="bold"),
            rx.box(
                rx.recharts.bar_chart(
                    rx.recharts.bar(
                        data_key="value",
                        stroke="#6366f1",
                        fill="#6366f1",
                        radius=[4, 4, 0, 0], # Bordes redondeados superiores
                    ),
                    rx.recharts.x_axis(data_key="name", stroke="#94a3b8", font_size=12),
                    rx.recharts.y_axis(stroke="#94a3b8", font_size=12),
                    rx.recharts.cartesian_grid(stroke_dasharray="3 3", vertical=False, stroke="#e2e8f0"),
                    rx.recharts.tooltip(
                        cursor={"fill": "transparent"},
                        content_style={"backgroundColor": "#1e293b", "color": "#f8fafc", "borderRadius": "8px", "border": "none"},
                    ),
                    data=DashboardState.propiedades_tipo_chart_data,
                    height=250,
                    width="100%",
                    bar_category_gap="20%",
                ),
                width="100%",
                height="250px",
            ),
            spacing="2",
            width="100%",
        ),
        size="2",
        width="100%",
    )


def incidentes_pie_chart() -> rx.Component:
    """
    Gráfico de torta para incidentes.
    """
    return rx.card(
        rx.vstack(
            rx.text("Incidentes por Estado", size="4", weight="bold"),
            rx.box(
                rx.recharts.pie_chart(
                    rx.recharts.pie(
                        data=DashboardState.incidentes_chart_data,
                        data_key="value",
                        name_key="name",
                        cx="50%",
                        cy="50%",
                        outer_radius=80,
                        label=True,
                    ),
                    rx.recharts.tooltip(),
                    rx.recharts.legend(),
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
        size="2",
        width="100%",
    )

def top_asesores_chart() -> rx.Component:
    """Gráfico de ranking de asesores por revenue."""
    return rx.card(
        rx.vstack(
            rx.text("Top Asesores (Revenue)", size="4", weight="bold"),
            rx.box(
                rx.recharts.bar_chart(
                    rx.recharts.bar(
                        data_key="revenue",
                        fill="#10b981",
                        radius=[0, 4, 4, 0],
                    ),
                    rx.recharts.x_axis(type_="number", hide=True),
                    rx.recharts.y_axis(
                        data_key="name", 
                        type_="category", 
                        width=80,
                        tick={"fontSize": 12}
                    ),
                    rx.recharts.tooltip(
                        cursor={"fill": "transparent"},
                        content_style={"backgroundColor": "#1e293b", "color": "#f8fafc", "borderRadius": "8px"},
                    ),
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
        size="2",
        width="100%",
    )

def tunel_vencimientos_chart() -> rx.Component:
    """Gráfico de túnel de vencimientos (Riesgo)."""
    return rx.card(
        rx.vstack(
            rx.text("Túnel de Vencimientos (12 Meses)", size="4", weight="bold"),
            rx.box(
                rx.recharts.area_chart(
                    rx.recharts.area(
                        data_key="riesgo",
                        stroke="#f59e0b",
                        fill="#fef3c7",
                    ),
                    rx.recharts.x_axis(data_key="name", font_size=10),
                    rx.recharts.y_axis(font_size=10),
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
        size="2",
        width="100%",
    )
