"""
Vista: Listado de Contratos
Permite visualizar y gestionar Contratos de Mandato y Arrendamiento.
Refactorizado para carga asíncrona (Optimización 17.3)
Adaptado a Flet moderno (sin UserControl).
"""

import flet as ft
import time
import threading
from typing import Callable, Optional, List
from src.presentacion.theme import colors, styles

# Integración Fase 4: Paginación
from src.presentacion.components.pagination_manager import PaginationManager

class ContratosListView(ft.Container):
    def __init__(
        self,
        page: ft.Page,
        servicio_contratos,
        on_nuevo_mandato: Callable,
        on_nuevo_arriendo: Callable,
        on_editar_mandato: Callable[[int], None],
        on_editar_arriendo: Callable[[int], None],
        on_renovar_mandato: Callable[[int], None], 
        on_renovar_arriendo: Callable[[int], None], 
        on_terminar_mandato: Callable[[int], None],
        on_terminar_arriendo: Callable[[int], None],
        on_ver_detalle: Callable[[str, int], None]
    ):
        super().__init__(expand=True, padding=30, bgcolor=colors.BACKGROUND)
        self.page_ref = page
        self.servicio_contratos = servicio_contratos
        self.on_nuevo_mandato = on_nuevo_mandato
        self.on_nuevo_arriendo = on_nuevo_arriendo
        self.on_editar_mandato = on_editar_mandato
        self.on_editar_arriendo = on_editar_arriendo
        self.on_renovar_mandato = on_renovar_mandato
        self.on_renovar_arriendo = on_renovar_arriendo
        self.on_terminar_mandato = on_terminar_mandato
        self.on_terminar_arriendo = on_terminar_arriendo
        self.on_ver_detalle = on_ver_detalle
        
        # Estado
        self.active_tab = "MANDATOS" # MANDATOS o ARRIENDOS
        self.contratos_actuales = []
        self.cargando = True
        
        # Paginación
        self.current_page = 1
        self.page_size = 25
        self.total_items = 0
        
        self.pagination = PaginationManager(
            total_items=0,
            items_per_page=25,
            on_page_change=self._on_page_change,
            on_page_size_change=self._on_page_size_change
        )
        
        # Controles
        self.search_field = ft.Ref[ft.TextField]()
        self.status_dropdown = ft.Ref[ft.Dropdown]()
        
        self.tabla_mandatos = ft.DataTable(
            heading_row_color=colors.SURFACE,
            data_row_color={ft.ControlState.HOVERED: colors.SURFACE_VARIANT},
            border=ft.border.all(1, colors.BORDER_DEFAULT),
            border_radius=8,
            width=float('inf'),
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Propiedad")),
                ft.DataColumn(ft.Text("Propietario")),
                ft.DataColumn(ft.Text("Canon")),
                ft.DataColumn(ft.Text("Vigencia")),
                ft.DataColumn(ft.Text("Estado")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=[]
        )
        
        self.tabla_arriendos = ft.DataTable(
            heading_row_color=colors.SURFACE,
            data_row_color={ft.ControlState.HOVERED: colors.SURFACE_VARIANT},
            border=ft.border.all(1, colors.BORDER_DEFAULT),
            border_radius=8,
            width=float('inf'),
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Propiedad")),
                ft.DataColumn(ft.Text("Inquilino")),
                ft.DataColumn(ft.Text("Canon")),
                ft.DataColumn(ft.Text("Vigencia")),
                ft.DataColumn(ft.Text("Estado")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=[]
        )
        
        self.container_loading = ft.Container(
            content=ft.Column([
                ft.ProgressBar(width=400, color=colors.PRIMARY),
                ft.Text("Cargando contratos...", color=colors.TEXT_SECONDARY)
            ], alignment=ft.MainAxisAlignment.CENTER),
            alignment=ft.alignment.center,
            visible=False
        )

        # --- Construcción UI (adaptado de build) ---

        # Campos
        txt_buscar = ft.TextField(
            ref=self.search_field,
            label="Buscar",
            hint_text="Propiedad, Inquilino, Propietario...",
            prefix_icon=ft.Icons.SEARCH,
            width=300,
            height=40,
            text_size=14,
            content_padding=10,
            on_submit=lambda e: self._reset_pagination()
        )
        
        dd_status = ft.Dropdown(
            ref=self.status_dropdown,
            label="Estado",
            width=150,
            text_size=14,
            content_padding=10,
            options=[
                ft.dropdown.Option("Activo", "Activos"),
                ft.dropdown.Option("Cancelado", "Cancelados"),
                ft.dropdown.Option("Todos", "Todos"),
            ],
            value="Activo",
            on_change=lambda e: self._reset_pagination()
        )

        # Tabs
        self.tabs_content = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            on_change=self._on_tab_change,
            tabs=[
                ft.Tab(
                    text="Mandatos (Propietarios)",
                    icon=ft.Icons.DOMAIN,
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("Listado de contratos de mandato activos e históricos.", color=colors.TEXT_SECONDARY),
                            ft.Column([self.tabla_mandatos], scroll=ft.ScrollMode.AUTO, height=500, expand=True)
                        ], expand=True),
                        padding=20
                    )
                ),
                ft.Tab(
                    text="Arrendamientos (Inquilinos)",
                    icon=ft.Icons.PEOPLE,
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("Listado de contratos de arrendamiento activos e históricos.", color=colors.TEXT_SECONDARY),
                            ft.Column([self.tabla_arriendos], scroll=ft.ScrollMode.AUTO, height=500, expand=True)
                        ], expand=True),
                        padding=20
                    )
                ),
            ],
            expand=True
        )

        
        # Referencia principal
        self.main_content_ref = ft.Ref[ft.Container]()
        
        # Layout
        self.content = ft.Column(
            [
                # Header
                ft.Container(
                    content=ft.Column([
                        ft.Text("Inicio > Contratos", style=styles.breadcrumb_text()),
                        ft.Text("Gestión de Contratos", style=styles.heading_1()),
                    ]),
                    padding=ft.padding.only(bottom=20)
                ),
                
                # Actions & Filtros
                ft.Container(
                    content=ft.Row(
                        [
                            ft.ElevatedButton(
                                "Nuevo Mandato",
                                icon=ft.Icons.ADD,
                                on_click=lambda e: self.on_nuevo_mandato(),
                                style=styles.button_primary()
                            ),
                            ft.ElevatedButton(
                                "Nuevo Arriendo",
                                icon=ft.Icons.ADD_HOME,
                                on_click=lambda e: self.on_nuevo_arriendo(),
                                style=styles.button_secondary()
                            ),
                            ft.Row([
                                txt_buscar,
                                dd_status,
                            ], alignment=ft.MainAxisAlignment.END),
                        ],
                        alignment=ft.MainAxisAlignment.END,
                        spacing=10
                    ),
                    padding=ft.padding.only(bottom=10)
                ),
                
                ft.Divider(height=1, color=colors.BORDER_DEFAULT),
                
                # REFACTOR: Usamos un Container principal y cambiamos su contenido
                # en lugar de un Stack
                ft.Container(
                    ref=self.main_content_ref,
                    expand=True
                ),
                
                # Paginación (compartida)
                ft.Container(
                    content=self.pagination,
                    padding=ft.padding.only(top=10)
                )
            ],
            expand=True,
            spacing=10
        )

    def did_mount(self):
        self.cargar_datos()

    def cargar_datos(self):
        self.cargando = True
        
        # Mostrar Loading reemplazando el contenido
        if self.main_content_ref.current:
            self.main_content_ref.current.content = self.container_loading
            self.main_content_ref.current.update()
        
        # Filtros
        filtro_texto = self.search_field.current.value.strip() if self.search_field.current else None
        filtro_estado = self.status_dropdown.current.value if self.status_dropdown.current else None
        
        filtros = {
            'estado': filtro_estado,
            'busqueda': filtro_texto
        }
        
        threading.Thread(target=self._fetch_data_thread, args=(filtros,), daemon=True).start()

    def _fetch_data_thread(self, filtros):
        try:
            start_time = time.time()
            result = None
            
            if self.active_tab == "MANDATOS":
                result = self.servicio_contratos.listar_mandatos_paginado(
                    page=self.current_page,
                    page_size=self.page_size,
                    estado=filtros['estado'],
                    busqueda=filtros['busqueda']
                )
            else:
                result = self.servicio_contratos.listar_arrendamientos_paginado(
                    page=self.current_page,
                    page_size=self.page_size,
                    estado=filtros['estado'],
                    busqueda=filtros['busqueda']
                )
                
            elapsed = time.time() - start_time
            self.contratos_actuales = result.items
            self.total_items = result.total
            
            self._schedule_ui_update()
            
        except Exception as e:
            pass  # print(f"Error cargando contratos: {e}") [OpSec Removed]
            self.contratos_actuales = []
            self.total_items = 0
            self._schedule_ui_update()

    def _schedule_ui_update(self):
        self.cargando = False
        
        # Actualizar filas de tablas (en memoria)
        self.actualizar_tablas()
            
        # Actualizar paginador
        self.pagination.set_total_items(self.total_items)
        self.pagination.set_current_page(self.current_page)
        
        # Restaurar Tabs y actualizar container
        if self.main_content_ref.current:
            self.main_content_ref.current.content = self.tabs_content
            self.main_content_ref.current.update()

    def _on_tab_change(self, e):
        index = e.control.selected_index
        nuevo_tab = "MANDATOS" if index == 0 else "ARRIENDOS"
        
        if nuevo_tab != self.active_tab:
            self.active_tab = nuevo_tab
            self.current_page = 1 # Reset pagina al cambiar tab
            self.cargar_datos()

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

    def construir_fila_mandato(self, m):
        return ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(str(m['id']))),
                ft.DataCell(ft.Text(m['propiedad'][:30] + "..." if len(m['propiedad']) > 30 else m['propiedad'])),
                ft.DataCell(ft.Text(m['propietario'])),
                ft.DataCell(ft.Text(f"${m['canon']:,.0f}".replace(",", "."))),
                ft.DataCell(ft.Text(f"{m['fecha_inicio']} / {m['fecha_fin']}")),
                ft.DataCell(
                    ft.Container(
                        content=ft.Text(m['estado'], color=colors.TEXT_PRIMARY, size=12),
                        bgcolor=colors.SUCCESS_LIGHT if m['estado'] == 'Activo' else colors.ERROR_LIGHT,
                        padding=5,
                        border_radius=5
                    )
                ),
                ft.DataCell(
                    ft.Row([
                        ft.IconButton(
                            icon=ft.Icons.EDIT, 
                            icon_color=colors.PRIMARY,
                            tooltip="Editar Mandato",
                            on_click=lambda e, id=m['id']: self.on_editar_mandato(id)
                        ),
                        ft.IconButton(
                            icon=ft.Icons.AUTORENEW,
                            icon_color=colors.SECONDARY,
                            tooltip="Renovar Mandato",
                            disabled=m['estado'] != 'Activo',
                            on_click=lambda e, id=m['id']: self.on_renovar_mandato(id)
                        ),
                        ft.IconButton(
                            icon=ft.Icons.BLOCK,
                            icon_color=colors.ERROR,
                            tooltip="Terminar Mandato",
                            disabled=m['estado'] != 'Activo',
                            on_click=lambda e, id=m['id']: self.on_terminar_mandato(id)
                        ),
                        ft.IconButton(
                            icon=ft.Icons.VISIBILITY, 
                            icon_color=colors.TEXT_SECONDARY,
                            tooltip="Ver Detalle",
                            on_click=lambda e, id=m['id']: self.on_ver_detalle("MANDATO", id)
                        )
                    ])
                ),
            ]
        )

    def construir_fila_arriendo(self, a):
        return ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(str(a['id']))),
                ft.DataCell(ft.Text(a['propiedad'][:30] + "..." if len(a['propiedad']) > 30 else a['propiedad'])),
                ft.DataCell(ft.Text(a['arrendatario'])),
                ft.DataCell(ft.Text(f"${a['canon']:,.0f}".replace(",", "."))),
                ft.DataCell(ft.Text(f"{a['fecha_inicio']} / {a['fecha_fin']}")),
                ft.DataCell(
                    ft.Container(
                        content=ft.Text(a['estado'], color=colors.TEXT_PRIMARY, size=12),
                        bgcolor=colors.SUCCESS_LIGHT if a['estado'] == 'Activo' else colors.ERROR_LIGHT,
                        padding=5,
                        border_radius=5
                    )
                ),
                ft.DataCell(
                    ft.Row([
                        ft.IconButton(
                            icon=ft.Icons.EDIT, 
                            icon_color=colors.PRIMARY,
                            tooltip="Editar Arriendo",
                            on_click=lambda e, id=a['id']: self.on_editar_arriendo(id)
                        ),
                        ft.IconButton(
                            icon=ft.Icons.AUTORENEW,
                            icon_color=colors.SECONDARY,
                            tooltip="Renovar Contrato",
                            disabled=a['estado'] != 'Activo',
                            on_click=lambda e, id=a['id']: self.on_renovar_arriendo(id)
                        ),
                        ft.IconButton(
                            icon=ft.Icons.BLOCK,
                            icon_color=colors.ERROR,
                            tooltip="Terminar Arriendo",
                            disabled=a['estado'] != 'Activo',
                            on_click=lambda e, id=a['id']: self.on_terminar_arriendo(id)
                        ),
                        ft.IconButton(
                            icon=ft.Icons.VISIBILITY, 
                            icon_color=colors.TEXT_SECONDARY,
                            tooltip="Ver Detalle",
                            on_click=lambda e, id=a['id']: self.on_ver_detalle("ARRIENDO", id)
                        )
                    ])
                ),
            ]
        )

    def actualizar_tablas(self):
        # Limpiar ambas tablas primero
        self.tabla_mandatos.rows = []
        self.tabla_arriendos.rows = []
        
        if self.active_tab == "MANDATOS":
            self.tabla_mandatos.rows = [self.construir_fila_mandato(m) for m in self.contratos_actuales]
        else:
             self.tabla_arriendos.rows = [self.construir_fila_arriendo(a) for a in self.contratos_actuales]
        
        # NOTA: No llamamos .update() aquí explícitamente porque 
        # al hacer swap del container padre, se repintará todo.

def crear_contratos_list_view(page, servicio_contratos, on_nuevo_mandato, on_nuevo_arriendo, on_editar_mandato, on_editar_arriendo, on_renovar_mandato, on_renovar_arriendo, on_terminar_mandato, on_terminar_arriendo, on_ver_detalle):
    return ContratosListView(
        page, 
        servicio_contratos, 
        on_nuevo_mandato, 
        on_nuevo_arriendo, 
        on_editar_mandato, 
        on_editar_arriendo,
        on_renovar_mandato,
        on_renovar_arriendo,
        on_terminar_mandato,
        on_terminar_arriendo,
        on_ver_detalle
    )
