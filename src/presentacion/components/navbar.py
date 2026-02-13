"""
Barra Superior (Navbar) - Inmobiliaria Velar
"""

import reflex as rx

from src.presentacion.theme import colors


class Navbar(ft.Container):
    """Barra superior con titulo y notificaciones."""

    def __init__(self, titulo: str, on_open_alerts, on_refresh=None):
        super().__init__()
        self.titulo = titulo
        self.on_open_alerts = on_open_alerts
        self.on_refresh = on_refresh

        self.height = 70
        self.bgcolor = colors.BACKGROUND
        self.border = ft.border.only(bottom=ft.border.BorderSide(1, colors.BORDER_DEFAULT))
        self.padding = ft.padding.symmetric(horizontal=30)
        self.alignment = ft.alignment.center

        self.content = self._build_content()

    def _build_content(self):
        # Build action buttons
        action_buttons = []

        # Refresh button (only if callback provided)
        if self.on_refresh:
            action_buttons.append(
                ft.IconButton(
                    icon=ft.Icons.REFRESH,
                    icon_color=colors.PRIMARY,
                    icon_size=24,
                    on_click=lambda _: self.on_refresh(),
                    tooltip="Actualizar datos",
                )
            )

        # Search bar
        action_buttons.append(
            ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.SEARCH, color=colors.TEXT_SECONDARY, size=20),
                        ft.Text("Buscar propiedad...", color=colors.TEXT_SECONDARY, size=14),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                ),
                bgcolor=colors.SURFACE,
                border_radius=8,
                padding=ft.padding.symmetric(horizontal=12, vertical=8),
                width=250,
                margin=ft.margin.only(right=20),
            )
        )

        # Notifications bell
        action_buttons.append(
            ft.Stack(
                [
                    ft.IconButton(
                        icon=ft.Icons.NOTIFICATIONS_OUTLINED,
                        icon_color=colors.TEXT_SECONDARY,
                        icon_size=24,
                        on_click=lambda _: self.on_open_alerts(),
                        tooltip="Centro de Alertas",
                    ),
                    # Badge rojo (hardcoded por ahora)
                    ft.Container(
                        bgcolor=colors.ERROR, width=10, height=10, border_radius=5, right=10, top=10
                    ),
                ]
            )
        )

        self.txt_titulo = ft.Text(
            self.titulo,
            size=24,
            weight=ft.FontWeight.BOLD,
            color=colors.TEXT_PRIMARY,
            font_family="Outfit",
        )

        return ft.Row(
            [
                # Titulo de la Pagina
                self.txt_titulo,
                ft.Container(expand=True),
                # Acciones (Buscador Global + Alertas)
                ft.Container(content=ft.Row(action_buttons)),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

    def set_title(self, nuevo_titulo: str):
        """Actualiza el título del Navbar dinámicamente."""
        self.titulo = nuevo_titulo
        self.txt_titulo.value = nuevo_titulo
        self.txt_titulo.update()
