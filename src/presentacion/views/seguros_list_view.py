"""
Vista: Lista de Seguros
Permite visualizar, buscar y gestionar seguros de arrendamiento.
Refactorizado a UserControl asíncrono.
Adaptado a Flet moderno (sin UserControl).
"""

import flet as ft
import threading
from typing import Callable
from src.presentacion.theme import colors, styles
from src.aplicacion.servicios.servicio_seguros import ServicioSeguros
from src.infraestructura.persistencia.database import DatabaseManager

class SegurosListView(ft.Container):
    def __init__(self, page: ft.Page, on_nuevo_seguro: Callable, on_editar_seguro: Callable[[int], None], on_nueva_poliza: Callable = None):
        super().__init__(expand=True, padding=30, bgcolor=colors.BACKGROUND)
        self.page_ref = page
        self.on_nuevo_seguro = on_nuevo_seguro
        self.on_editar_seguro = on_editar_seguro
        self.on_nueva_poliza = on_nueva_poliza
        
        # Inyección (Internal)
        self.db_manager = DatabaseManager()
        self.servicio = ServicioSeguros(self.db_manager)
        
        # Estado
        self.seguros = []
        self.polizas = []
        self.busqueda_actual = ""
        self.solo_activos = True
        
        # Controls
        self.txt_busqueda = ft.Ref[ft.TextField]()
        self.switch_activos = ft.Ref[ft.Switch]()
        self.loading = ft.ProgressBar(width=400, color=colors.PRIMARY, visible=False)
        
        # TAB 1: Seguros (Catálogo)
        self.tabla_seguros = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Nombre", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Porcentaje", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Estado", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            border=ft.border.all(1, colors.BORDER_DEFAULT),
            border_radius=10,
        )
        
        # TAB 2: Pólizas (Asignaciones)
        self.tabla_polizas = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Contrato", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Inquilino", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Seguro", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Vigencia", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Estado", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            border=ft.border.all(1, colors.BORDER_DEFAULT),
            border_radius=10,
        )

        self.tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="Catálogo de Seguros",
                    icon=ft.Icons.LIST,
                    content=ft.Column([
                        self._build_filters(),
                        ft.Row([self.tabla_seguros], scroll=ft.ScrollMode.AUTO, expand=True)
                    ], expand=True)
                ),
                ft.Tab(
                    text="Pólizas Asignadas",
                    icon=ft.Icons.ASSIGNMENT,
                    content=ft.Column([
                        self._build_polizas_actions(),
                        ft.Row([self.tabla_polizas], scroll=ft.ScrollMode.AUTO, expand=True, vertical_alignment=ft.CrossAxisAlignment.START)
                    ], expand=True)
                ),
            ],
            expand=True,
            on_change=lambda e: self.cargar_datos()
        )

        self.content = ft.Column(
            [
                # Encabezado
                ft.Container(
                    content=ft.Column([
                        ft.Text("Inicio > Seguros", style=styles.breadcrumb_text()),
                        ft.Text("Gestión de Seguros y Pólizas", size=24, weight=ft.FontWeight.BOLD, color=colors.TEXT_PRIMARY),
                    ]),
                    padding=ft.padding.only(bottom=20)
                ),
                # Loading
                ft.Container(content=self.loading, alignment=ft.alignment.center, height=4),
                # Tabs
                self.tabs
            ],
            expand=True
        )

    def _build_filters(self):
        return ft.Row([
            ft.TextField(ref=self.txt_busqueda, hint_text="Buscar seguro...", expand=True, on_submit=lambda e: self.cargar_datos()),
            ft.IconButton(ft.Icons.SEARCH, on_click=lambda e: self.cargar_datos()),
            ft.Switch(ref=self.switch_activos, label="Solo activos", value=True, on_change=lambda e: self.cargar_datos()),
            ft.ElevatedButton("Nuevo Seguro", icon=ft.Icons.ADD, on_click=lambda e: self.on_nuevo_seguro(), bgcolor=colors.PRIMARY, color="white")
        ], spacing=10)

    def _build_polizas_actions(self):
         return ft.Row([
            ft.Text("Listado de Arrendamientos Asegurados", weight="bold", size=16),
            ft.Container(expand=True),
            ft.ElevatedButton("Asignar Póliza", icon=ft.Icons.ADD_LINK, on_click=lambda e: self.on_nueva_poliza(), bgcolor=colors.PRIMARY, color="white")
        ], spacing=10)

    def did_mount(self):
        self.cargar_datos()

    def cargar_datos(self):
        self.loading.visible = True
        self.update()
        threading.Thread(target=self._fetch_data, daemon=True).start()

    def _fetch_data(self):
        try:
            # Cargar Seguros
            activos = self.switch_activos.current.value if self.switch_activos.current else True
            self.seguros = self.servicio.listar_seguros(solo_activos=activos)
            
            # Cargar Polizas (si tab 2)
            if self.tabs.selected_index == 1:
                self.polizas = self.servicio.listar_polizas()
            
            self._update_ui()
        except Exception as e:
            print(f"Error seguros/polizas: {e}")
            self._schedule_error(str(e))

    def _schedule_error(self, error):
        self.loading.visible = False
        self.page_ref.snack_bar = ft.SnackBar(ft.Text(f"Error: {error}"), bgcolor="red")
        self.page_ref.snack_bar.open = True
        self.update()

    def _update_ui(self):
        # 1. Update Tabla Seguros
        self.tabla_seguros.rows = []
        for s in self.seguros:
            self.tabla_seguros.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(str(s.id_seguro))),
                ft.DataCell(ft.Text(s.nombre_seguro)),
                ft.DataCell(ft.Text(f"{s.obtener_porcentaje_decimal()}%")),
                ft.DataCell(ft.Text("Activo" if s.esta_activo() else "Inactivo", color="green" if s.esta_activo() else "red")),
                ft.DataCell(ft.Row([
                    ft.IconButton(ft.Icons.EDIT, icon_color=colors.PRIMARY, on_click=lambda e, id=s.id_seguro: self.on_editar_seguro(id)),
                    ft.IconButton(ft.Icons.TOGGLE_OFF if s.esta_activo() else ft.Icons.TOGGLE_ON, on_click=lambda e, obj=s: self.handle_toggle_estado_seguro(obj))
                ]))
            ]))

        # 2. Update Tabla Polizas
        self.tabla_polizas.rows = []
        if self.tabs.selected_index == 1:
            for p in self.polizas:
                self.tabla_polizas.rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(p.propiedad_info or "N/A", size=12)),
                    ft.DataCell(ft.Text(p.inquilino_info or "N/A", size=12)),
                    ft.DataCell(ft.Text(p.nombre_seguro or "N/A")),
                    ft.DataCell(ft.Column([
                        ft.Text(f"Desde: {p.fecha_inicio}", size=11),
                        ft.Text(f"Hasta: {p.fecha_fin}", size=11, color="red" if p.fecha_fin < datetime.now().strftime("%Y-%m-%d") else "black")
                    ])),
                    ft.DataCell(ft.Container(
                        content=ft.Text(p.estado, size=11, color="white"),
                        bgcolor="green" if p.esta_activa else "grey",
                        padding=5, border_radius=5
                    )),
                    ft.DataCell(ft.IconButton(ft.Icons.CANCEL, tooltip="Cancelar Póliza", icon_color="red", 
                                              on_click=lambda e, id=p.id_poliza: self.cancelar_poliza(id)))
                ]))

        self.loading.visible = False
        self.update()

    def handle_toggle_estado_seguro(self, seguro):
         # Simplificado para brevedad, idealmente usar dialogo
        nuevo_estado = 0 if seguro.esta_activo() else 1
        if nuevo_estado == 0:
             self.servicio.desactivar_seguro(seguro.id_seguro, "Click UI", "admin")
        else:
             self.servicio.activar_seguro(seguro.id_seguro, "admin")
        self.cargar_datos()

    def cancelar_poliza(self, id_poliza):
        # TODO: Dialogo confirm
        try:
            self.servicio.cambiar_estado_poliza(id_poliza, "Cancelada", "admin")
            self.cargar_datos()
        except Exception as e:
            print(e)

def crear_seguros_list_view(page, on_nuevo_seguro, on_editar_seguro, on_nueva_poliza=None):
    return SegurosListView(page, on_nuevo_seguro, on_editar_seguro, on_nueva_poliza)
