from datetime import datetime
from typing import Callable, Optional

import reflex as rx

from src.infraestructura.persistencia.database import DatabaseManager
from src.infraestructura.persistencia.repositorio_asesor_sqlite import RepositorioAsesorSQLite


class DashboardFilters(ft.Container):
    """
    Componente de filtros para el dashboard.
    Permite filtrar por Mes, Año y Asesor.
    """

    def __init__(
        self,
        on_filter_apply: Callable[[Optional[int], Optional[int], Optional[int]], None],
        db_manager: DatabaseManager,
    ):
        super().__init__()
        self.on_filter_apply = on_filter_apply
        self.repo_asesores = RepositorioAsesorSQLite(db_manager)

        # Configuración inicial (Fecha actual)
        hoy = datetime.now()
        self.selected_month = hoy.month
        self.selected_year = hoy.year
        self.selected_asesor_id = None

        # UI Elements
        self.dd_mes = self._build_month_dropdown()
        self.dd_anio = self._build_year_dropdown()
        self.dd_asesor = self._build_advisor_dropdown()

        self.content = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.FILTER_LIST, color=ft.Colors.PRIMARY),
                            ft.Text("Filtros:", weight=ft.FontWeight.BOLD),
                            self.dd_mes,
                            self.dd_anio,
                            self.dd_asesor,
                            ft.ElevatedButton(
                                "Aplicar", icon=ft.Icons.CHECK, on_click=self._handle_apply
                            ),
                            ft.IconButton(
                                icon=ft.Icons.REFRESH,
                                tooltip="Reiniciar Filtros",
                                on_click=self._handle_reset,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    padding=10,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=10,
                    shadow=ft.BoxShadow(
                        blur_radius=10, color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK)
                    ),
                )
            ]
        )

    def _build_month_dropdown(self) -> ft.Dropdown:
        meses = [
            (1, "Enero"),
            (2, "Febrero"),
            (3, "Marzo"),
            (4, "Abril"),
            (5, "Mayo"),
            (6, "Junio"),
            (7, "Julio"),
            (8, "Agosto"),
            (9, "Septiembre"),
            (10, "Octubre"),
            (11, "Noviembre"),
            (12, "Diciembre"),
        ]

        return ft.Dropdown(
            label="Mes",
            width=120,
            value=str(self.selected_month),  # Dropdown values are strings
            options=[ft.dropdown.Option(str(k), v) for k, v in meses],
            content_padding=5,
            text_size=12,
        )

    def _build_year_dropdown(self) -> ft.Dropdown:
        anio_actual = datetime.now().year
        anios = range(anio_actual, anio_actual - 5, -1)

        return ft.Dropdown(
            label="Año",
            width=100,
            value=str(self.selected_year),
            options=[ft.dropdown.Option(str(a), str(a)) for a in anios],
            content_padding=5,
            text_size=12,
        )

    def _build_advisor_dropdown(self) -> ft.Dropdown:
        try:
            asesores = self.repo_asesores.listar_todos()
            options = []
            for a in asesores:
                # Usamos el atributo dinámico inyectado en el repositorio
                nombre_mostrar = getattr(a, "nombre_completo", f"Asesor {a.id_asesor}")
                options.append(ft.dropdown.Option(str(a.id_asesor), nombre_mostrar))
        except Exception:
            pass  # print(f"Error cargando asesores: {e}") [OpSec Removed]
            options = []

        return ft.Dropdown(
            label="Asesor",
            width=200,
            hint_text="Todos los asesores",
            options=options,
            content_padding=5,
            text_size=12,
        )

    def _handle_apply(self, e):
        mes = int(self.dd_mes.value) if self.dd_mes.value else None
        anio = int(self.dd_anio.value) if self.dd_anio.value else None
        asesor_id = int(self.dd_asesor.value) if self.dd_asesor.value else None

        self.on_filter_apply(mes, anio, asesor_id)

    def _handle_reset(self, e):
        hoy = datetime.now()
        self.dd_mes.value = str(hoy.month)
        self.dd_anio.value = str(hoy.year)
        self.dd_asesor.value = None

        # Actualizar visualmente los dropdowns
        self.dd_mes.update()
        self.dd_anio.update()
        self.dd_asesor.update()

        # Aplicar filtro por defecto
        self.on_filter_apply(hoy.month, hoy.year, None)
