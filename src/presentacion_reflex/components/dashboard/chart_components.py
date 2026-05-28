"""
Componentes de Gráficos para Dashboard - Reflex
Wrappers COMPLETAMENTE DESACTIVADOS para evitar TypeError fatal en Recharts 3 / React 19.
"""

import reflex as rx

def vencimientos_chart() -> rx.Component:
    return rx.center(rx.text("Gráfico de Vencimientos (Desactivado)"), height="250px", width="100%", border="1px dashed gray", border_radius="8px")

def evolucion_chart() -> rx.Component:
    return rx.center(rx.text("Gráfico de Evolución (Desactivado)"), height="250px", width="100%", border="1px dashed gray", border_radius="8px")

def incidentes_pie_chart() -> rx.Component:
    return rx.center(rx.text("Gráfico de Incidentes (Desactivado)"), height="250px", width="100%", border="1px dashed gray", border_radius="8px")

def propiedades_tipo_chart() -> rx.Component:
    return rx.center(rx.text("Gráfico de Propiedades (Desactivado)"), height="250px", width="100%", border="1px dashed gray", border_radius="8px")

def top_asesores_chart() -> rx.Component:
    return rx.center(rx.text("Gráfico de Asesores (Desactivado)"), height="250px", width="100%", border="1px dashed gray", border_radius="8px")

def tunel_vencimientos_chart() -> rx.Component:
    return rx.center(rx.text("Túnel de Vencimientos (Desactivado)"), height="250px", width="100%", border="1px dashed gray", border_radius="8px")
