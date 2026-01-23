"""
Vista: Lista de Desocupaciones
Muestra desocupaciones en proceso y completadas con progreso visual.
"""

import flet as ft
import threading
from typing import Callable, List

from src.presentacion.theme import colors
from src.presentacion.components.document_manager import DocumentManager
from src.presentacion.components.pagination_manager import PaginationManager


class DesocupacionesListView(ft.Container):
    def __init__(
        self,
        page: ft.Page,
        servicio_desocupaciones,
        servicio_documental,
        on_nueva: Callable,
        on_ver_checklist: Callable[[int], None]
    ):
        super().__init__(expand=True, padding=16) # Reduced padding
        self.page_ref = page
        self.servicio = servicio_desocupaciones
        self.servicio_documental = servicio_documental
        self.on_nueva = on_nueva
        self.on_ver_checklist = on_ver_checklist
        
        self.desocupaciones = []
        
        # Pagination state
        self.current_page = 1
        self.page_size = 25
        self.total_items = 0
        
        # Refs
        self.dd_estado = ft.Ref[ft.Dropdown]()
        self.main_content_ref = ft.Ref[ft.Container]()
        self.txt_total = ft.Ref[ft.Text]()
        
        # Loading
        self.loading_control = ft.Container(
            content=ft.ProgressBar(width=400, color="blue"),
            alignment=ft.alignment.center
        )
        
        # Build UI
        filtros = ft.Row([
            ft.Dropdown(
                ref=self.dd_estado,
                label="Estado",
                width=200,
                options=[
                    ft.dropdown.Option("", "Todos"),
                    ft.dropdown.Option("En Proceso", "En Proceso"),
                    ft.dropdown.Option("Completada", "Completada"),
                    ft.dropdown.Option("Cancelada", "Cancelada")
                ],
                on_change=lambda e: self._on_filtro_change()
            ),
            ft.Container(expand=True),
            ft.IconButton(icon=ft.Icons.REFRESH, tooltip="Actualizar", on_click=lambda e: self.cargar_datos()),
            ft.Text(ref=self.txt_total, value="...", color=ft.Colors.GREY_600)
        ], spacing=12)
        
        # Pagination component
        self.pagination = PaginationManager(
            total_items=0,
            items_per_page=25,
            on_page_change=self._on_page_change,
            on_page_size_change=self._on_page_size_change
        )
        
        self.content = ft.Column([
            # Header
            ft.Row([
                ft.Text("Gestión de Desocupaciones", size=28, weight="bold"),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    "Nueva Desocupación",
                    icon=ft.Icons.ADD_HOME_WORK,
                    on_click=lambda e: self.on_nueva(),
                    style=ft.ButtonStyle(
                        bgcolor=colors.PRIMARY,
                        color=colors.TEXT_ON_PRIMARY,
                        padding=20
                    ),
                    height=45
                )
            ]),
            
            # Filtros
            filtros,
            
            # Tabla (container dinámico)
            ft.Container(
                ref=self.main_content_ref,
                expand=True,
                border=ft.border.all(1, ft.Colors.GREY_200),
                border_radius=8,
                padding=8
            ),
            
            # Pagination
            ft.Container(
                content=self.pagination,
                padding=ft.padding.only(top=10)
            ),
        ], spacing=10, expand=True) # Reduced spacing
    
    def did_mount(self):
        self.cargar_datos()
    
    def _on_filtro_change(self):
        """Handler cuando cambia el filtro de estado."""
        self.current_page = 1  # Reset to page 1 when filter changes
        self.cargar_datos()
    
    def _on_page_change(self, page: int):
        """Handler cuando cambia la página."""
        self.current_page = page
        self.cargar_datos()
    
    def _on_page_size_change(self, page_size: int):
        """Handler cuando cambia el tamaño de página."""
        self.page_size = page_size
        self.current_page = 1
        self.cargar_datos()
    
    def cargar_datos(self):
        if self.main_content_ref.current:
            self.main_content_ref.current.content = self.loading_control
            self.main_content_ref.current.update()
        
        filtro_estado = self.dd_estado.current.value if self.dd_estado.current.value else None
        threading.Thread(target=self._fetch_data, args=(filtro_estado,), daemon=True).start()
    
    def _fetch_data(self, estado):
        try:
            result = self.servicio.listar_desocupaciones_paginado(
                page=self.current_page,
                page_size=self.page_size,
                estado=estado
            )
            self.desocupaciones = result.items
            self.total_items = result.total
            self._schedule_ui_update()
        except Exception as e:
            print(f"Error desocupaciones: {e}")
            self._schedule_ui_update(error=str(e))
    
    def _schedule_ui_update(self, error=None):
        if error:
            if self.main_content_ref.current:
                self.main_content_ref.current.content = ft.Text(f"Error: {error}", color="red")
                self.main_content_ref.current.update()
            return
        
        # Actualizar contador
        if self.txt_total.current:
            self.txt_total.current.value = f"{len(self.desocupaciones)} desocupaciones"
            self.txt_total.current.update()
        
        # Actualizar tabla
        if self.main_content_ref.current:
            self.main_content_ref.current.content = self._crear_tabla()
            self.main_content_ref.current.update()
        
        # Actualizar paginación
        self.pagination.set_total_items(self.total_items)
        self.pagination.set_current_page(self.current_page)
    
    def _crear_tabla(self):
        if not self.desocupaciones:
            return ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.HOME_WORK_OUTLINED, size=60, color=ft.Colors.GREY_400),
                    ft.Text("No hay desocupaciones registradas", size=16, color="grey"),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                alignment=ft.alignment.top_center,
                padding=ft.padding.only(top=50),
                expand=True
            )
        
        rows = []
        for d in self.desocupaciones:
            # Barra de progreso visual
            progreso_bar = ft.ProgressBar(
                value=d.progreso_porcentaje / 100,
                width=120,
                height=8,
                color=ft.Colors.GREEN if d.progreso_porcentaje == 100 else ft.Colors.BLUE,
                bgcolor=ft.Colors.GREY_300
            )
            
            progreso_col = ft.Column([
                ft.Text(f"{d.progreso_porcentaje}%", size=12, weight="bold"),
                progreso_bar
            ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            
            # Estado con color
            estado_chip = self._get_estado_chip(d.estado)
            
            # Action Menu
            actions_menu = ft.PopupMenuButton(
                icon=ft.Icons.MORE_VERT,
                tooltip="Acciones",
                items=[
                    ft.PopupMenuItem(
                        text="Ver Checklist" if d.esta_en_proceso else "Ver Detalles",
                        icon=ft.Icons.CHECKLIST if d.esta_en_proceso else ft.Icons.VISIBILITY,
                        on_click=lambda e, id=d.id_desocupacion: self.on_ver_checklist(id)
                    ),
                    ft.PopupMenuItem(
                        text="Gestionar Documentos",
                        icon=ft.Icons.FOLDER_OPEN,
                        on_click=lambda e, id=d.id_desocupacion: self._mostrar_gestor_documentos(id)
                    )
                ]
            )
            
            rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(d.direccion_propiedad or "-", max_lines=2)),
                ft.DataCell(ft.Text(d.nombre_inquilino or "-")),
                ft.DataCell(ft.Text(d.fecha_programada)),
                ft.DataCell(ft.Text(d.fecha_real if d.fecha_real else "-", color="grey")),
                ft.DataCell(progreso_col),
                ft.DataCell(estado_chip),
                ft.DataCell(ft.Row([actions_menu], alignment=ft.MainAxisAlignment.CENTER))
            ]))
        
        tabla = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Propiedad")),
                ft.DataColumn(ft.Text("Inquilino")),
                ft.DataColumn(ft.Text("Fecha Programada")),
                ft.DataColumn(ft.Text("Fecha Real")),
                ft.DataColumn(ft.Text("Progreso")),
                ft.DataColumn(ft.Text("Estado")),
                ft.DataColumn(ft.Text("Acciones"))
            ],
            rows=rows,
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=8
        )
        
        return ft.Column([
            ft.Row([tabla], scroll=ft.ScrollMode.AUTO)
        ], alignment=ft.MainAxisAlignment.START, expand=True)
    
    def _get_estado_chip(self, estado: str):
        """Crea chip visual para estado."""
        color_map = {
            'En Proceso': (ft.Colors.BLUE_100, ft.Colors.BLUE_800),
            'Completada': (ft.Colors.GREEN_100, ft.Colors.GREEN_800),
            'Cancelada': (ft.Colors.RED_100, ft.Colors.RED_800)
        }
        bg, fg = color_map.get(estado, (ft.Colors.GREY_100, ft.Colors.GREY_800))
        
        return ft.Container(
            content=ft.Text(estado, color=fg, size=12),
            bgcolor=bg,
            padding=ft.padding.symmetric(horizontal=12, vertical=6),
            border_radius=12
        )
    
    def _mostrar_gestor_documentos(self, id_desocupacion):
        """Muestra el DocumentManager en un diálogo."""
        
        # Referencia para el diálogo
        dlg_container = [None]
        
        def cerrar_dialogo(e):
             if dlg_container[0]:
                 self.page_ref.close(dlg_container[0])

        
        content = ft.Container(
            content=DocumentManager(
                entidad_tipo="DESOCUPACION",
                entidad_id=str(id_desocupacion),
                page=self.page_ref,
                height=400 # Altura fija para scroll interno
            ),
            width=800, # Ancho suficiente para la tabla
            padding=10
        )
        
        dlg = ft.AlertDialog(
            title=ft.Text(f"Documentos - Desocupación #{id_desocupacion}"),
            content=content,
            actions=[
                ft.TextButton("Cerrar", on_click=cerrar_dialogo)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            modal=True 
        )
        
        dlg_container[0] = dlg
        self.page_ref.open(dlg)


def crear_desocupaciones_list_view(page, servicio_desocupaciones, servicio_documental, on_nueva, on_ver_checklist):
    return DesocupacionesListView(page, servicio_desocupaciones, servicio_documental, on_nueva, on_ver_checklist)
