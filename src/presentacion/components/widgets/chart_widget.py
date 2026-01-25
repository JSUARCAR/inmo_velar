"""
Componente de Gráfico - Inmobiliaria Velar
Wrapper para gráficos Plotly en Flet.
"""

import flet as ft
import plotly.graph_objects as go
from flet.plotly_chart import PlotlyChart

from src.presentacion.theme import colors


class ChartWidget(ft.Container):
    """Contenedor para graficos Plotly."""

    def __init__(self, titulo: str, chart: go.Figure, descripcion: str = ""):
        super().__init__()
        self.titulo = titulo
        self.chart = chart
        self.descripcion = descripcion

        # Configurar grafica
        self.chart.update_layout(
            margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter", color=colors.TEXT_SECONDARY),
        )

        # Estilos Container
        self.bgcolor = colors.SURFACE
        self.border_radius = 12
        self.padding = 20
        self.shadow = ft.BoxShadow(
            spread_radius=1, blur_radius=10, color="rgba(0, 0, 0, 0.08)", offset=ft.Offset(0, 4)
        )

        self.content = self._build_content()

    def _build_content(self):
        return ft.Column(
            [
                # Titulo Grafico
                ft.Text(
                    self.titulo, size=16, weight=ft.FontWeight.W_600, color=colors.TEXT_PRIMARY
                ),
                # Descripcion (opcional)
                (
                    ft.Text(
                        self.descripcion,
                        size=12,
                        color=colors.TEXT_SECONDARY,
                        visible=bool(self.descripcion),
                    )
                    if self.descripcion
                    else ft.Container()
                ),
                ft.Divider(height=10, color="transparent"),
                # Grafico Plotly
                ft.Container(content=PlotlyChart(self.chart, expand=True), expand=True),
            ],
            expand=True,
        )
