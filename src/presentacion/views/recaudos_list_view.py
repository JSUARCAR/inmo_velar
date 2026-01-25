"""
Vista: Lista de Recaudos
Muestra todos los pagos recibidos de inquilinos con filtros y búsqueda.
Refactorizado para carga asíncrona (Optimización 17.3)
Adaptado a Flet moderno (sin UserControl).
"""

import threading
import time
from datetime import datetime
from typing import Callable

import flet as ft

# Integración Fase 4: Paginación
from src.presentacion.components.pagination_manager import PaginationManager
from src.presentacion.theme import colors


class RecaudosListView(ft.Container):
    def __init__(
        self,
        page: ft.Page,
        servicio_financiero,
        on_nuevo_recaudo: Callable,
        on_ver_detalle: Callable[[int], None],
        on_aprobar: Callable[[int], None] = None,
        on_reversar: Callable[[int], None] = None,
    ):
        super().__init__(expand=True, padding=30)
        self.page_ref = page
        self.servicio_financiero = servicio_financiero
        self.on_nuevo_recaudo = on_nuevo_recaudo
        self.on_ver_detalle = on_ver_detalle
        self.on_aprobar = on_aprobar
        self.on_reversar = on_reversar

        # Estado
        self.recaudos = []
        self.cargando = True

        # Paginación
        self.current_page = 1
        self.page_size = 25
        self.total_items = 0

        self.pagination = PaginationManager(
            total_items=0,
            items_per_page=25,
            on_page_change=self._on_page_change,
            on_page_size_change=self._on_page_size_change,
        )

        # Referencias de controles
        self.filtro_estado = ft.Ref[ft.Dropdown]()
        self.filtro_fecha_desde = ft.Ref[ft.TextField]()
        self.filtro_fecha_hasta = ft.Ref[ft.TextField]()
        self.busqueda_ref = ft.Ref[ft.TextField]()
        self.tabla_container = ft.Ref[ft.Column]()

        # DatePickers (se agregan al overlay en did_mount si es seguro, o en __init__ si page es válida)
        # Nota: page ya debería ser válida aquí.
        self.date_picker_desde = ft.DatePicker(
            first_date=datetime(2020, 1, 1),
            last_date=datetime(2030, 12, 31),
            on_change=self.actualizar_fecha_desde,
        )
        self.date_picker_hasta = ft.DatePicker(
            first_date=datetime(2020, 1, 1),
            last_date=datetime(2030, 12, 31),
            on_change=self.actualizar_fecha_hasta,
        )

        # --- Construcción UI (adaptado de build) ---

        # Filtros UI
        filtros_section = ft.Container(
            content=ft.Column(
                [
                    ft.Text("Filtros", size=18, weight=ft.FontWeight.BOLD),
                    ft.Divider(height=1, color="#e0e0e0"),
                    ft.Row(
                        [
                            ft.Dropdown(
                                ref=self.filtro_estado,
                                label="Estado",
                                hint_text="Todos",
                                width=200,
                                options=[
                                    ft.dropdown.Option("Pendiente"),
                                    ft.dropdown.Option("Aplicado"),
                                    ft.dropdown.Option("Reversado"),
                                ],
                            ),
                            ft.TextField(
                                ref=self.filtro_fecha_desde,
                                label="Desde",
                                hint_text="YYYY-MM-DD",
                                width=180,
                                read_only=True,
                                suffix=ft.IconButton(
                                    icon=ft.Icons.CALENDAR_MONTH,
                                    icon_color="#1976d2",
                                    tooltip="Seleccionar fecha",
                                    on_click=lambda e: self.page_ref.open(self.date_picker_desde),
                                ),
                            ),
                            ft.TextField(
                                ref=self.filtro_fecha_hasta,
                                label="Hasta",
                                hint_text="YYYY-MM-DD",
                                width=180,
                                read_only=True,
                                suffix=ft.IconButton(
                                    icon=ft.Icons.CALENDAR_MONTH,
                                    icon_color="#1976d2",
                                    tooltip="Seleccionar fecha",
                                    on_click=lambda e: self.page_ref.open(self.date_picker_hasta),
                                ),
                            ),
                            ft.TextField(
                                ref=self.busqueda_ref,
                                label="Buscar",
                                hint_text="Referencia bancaria...",
                                width=250,
                                prefix_icon=ft.Icons.SEARCH,
                            ),
                            ft.ElevatedButton(
                                "Aplicar",
                                icon=ft.Icons.FILTER_ALT,
                                on_click=lambda e: self._reset_pagination(),
                                bgcolor="#4caf50",
                                color="white",
                            ),
                            ft.OutlinedButton(
                                "Limpiar",
                                icon=ft.Icons.CLEAR,
                                on_click=self.limpiar_filtros,
                            ),
                        ],
                        wrap=True,
                        spacing=10,
                    ),
                ]
            ),
            bgcolor="white",
            padding=20,
            border_radius=8,
            border=ft.border.all(1, "#e0e0e0"),
        )

        self.content = ft.Column(
            [
                # Breadcrumbs
                ft.Row(
                    [
                        ft.Text("Inicio", size=14, color="#666"),
                        ft.Text(" > ", size=14, color="#666"),
                        ft.Text("Recaudos", size=14, weight=ft.FontWeight.BOLD, color="#1976d2"),
                    ]
                ),
                ft.Divider(height=20, color="transparent"),
                # Header
                ft.Row(
                    [
                        ft.Text("Gestión de Recaudos", size=28, weight=ft.FontWeight.BOLD),
                        ft.Container(expand=True),
                        ft.ElevatedButton(
                            "+ Registrar Pago",
                            icon=ft.Icons.ADD,
                            on_click=lambda e: self.on_nuevo_recaudo(),
                            bgcolor="#1976d2",
                            color="white",
                            height=45,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(height=20, color="transparent"),
                filtros_section,
                ft.Divider(height=20, color="transparent"),
                # Tabla Container
                ft.Column(ref=self.tabla_container, spacing=10),
                # Paginación
                ft.Container(content=self.pagination, padding=ft.padding.only(top=10, bottom=20)),
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=0,
        )

    def did_mount(self):
        # Registrar datepickers
        # Verificación extra por seguridad en hilos/contextos complejos
        if self.page_ref and self.page_ref.overlay is not None:
            if self.date_picker_desde not in self.page_ref.overlay:
                self.page_ref.overlay.append(self.date_picker_desde)
            if self.date_picker_hasta not in self.page_ref.overlay:
                self.page_ref.overlay.append(self.date_picker_hasta)
            self.page_ref.update()

        self.cargar_datos()

    def will_unmount(self):
        # Limpiar overlay para no acumular pickers
        if self.page_ref and self.page_ref.overlay is not None:
            if self.date_picker_desde in self.page_ref.overlay:
                self.page_ref.overlay.remove(self.date_picker_desde)
            if self.date_picker_hasta in self.page_ref.overlay:
                self.page_ref.overlay.remove(self.date_picker_hasta)
            self.page_ref.update()

    def actualizar_fecha_desde(self, e):
        if e.control.value:
            self.filtro_fecha_desde.current.value = e.control.value.strftime("%Y-%m-%d")
            self.filtro_fecha_desde.current.update()

    def actualizar_fecha_hasta(self, e):
        if e.control.value:
            self.filtro_fecha_hasta.current.value = e.control.value.strftime("%Y-%m-%d")
            self.filtro_fecha_hasta.current.update()

    def limpiar_filtros(self, e):
        self.filtro_estado.current.value = None
        self.filtro_fecha_desde.current.value = ""
        self.filtro_fecha_hasta.current.value = ""
        self.busqueda_ref.current.value = ""
        self.update()
        self.cargar_datos()

    def cargar_datos(self):
        # Mostrar Loading
        self.tabla_container.current.controls = [
            ft.Container(
                content=ft.Column(
                    [
                        ft.ProgressBar(width=400, color=colors.PRIMARY),
                        ft.Text("Cargando recaudos...", color=colors.TEXT_SECONDARY),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                alignment=ft.alignment.center,
                padding=50,
            )
        ]
        self.tabla_container.current.update()

        filtros = {
            "estado": self.filtro_estado.current.value,
            "desde": self.filtro_fecha_desde.current.value,
            "hasta": self.filtro_fecha_hasta.current.value,
            "busqueda": self.busqueda_ref.current.value,
        }

        threading.Thread(target=self._fetch_data_thread, args=(filtros,), daemon=True).start()

    def _fetch_data_thread(self, filtros):
        try:
            time.time()

            result = self.servicio_financiero.listar_recaudos_paginado(
                page=self.current_page,
                page_size=self.page_size,
                estado=filtros["estado"],
                fecha_desde=filtros["desde"],
                fecha_hasta=filtros["hasta"],
                busqueda=filtros["busqueda"],
            )

            self.recaudos = result.items
            self.total_items = result.total

            self._schedule_ui_update()

        except Exception as e:
            pass  # print(f"Error fetch recaudos: {e}") [OpSec Removed]
            self.recaudos = []
            self.total_items = 0
            self._schedule_ui_update(error=str(e))

        except Exception as e:
            pass  # print(f"Error fetch recaudos: {e}") [OpSec Removed]
            self._schedule_ui_update(error=str(e))

    def _schedule_ui_update(self, error=None):
        if error:
            self.tabla_container.current.controls = [ft.Text(f"Error: {error}", color="red")]
            self.tabla_container.current.update()
            return

        filas = []
        for rec in self.recaudos:
            acciones = [
                ft.IconButton(
                    icon=ft.Icons.VISIBILITY,
                    icon_color="#2196f3",
                    tooltip="Ver Detalle",
                    on_click=lambda e, id_rec=rec["id"]: self.on_ver_detalle(id_rec),
                )
            ]

            if rec["estado"] == "Pendiente":
                if self.on_aprobar:
                    acciones.append(
                        ft.IconButton(
                            icon=ft.Icons.CHECK_CIRCLE,
                            icon_color="green",
                            tooltip="Aprobar (Aplicar)",
                            on_click=lambda e, id_rec=rec["id"]: self.on_aprobar(id_rec),
                        )
                    )
                if self.on_reversar:
                    acciones.append(
                        ft.IconButton(
                            icon=ft.Icons.CANCEL,
                            icon_color="red",
                            tooltip="Reversar (Anular)",
                            on_click=lambda e, id_rec=rec["id"]: self.on_reversar(id_rec),
                        )
                    )

            filas.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(rec["id"]))),
                        ft.DataCell(ft.Text(rec["fecha"])),
                        ft.DataCell(ft.Text(rec["contrato"])),
                        ft.DataCell(ft.Text(f"${rec['valor']:,}")),
                        ft.DataCell(ft.Text(rec["metodo"])),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(
                                    rec["estado"], color="white", size=12, weight=ft.FontWeight.BOLD
                                ),
                                bgcolor={
                                    "Aplicado": "#4caf50",
                                    "Pendiente": "#ff9800",
                                    "Reversado": "#f44336",
                                }.get(rec["estado"], "grey"),
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                border_radius=4,
                            )
                        ),
                        ft.DataCell(ft.Row(acciones)),
                    ]
                )
            )

        if not filas:
            self.tabla_container.current.controls = [
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(ft.Icons.INBOX, size=64, color="#ccc"),
                            ft.Text("No se encontraron recaudos", size=16, color="#999"),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=50,
                    alignment=ft.alignment.center,
                )
            ]
        else:
            tabla = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("ID", weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Fecha", weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Contrato", weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Valor", weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Método", weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Estado", weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.BOLD)),
                ],
                rows=filas,
                border=ft.border.all(1, "#e0e0e0"),
                border_radius=8,
                vertical_lines=ft.border.BorderSide(1, "#f5f5f5"),
                horizontal_lines=ft.border.BorderSide(1, "#f5f5f5"),
                heading_row_color="#f5f5f5",
            )

            self.tabla_container.current.controls = [
                ft.Container(
                    content=ft.Column([tabla], scroll=ft.ScrollMode.AUTO, expand=True),
                    border_radius=8,
                    bgcolor="white",
                    padding=10,
                )
            ]

        self.tabla_container.current.update()

        # Actualizar paginador
        self.pagination.set_total_items(self.total_items)
        self.pagination.set_current_page(self.current_page)
        self.pagination.update()

    def _on_page_change(self, page: int):
        self.current_page = page
        self.cargar_datos()

    def _on_page_size_change(self, page_size: int):
        self.page_size = page_size
        self.current_page = 1
        self.cargar_datos()

    def _reset_pagination(self):
        self.current_page = 1
        self.cargar_datos()


def crear_recaudos_list_view(
    page, servicio_financiero, on_nuevo_recaudo, on_ver_detalle, on_aprobar=None, on_reversar=None
):
    return RecaudosListView(
        page, servicio_financiero, on_nuevo_recaudo, on_ver_detalle, on_aprobar, on_reversar
    )
