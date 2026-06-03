"""
Componentes de Gráficos para Dashboard - Reflex usando Plotly nativo.
Estos componentes leen las figuras `go.Figure` generadas asíncronamente
en el `DashboardState`.
"""

import reflex as rx
from src.presentacion_reflex.state.dashboard_state import DashboardState

def vencimientos_chart(height: str = "320px") -> rx.Component:
    return rx.plotly(
        data=DashboardState.vencimiento_chart_fig,
        height=height,
        width="100%"
    )

def evolucion_chart(height: str = "320px") -> rx.Component:
    return rx.plotly(
        data=DashboardState.evolucion_chart_fig,
        height=height,
        width="100%"
    )

def incidentes_pie_chart(height: str = "280px") -> rx.Component:
    return rx.plotly(
        data=DashboardState.incidentes_chart_fig,
        height=height,
        width="100%"
    )

def propiedades_tipo_chart(height: str = "280px") -> rx.Component:
    return rx.plotly(
        data=DashboardState.propiedades_tipo_chart_fig,
        height=height,
        width="100%"
    )

def top_asesores_chart(height: str = "280px") -> rx.Component:
    return rx.plotly(
        data=DashboardState.top_asesores_chart_fig,
        height=height,
        width="100%"
    )

def tunel_vencimientos_chart(height: str = "300px") -> rx.Component:
    return rx.plotly(
        data=DashboardState.tunel_chart_fig,
        height=height,
        width="100%"
    )
