"""
Componentes de Gráficos para Dashboard - Reflex usando Plotly nativo.
Estos componentes leen las figuras `go.Figure` generadas asíncronamente
en el `DashboardState`.
"""

import reflex as rx
from src.presentacion_reflex.state.dashboard_state import DashboardState

def vencimientos_chart() -> rx.Component:
    return rx.plotly(
        data=DashboardState.vencimiento_chart_fig,
        height="250px",
        width="100%"
    )

def evolucion_chart() -> rx.Component:
    return rx.plotly(
        data=DashboardState.evolucion_chart_fig,
        height="250px",
        width="100%"
    )

def incidentes_pie_chart() -> rx.Component:
    return rx.plotly(
        data=DashboardState.incidentes_chart_fig,
        height="250px",
        width="100%"
    )

def propiedades_tipo_chart() -> rx.Component:
    return rx.plotly(
        data=DashboardState.propiedades_tipo_chart_fig,
        height="250px",
        width="100%"
    )

def top_asesores_chart() -> rx.Component:
    return rx.plotly(
        data=DashboardState.top_asesores_chart_fig,
        height="250px",
        width="100%"
    )

def tunel_vencimientos_chart() -> rx.Component:
    return rx.plotly(
        data=DashboardState.tunel_chart_fig,
        height="250px",
        width="100%"
    )
