"""
Componentes de Gráficos para Dashboard - Reflex
Wrappers simplificados para evitar Error #418 en React 19.
"""

import reflex as rx
from src.presentacion_reflex.state.dashboard_state import DashboardState
from src.presentacion_reflex import styles

def vencimientos_chart() -> rx.Component:
    return rx.recharts.bar_chart(
        rx.recharts.bar(
            data_key="value",
            fill=styles.BRAND_PRIMARY,
        ),
        rx.recharts.x_axis(data_key="name"),
        rx.recharts.y_axis(),
        data=DashboardState.vencimiento_chart_data,
        width="100%",
        height=250,
    )

def evolucion_chart() -> rx.Component:
    return rx.recharts.area_chart(
        rx.recharts.area(
            data_key="recaudo",
            fill=styles.BRAND_PRIMARY,
            stroke=styles.BRAND_PRIMARY,
        ),
        rx.recharts.x_axis(data_key="mes"),
        rx.recharts.y_axis(),
        data=DashboardState.evolucion_data,
        width="100%",
        height=250,
    )

def incidentes_pie_chart() -> rx.Component:
    return rx.recharts.pie_chart(
        rx.recharts.pie(
            data=DashboardState.incidentes_chart_data,
            data_key="value",
            name_key="name",
            outer_radius=80,
            fill="#8884d8",
        ),
        width="100%",
        height=250,
    )

def propiedades_tipo_chart() -> rx.Component:
    return rx.recharts.bar_chart(
        rx.recharts.bar(
            data_key="value",
            fill=styles.BRAND_SECONDARY,
        ),
        rx.recharts.x_axis(data_key="name"),
        rx.recharts.y_axis(),
        data=DashboardState.propiedades_tipo_data,
        width="100%",
        height=250,
    )

def top_asesores_chart() -> rx.Component:
    return rx.recharts.bar_chart(
        rx.recharts.bar(
            data_key="value",
            fill=styles.BRAND_PRIMARY,
        ),
        rx.recharts.x_axis(data_key="name"),
        rx.recharts.y_axis(),
        data=DashboardState.top_asesores_data,
        width="100%",
        height=250,
    )

def tunel_vencimientos_chart() -> rx.Component:
    return rx.recharts.area_chart(
        rx.recharts.area(
            data_key="value",
            fill=styles.BRAND_SECONDARY,
        ),
        rx.recharts.x_axis(data_key="name"),
        rx.recharts.y_axis(),
        data=DashboardState.tunel_chart_data,
        width="100%",
        height=250,
    )
