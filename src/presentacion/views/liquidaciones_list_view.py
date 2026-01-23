"""
Vista: Lista de Liquidaciones (Agrupadas por Propietario)
Muestra estados de cuenta mensuales agrupados por propietario con filtros por período y estado.
Refactorizado para mostrar liquidaciones consolidadas por propietario.
Adaptado a Flet moderno (sin UserControl).
"""

import flet as ft
import time
import threading
from typing import Callable, Optional, List
from src.presentacion.theme import colors, styles

# Integración Fase 4: Paginación
from src.presentacion.components.pagination_manager import PaginationManager

class LiquidacionesListView(ft.Container):
    def __init__(
        self,
        page: ft.Page,
        servicio_financiero,
        on_nueva_liquidacion: Callable,
        on_ver_detalle: Callable[[int, str], None],  # Cambiado: ahora recibe (id_propietario, periodo)
        on_aprobar: Callable[[int, str], None],  # Cambiado: ahora recibe (id_propietario, periodo)
        on_marcar_pagada: Callable[[int, str], None],  # Cambiado: ahora recibe (id_propietario, periodo)
        on_editar: Callable[[int, str], None]  # Nuevo: permite editar liquidaciones en proceso
    ):
        super().__init__(expand=True, padding=30)
        self.page_ref = page
        self.servicio_financiero = servicio_financiero
        self.on_nueva_liquidacion = on_nueva_liquidacion
        self.on_ver_detalle = on_ver_detalle
        self.on_aprobar = on_aprobar
        self.on_marcar_pagada = on_marcar_pagada
        self.on_editar = on_editar
        
        # Estado
        self.liquidaciones_data = [] # Lista completa
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
        
        # Controles Ref
        self.filtro_estado = ft.Ref[ft.Dropdown]()
        self.filtro_periodo = ft.Ref[ft.TextField]()
        self.busqueda_ref = ft.Ref[ft.TextField]()
        self.tabla_container = ft.Ref[ft.Column]()

        # --- Construcción UI (adaptado de build) ---

        # Filtros UI
        filtros_section = ft.Container(
            content=ft.Column([
                ft.Text("Filtros", size=18, weight=ft.FontWeight.BOLD),
                ft.Divider(height=1, color="#e0e0e0"),
                ft.Row([
                    ft.Dropdown(
                        ref=self.filtro_estado,
                        label="Estado",
                        hint_text="Todos",
                        width=200,
                        options=[
                            ft.dropdown.Option("En Proceso"),
                            ft.dropdown.Option("Aprobada"),
                            ft.dropdown.Option("Pagada"),
                            ft.dropdown.Option("Cancelada"),
                        ]
                    ),
                    ft.TextField(
                        ref=self.filtro_periodo,
                        label="Período",
                        hint_text="YYYY-MM",
                        width=150,
                    ),
                    ft.TextField(
                        ref=self.busqueda_ref,
                        label="Buscar Propietario",
                        hint_text="Nombre o documento...",
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
                ], wrap=True, spacing=10),
            ]),
            bgcolor="white",
            padding=20,
            border_radius=8,
            border=ft.border.all(1, "#e0e0e0"),
        )
        
        # Leyenda Colors
        leyenda = ft.Container(
            content=ft.Row([
                ft.Text("Estados:", size=12, weight=ft.FontWeight.BOLD, color="#666"),
                self._crear_badge_leyenda("En Proceso", "#ff9800"),
                self._crear_badge_leyenda("Aprobada", "#2196f3"),
                self._crear_badge_leyenda("Pagada", "#4caf50"),
                self._crear_badge_leyenda("Cancelada", "#f44336"),
                self._crear_badge_leyenda("Mixto", "#9c27b0"),
            ], spacing=10),
            padding=10,
            bgcolor="#f5f5f5",
            border_radius=4,
        )

        self.content = ft.Column([
            # Breadcrumbs
            ft.Row([
                ft.Text("Inicio", size=14, color="#666"),
                ft.Text(" > ", size=14, color="#666"),
                ft.Text("Liquidaciones", size=14, weight=ft.FontWeight.BOLD, color="#1976d2"),
            ]),
            ft.Divider(height=20, color="transparent"),
            
            # Header
            ft.Row([
                ft.Text("Gestión de Liquidaciones", size=28, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    "+ Nueva Liquidación",
                    icon=ft.Icons.ADD,
                    on_click=lambda e: self.on_nueva_liquidacion(),
                    bgcolor="#1976d2",
                    color="white",
                    height=45,
                ),
                ft.ElevatedButton(
                    "Generar Masivas",
                    icon=ft.Icons.AUTORENEW,
                    on_click=lambda e: self._abrir_dialogo_masivas(),
                    bgcolor="#ff9800",
                    color="white",
                    tooltip="Generar liquidaciones para múltiples propietarios",
                    height=45,
                ),
            ],
            alignment=ft.MainAxisAlignment.END,
            spacing=10
            ),
            
            ft.Divider(height=20, color="transparent"),
            filtros_section,
            ft.Divider(height=20, color="transparent"),
            leyenda,
            ft.Divider(height=10, color="transparent"),
            
            ft.Column(ref=self.tabla_container, spacing=10),
            
            # Paginación
            ft.Container(
                content=self.pagination,
                padding=ft.padding.only(top=10, bottom=20)
            )
            
        ], scroll=ft.ScrollMode.AUTO, spacing=0)

    def _crear_badge_leyenda(self, texto, color):
        return ft.Container(
            content=ft.Text(texto, color="white", size=10),
            bgcolor=color,
            padding=5,
            border_radius=3
        )

    def did_mount(self):
        self.cargar_datos()

    def limpiar_filtros(self, e):
        self.filtro_estado.current.value = None
        self.filtro_periodo.current.value = ""
        self.busqueda_ref.current.value = ""
        self.update()
        self.cargar_datos()

    def cargar_datos(self):
        # Loading state
        self.tabla_container.current.controls = [
             ft.Container(
                content=ft.Column([
                    ft.ProgressBar(width=400, color=colors.PRIMARY),
                    ft.Text("Cargando liquidaciones...", color=colors.TEXT_SECONDARY)
                ], alignment=ft.MainAxisAlignment.CENTER),
                alignment=ft.alignment.center,
                padding=50
            )
        ]
        self.tabla_container.current.update()
        
        filtros = {
            'estado': self.filtro_estado.current.value,
            'periodo': self.filtro_periodo.current.value,
            'busqueda': self.busqueda_ref.current.value
        }
        
        threading.Thread(target=self._fetch_data_thread, args=(filtros,), daemon=True).start()

    def _fetch_data_thread(self, filtros):
        try:
            start_time = time.time()
            
            result = self.servicio_financiero.listar_liquidaciones_propietarios_paginado(
                page=self.current_page,
                page_size=self.page_size,
                estado=filtros['estado'],
                periodo=filtros['periodo'],
                busqueda=filtros['busqueda']
            )
            
            self.liquidaciones_data = result.items
            self.total_items = result.total
            
            self._schedule_ui_update()
            
        except Exception as e:
            print(f"Error loadings liquidaciones: {e}")
            self.liquidaciones_data = []
            self.total_items = 0
            self._schedule_ui_update(error=str(e))

    def _schedule_ui_update(self, error=None):
        if error:
            self.tabla_container.current.controls = [ft.Text(f"Error: {error}", color="red")]
            self.tabla_container.current.update()
            return
            
        if not self.liquidaciones_data:
            self.tabla_container.current.controls = [
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.INBOX, size=64, color="#ccc"),
                        ft.Text("No se encontraron resultados", size=16, color="#999"),
                        ft.Text("Intenta ajustar los filtros", size=12, color="#ccc")
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    padding=50,
                    alignment=ft.alignment.center
                )
            ]
            self.tabla_container.current.update()
            return
            
        filas = []
        for liq in self.liquidaciones_data:
            acciones = []
            
            # Acciones según estado
            if liq['estado'] == 'En Proceso':
                # Editar - Solo para liquidaciones en proceso
                acciones.append(
                    ft.IconButton(
                        icon=ft.Icons.EDIT,
                        icon_color="#ff9800",
                        tooltip="Editar Liquidación",
                        on_click=lambda e, id_prop=liq['id_propietario'], per=liq['periodo']: self.on_editar(id_prop, per)
                    )
                )
                # Aprobar
                acciones.append(
                    ft.IconButton(
                        icon=ft.Icons.CHECK_CIRCLE,
                        icon_color="#4caf50",
                        tooltip="Aprobar Todas",
                        on_click=lambda e, id_prop=liq['id_propietario'], per=liq['periodo']: self.on_aprobar(id_prop, per)
                    )
                )
            elif liq['estado'] == 'Aprobada':
                acciones.append(
                    ft.IconButton(
                        icon=ft.Icons.ATTACH_MONEY,
                        icon_color="#2196f3",
                        tooltip="Marcar como Pagada",
                        on_click=lambda e, id_prop=liq['id_propietario'], per=liq['periodo']: self.on_marcar_pagada(id_prop, per)
                    )
                )
            
            # Ver detalle siempre
            acciones.append(
                ft.IconButton(
                    icon=ft.Icons.VISIBILITY,
                    icon_color="#616161",
                    tooltip="Ver Detalle",
                    on_click=lambda e, id_prop=liq['id_propietario'], per=liq['periodo']: self.on_ver_detalle(id_prop, per)
                )
            )

            filas.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(liq['nombre_propietario'])),
                        ft.DataCell(ft.Text(liq['documento'])),
                        ft.DataCell(ft.Text(liq['periodo'])),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(str(liq['cantidad_contratos']), weight=ft.FontWeight.BOLD),
                                bgcolor="#e3f2fd",
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                border_radius=4
                            )
                        ),
                        ft.DataCell(ft.Text(f"${liq['total_canon']:,}")),
                        ft.DataCell(ft.Text(f"${liq['neto_total']:,}", weight=ft.FontWeight.BOLD, color="#1976d2")),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(liq['estado'], color="white", size=12, weight=ft.FontWeight.BOLD),
                                bgcolor=self._get_estado_color(liq['estado']),
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                border_radius=4
                            )
                        ),
                        ft.DataCell(ft.Row(acciones, spacing=5)),
                    ]
                )
            )

        tabla = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Propietario", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Documento", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Período", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("# Contratos", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Canon Total", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Neto a Pagar", weight=ft.FontWeight.BOLD)),
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
                content=tabla,
                border_radius=8,
                bgcolor="white",
                padding=10
            )
        ]
        self.tabla_container.current.update()
        
        # Paginador
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

    def _get_estado_color(self, estado):
        return {
            'En Proceso': '#ff9800',
            'Aprobada': '#2196f3',
            'Pagada': '#4caf50',
            'Cancelada': '#f44336',
            'Mixto': '#9c27b0'  # Púrpura para estado mixto
        }.get(estado, '#9e9e9e')
    
    def _abrir_dialogo_masivas(self):
        """Abre diálogo para generación masiva de liquidaciones"""
        from datetime import datetime
        
        # Referencias para los controles
        txt_periodo = ft.Ref[ft.TextField]()
        dropdown_asesor = ft.Ref[ft.Dropdown]()
        txt_progress = ft.Ref[ft.Text]()
        progress_bar = ft.Ref[ft.ProgressBar]()
        
        # Obtener período actual por defecto
        periodo_actual = datetime.now().strftime("%Y-%m")
        
        def cerrar_dialogo(e):
            self.page_ref.close(dlg)
        
        def generar_masivas(e):
            """Ejecuta la generación masiva"""
            if not txt_periodo.current.value:
                txt_periodo.current.error_text = "El período es obligatorio"
                txt_periodo.current.update()
                return
            
            periodo = txt_periodo.current.value
            filtro_asesor = dropdown_asesor.current.value if dropdown_asesor.current.value != "Todos" else None
            
            # Mostrar barra de progreso
            txt_progress.current.value = "Generando liquidaciones..."
            progress_bar.current.visible = True
            txt_progress.current.update()
            progress_bar.current.update()
            
            # Llamar al servicio en un thread para no bloquear UI
            import threading
            
            def _generar_thread():
                try:
                    # Obtener usuario de session (solo acepta 1 argumento)
                    usuario = self.page_ref.session.get("usuario") or "sistema"
                    
                    # Convertir filtro_asesor a int si existe
                    filtro_asesor_int = int(filtro_asesor) if filtro_asesor else None
                    
                    # Llamar al servicio
                    liquidaciones = self.servicio_financiero.generar_liquidaciones_masivas(
                        periodo=periodo,
                        filtro_asesor=filtro_asesor_int,
                        usuario_sistema=usuario
                    )
                    
                    # Actualizar UI en el hilo principal - debe ser async
                    async def _actualizar_ui_exito():
                        self.page_ref.close(dlg)
                        self.page_ref.snack_bar = ft.SnackBar(
                            content=ft.Text(f"✅ {len(liquidaciones)} liquidación(es) generada(s) exitosamente"),
                            bgcolor="#4caf50"
                        )
                        self.page_ref.snack_bar.open = True
                        self.page_ref.update()
                        # Recargar la tabla
                        self.cargar_datos()
                    
                    self.page_ref.run_task(_actualizar_ui_exito)
                    
                except Exception as ex:
                    # CRITICAL: Capturar el mensaje ANTES de definir async function
                    # para evitar NameError por scope de closure
                    error_message = str(ex)
                    
                    async def _actualizar_ui_error():
                        txt_progress.current.value = f"Error: {error_message}"
                        txt_progress.current.color = "red"
                        progress_bar.current.visible = False
                        txt_progress.current.update()
                        progress_bar.current.update()
                    
                    self.page_ref.run_task(_actualizar_ui_error)
            
            threading.Thread(target=_generar_thread, daemon=True).start()
        
        # Obtener asesores para el dropdown
        # Por ahora, lista simple - en producción debería venir del servicio
        opciones_asesores = [
            ft.dropdown.Option("Todos", "Todos los asesores"),
        ]
        
        # Contenido del diálogo
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.AUTORENEW, color="#ff9800"),
                ft.Text("Generación Masiva de Liquidaciones", weight=ft.FontWeight.BOLD)
            ]),
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        "Genera liquidaciones consolidadas para todos los propietarios con contratos activos.",
                        size=13,
                        color="#666"
                    ),
                    ft.Divider(),
                    ft.TextField(
                        ref=txt_periodo,
                        label="Período *",
                        hint_text="YYYY-MM (ej: 2026-01)",
                        value=periodo_actual,
                        prefix_icon=ft.Icons.CALENDAR_MONTH,
                        autofocus=True,
                    ),
                    ft.Dropdown(
                        ref=dropdown_asesor,
                        label="Filtrar por Asesor (Opcional)",
                        hint_text="Seleccione un asesor",
                        options=opciones_asesores,
                        value="Todos",
                    ),
                    ft.Container(height=10),
                    ft.Container(
                        content=ft.Column([
                            ft.Text(
                                ref=txt_progress,
                                value="",
                                size=12,
                                color="#666"
                            ),
                            ft.ProgressBar(ref=progress_bar, visible=False),
                        ]),
                        padding=ft.padding.only(top=10)
                    ),
                    ft.Divider(),
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.INFO, size=16, color="#2196f3"),
                            ft.Text(
                                "Se generará UNA liquidación consolidada por cada propietario que tenga contratos activos.",
                                size=11,
                                italic=True,
                                color="#666",
                                expand=True
                            )
                        ]),
                        bgcolor="#e3f2fd",
                        padding=8,
                        border_radius=4
                    ),
                ], tight=True, spacing=10),
                width=500
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=cerrar_dialogo),
                ft.ElevatedButton(
                    "Generar Liquidaciones",
                    icon=ft.Icons.CHECK,
                    on_click=generar_masivas,
                    bgcolor="#ff9800",
                    color="white"
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page_ref.open(dlg)

def crear_liquidaciones_list_view(page, servicio_financiero, on_nueva_liquidacion, on_ver_detalle, on_aprobar, on_marcar_pagada, on_editar):
    return LiquidacionesListView(page, servicio_financiero, on_nueva_liquidacion, on_ver_detalle, on_aprobar, on_marcar_pagada, on_editar)
