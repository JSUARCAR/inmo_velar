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
                        label={"position": "top", "fill": "#6b7280", "fontSize": 12},
                        radius=[4, 4, 0, 0],
                    ),
                    rx.recharts.x_axis(data_key="name", axis_line=False, tick_line=False),
                    rx.recharts.y_axis(hide=True),
                    rx.recharts.cartesian_grid(
                        stroke_dasharray="3 3", vertical=False, stroke="#f1f5f9"
                    ),
                    rx.recharts.tooltip(
                        cursor={"fill": "rgba(0,0,0,0.04)"},
                        content_style={
                            "backgroundColor": "#1e293b",
                            "borderRadius": "12px",
                            "border": "none",
                            "boxShadow": "0 10px 15px -3px rgba(0, 0, 0, 0.1)",
                            "padding": "12px",
                        },
                        label_style={"color": "#94a3b8", "fontSize": "12px", "marginBottom": "4px"},
                        item_style={"color": "#f8fafc", "fontSize": "14px", "fontWeight": "bold"},
                    ),
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
                        stroke="#10b981",
                        fill="url(#colorRecaudo)",
                        fill_opacity=0.3,
                        type_="monotone",
                    ),
                    rx.el.svg.defs(
                        rx.el.svg.linear_gradient(
                            rx.el.svg.stop(offset="5%", stop_color="#10b981", stop_opacity=0.8),
                            rx.el.svg.stop(offset="95%", stop_color="#10b981", stop_opacity=0),
                            id="colorRecaudo",
                            x1="0",
                            y1="0",
                            x2="0",
                            y2="1",
                        )
                    ),
                    rx.recharts.x_axis(
                        data_key="name",
                        axis_line=False,
                        tick_line=False,
                        tick={"fontSize": 11, "fill": "#94a3b8"},
                    ),
                    rx.recharts.y_axis(
                        axis_line=False, tick_line=False, tick={"fontSize": 11, "fill": "#94a3b8"}
                    ),
                    rx.recharts.cartesian_grid(
                        stroke_dasharray="3 3", vertical=False, stroke="#f1f5f9"
                    ),
                    rx.recharts.tooltip(
                        content_style={
                            "backgroundColor": "#1e293b",
                            "borderRadius": "12px",
                            "border": "none",
                            "boxShadow": "0 10px 15px -3px rgba(0, 0, 0, 0.1)",
                            "padding": "12px",
                        },
                        label_style={"color": "#94a3b8", "fontSize": "12px", "marginBottom": "4px"},
                        item_style={"color": "#10b981", "fontSize": "14px", "fontWeight": "bold"},
                    ),
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
                        radius=[4, 4, 0, 0],
                        label={"position": "top", "fill": "#64748b", "fontSize": 10},
                    ),
                    rx.recharts.x_axis(
                        data_key="name",
                        stroke="#94a3b8",
                        font_size=10,
                        axis_line=False,
                        tick_line=False,
                    ),
                    rx.recharts.y_axis(
                        stroke="#94a3b8", font_size=10, axis_line=False, tick_line=False
                    ),
                    rx.recharts.cartesian_grid(
                        stroke_dasharray="3 3", vertical=False, stroke="#f1f5f9"
                    ),
                    rx.recharts.tooltip(
                        cursor={"fill": "rgba(99, 102, 241, 0.04)"},
                        content_style={
                            "backgroundColor": "#1e293b",
                            "borderRadius": "12px",
                            "border": "none",
                            "boxShadow": "0 10px 15px -3px rgba(0, 0, 0, 0.1)",
                            "padding": "12px",
                        },
                        label_style={"color": "#94a3b8", "fontSize": "12px", "marginBottom": "4px"},
                        item_style={"color": "#6366f1", "fontSize": "14px", "fontWeight": "bold"},
                    ),
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
                    rx.recharts.tooltip(
                        content_style={
                            "backgroundColor": "#1e293b",
                            "borderRadius": "12px",
                            "border": "none",
                            "boxShadow": "0 10px 15px -3px rgba(0, 0, 0, 0.1)",
                            "padding": "12px",
                        },
                        label_style={"color": "#94a3b8", "fontSize": "12px", "marginBottom": "4px"},
                        item_style={"color": "#f8fafc", "fontSize": "14px", "fontWeight": "bold"},
                    ),
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
                        label={
                            "position": "right",
                            "fill": "#10b981",
                            "fontSize": 10,
                            "fontWeight": "bold",
                        },
                    ),
                    rx.recharts.x_axis(type_="number", hide=True),
                    rx.recharts.y_axis(
                        data_key="name",
                        type_="category",
                        width=80,
                        tick={"fontSize": 11, "fill": "#64748b"},
                        axis_line=False,
                        tick_line=False,
                    ),
                    rx.recharts.tooltip(
                        cursor={"fill": "rgba(16, 185, 129, 0.04)"},
                        content_style={
                            "backgroundColor": "#1e293b",
                            "borderRadius": "12px",
                            "border": "none",
                            "boxShadow": "0 10px 15px -3px rgba(0, 0, 0, 0.1)",
                            "padding": "12px",
                        },
                        label_style={"color": "#94a3b8", "fontSize": "12px", "marginBottom": "4px"},
                        item_style={"color": "#10b981", "fontSize": "14px", "fontWeight": "bold"},
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
                        fill="url(#colorRiesgo)",
                        fill_opacity=0.4,
                        type_="monotone",
                    ),
                    rx.el.svg.defs(
                        rx.el.svg.linear_gradient(
                            rx.el.svg.stop(offset="5%", stop_color="#f59e0b", stop_opacity=0.6),
                            rx.el.svg.stop(offset="95%", stop_color="#f59e0b", stop_opacity=0),
                            id="colorRiesgo",
                            x1="0",
                            y1="0",
                            x2="0",
                            y2="1",
                        )
                    ),
                    rx.recharts.x_axis(
                        data_key="name",
                        axis_line=False,
                        tick_line=False,
                        tick={"fontSize": 10, "fill": "#94a3b8"},
                    ),
                    rx.recharts.y_axis(
                        axis_line=False, tick_line=False, tick={"fontSize": 10, "fill": "#94a3b8"}
                    ),
                    rx.recharts.tooltip(
                        content_style={
                            "backgroundColor": "#1e293b",
                            "borderRadius": "12px",
                            "border": "none",
                            "boxShadow": "0 10px 15px -3px rgba(0, 0, 0, 0.1)",
                            "padding": "12px",
                        },
                        label_style={"color": "#94a3b8", "fontSize": "12px", "marginBottom": "4px"},
                        item_style={"color": "#f59e0b", "fontSize": "14px", "fontWeight": "bold"},
                    ),
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
