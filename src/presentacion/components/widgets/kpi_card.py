"""
Componente KPI Card - Inmobiliaria Velar
Tarjeta para mostrar indicadores clave de rendimiento.
"""

import reflex as rx

from src.presentacion.theme import colors


class KpiCard(ft.Container):
    """Tarjeta de indicador KPI."""

    def __init__(
        self,
        titulo: str,
        valor: str,
        icono: str,
        color_icono: str = colors.PRIMARY,
        subtitulo: str = "",
        color_fondo: str = colors.SURFACE,
        es_critico: bool = False,
        on_click=None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.titulo = titulo
        self.valor = valor
        self.icono = icono
        self.color_icono = color_icono
        self.subtitulo = subtitulo
        self.es_critico = es_critico
        self.on_click = on_click

        # Configurar estilos base
        self.bgcolor = colors.ERROR if es_critico else color_fondo
        self.border_radius = 12
        self.padding = 20
        self.shadow = ft.BoxShadow(
            spread_radius=1, blur_radius=10, color="rgba(0, 0, 0, 0.08)", offset=ft.Offset(0, 4)
        )

        # Contenido
        self.content = self._construir_contenido()

    def _construir_contenido(self):
        color_texto_titulo = colors.TEXT_ON_PRIMARY if self.es_critico else colors.TEXT_SECONDARY
        color_texto_valor = colors.TEXT_ON_PRIMARY if self.es_critico else colors.TEXT_PRIMARY
        color_icon = colors.TEXT_ON_PRIMARY if self.es_critico else self.color_icono

        return ft.Column(
            [
                # Encabezado: Icono + Titulo
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(self.icono, color=color_icon, size=20),
                            bgcolor=(
                                colors.BACKGROUND
                                if not self.es_critico
                                else "rgba(255,255,255,0.2)"
                            ),
                            padding=8,
                            border_radius=8,
                        ),
                        ft.Text(
                            self.titulo,
                            size=14,
                            color=color_texto_titulo,
                            weight=ft.FontWeight.W_500,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Container(height=10),
                # Valor Principal
                ft.Text(self.valor, size=28, weight=ft.FontWeight.BOLD, color=color_texto_valor),
                # Subtitulo (opcional)
                (
                    ft.Text(
                        self.subtitulo,
                        size=12,
                        color=color_texto_titulo if self.es_critico else colors.TEXT_SECONDARY,
                        visible=bool(self.subtitulo),
                    )
                    if self.subtitulo
                    else ft.Container()
                ),
            ],
            spacing=0,
        )
