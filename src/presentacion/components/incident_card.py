import flet as ft
from typing import Callable, Any
from src.dominio.entidades.incidente import Incidente

class IncidentCard(ft.Card):
    def __init__(self, incidente: Incidente, on_click: Callable[[Any], None]):
        super().__init__()
        self.incidente = incidente
        self.on_click_handler = on_click
        self.content = self._build_content()
        self.elevation = 2
        
    def _get_priority_color(self, priority: str) -> str:
        colors = {
            "Baja": ft.Colors.GREEN_400,
            "Media": ft.Colors.ORANGE_400,
            "Alta": ft.Colors.DEEP_ORANGE_400,
            "Urgente": ft.Colors.RED_600
        }
        return colors.get(priority, ft.Colors.GREY_400)

    def _get_status_icon(self, status: str) -> str:
        icons = {
            "Reportado": ft.Icons.REPORT_PROBLEM_OUTLINED,
            "En Revision": ft.Icons.SEARCH,
            "Cotizado": ft.Icons.REQUEST_QUOTE_OUTLINED,
            "Aprobado": ft.Icons.CHECK_CIRCLE_OUTLINED,
            "En Reparacion": ft.Icons.CONSTRUCTION,
            "Finalizado": ft.Icons.VERIFIED,
            "Cancelado": ft.Icons.CANCEL_OUTLINED
        }
        return icons.get(status, ft.Icons.CIRCLE)

    def _build_content(self):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.ListTile(
                        leading=ft.Icon(
                            self._get_status_icon(self.incidente.estado),
                            color=self._get_priority_color(self.incidente.prioridad),
                            size=30
                        ),
                        title=ft.Text(
                            f"Incidente #{self.incidente.id_incidente}",
                            weight=ft.FontWeight.BOLD
                        ),
                        subtitle=ft.Text(
                            self.incidente.descripcion_incidente,
                            max_lines=2,
                            overflow=ft.TextOverflow.ELLIPSIS
                        ),
                        trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT),
                        on_click=lambda e: self.on_click_handler(self.incidente)
                    ),
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Container(
                                    content=ft.Text(self.incidente.estado, size=12, color=ft.Colors.WHITE),
                                    bgcolor=self._get_priority_color(self.incidente.prioridad),
                                    border_radius=4,
                                    padding=ft.padding.symmetric(horizontal=8, vertical=4)
                                ),
                                ft.Text(
                                    self.incidente.fecha_incidente[:10] if isinstance(self.incidente.fecha_incidente, str) else self.incidente.fecha_incidente.strftime("%Y-%m-%d"),
                                    size=12,
                                    color=ft.Colors.GREY_600
                                )
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        padding=ft.padding.only(left=16, right=16, bottom=12)
                    )
                ],
                spacing=0
            ),
            width=300, # Fixed width for Kanban or responsive grid
            padding=0
        )
