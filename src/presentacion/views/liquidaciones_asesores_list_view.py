"""
Vista: Lista de Liquidaciones de Asesores
Muestra todas las liquidaciones de comisiones con filtros y acciones contextuales.
Refactorizado para carga asíncrona (Optimización 17.3)
Adaptado a Flet moderno (sin UserControl).
"""

import flet as ft
import time
import threading
from typing import Callable, Optional
from src.presentacion.theme import colors, styles

# Integración Fase 4: Paginación
from src.presentacion.components.pagination_manager import PaginationManager
 
class LiquidacionesAsesoresListView(ft.Container):
    def __init__(
        self,
        page: ft.Page,
        servicio_liquidacion_asesores,
        servicio_personas,
        on_nueva_liquidacion: Callable,
        on_editar_liquidacion: Callable[[int], None],
        on_ver_detalle: Callable[[int], None],
        on_aprobar: Callable[[int], None],
        on_anular: Callable[[int], None]
    ):
        super().__init__(expand=True, padding=30)
        self.page_ref = page
        self.servicio = servicio_liquidacion_asesores
        self.servicio_personas = servicio_personas
        self.on_nueva_liquidacion = on_nueva_liquidacion
        self.on_editar_liquidacion = on_editar_liquidacion
        self.on_ver_detalle = on_ver_detalle
        self.on_aprobar = on_aprobar
        self.on_anular = on_anular
        
        # Estado
        self.data_liquidaciones = []
        self.cache_asesores = {}
        self.opciones_asesores_dd = []
        
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
        
        # Refs de controles
        self.filtro_asesor = ft.Ref[ft.Dropdown]()
        self.filtro_periodo = ft.Ref[ft.TextField]()
        self.filtro_estado = ft.Ref[ft.Dropdown]()
        self.tabla_container = ft.Ref[ft.Column]()
        
        # Refs resumen
        self.res_pendiente = ft.Ref[ft.Text]()
        self.res_aprobado = ft.Ref[ft.Text]()
        self.res_pagado = ft.Ref[ft.Text]()

        # --- Construcción UI (adaptado de build) ---

        # Filtros UI
        filtros_section = ft.Container(
            content=ft.Column([
                ft.Text("Filtros", size=18, weight=ft.FontWeight.BOLD),
                ft.Divider(height=1, color="#e0e0e0"),
                ft.ResponsiveRow([
                    ft.Dropdown(
                        ref=self.filtro_asesor,
                        col={"sm": 12, "md": 6, "lg": 4},
                        label="Asesor",
                        hint_text="Cargando...",
                        options=[], # Se llenan async
                        prefix_icon=ft.Icons.PERSON,
                        text_size=14,
                        on_change=lambda e: self.cargar_datos(mantener_opciones=True)
                    ),
                    ft.TextField(
                        ref=self.filtro_periodo,
                        col={"sm": 12, "md": 6, "lg": 4},
                        label="Período",
                        hint_text="YYYY-MM",
                        prefix_icon=ft.Icons.CALENDAR_MONTH,
                        on_change=lambda e: self.cargar_datos(mantener_opciones=True)
                    ),
                    ft.Dropdown(
                        ref=self.filtro_estado,
                        col={"sm": 12, "md": 6, "lg": 4},
                        label="Estado",
                        hint_text="Todos",
                        options=[
                            ft.dropdown.Option("Todos"),
                            ft.dropdown.Option("Pendiente"),
                            ft.dropdown.Option("Aprobada"),
                            ft.dropdown.Option("Pagada"),
                            ft.dropdown.Option("Anulada"),
                        ],
                        on_change=lambda e: self.cargar_datos(mantener_opciones=True)
                    ),
                ]),
                ft.Row([
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
                ], spacing=10),
            ]),
            bgcolor="white",
            padding=20,
            border_radius=8,
            border=ft.border.all(1, "#e0e0e0"),
        )
        
        # Resumen Widgets
        resumen_section = ft.Container(
            content=ft.ResponsiveRow([
                self._crear_widget_resumen("Pendiente Aprobación", ft.Icons.PENDING_ACTIONS, "#ff9800", self.res_pendiente, "$..."),
                self._crear_widget_resumen("Aprobado (Por Pagar)", ft.Icons.CHECK_CIRCLE_OUTLINE, "#2196f3", self.res_aprobado, "$..."),
                self._crear_widget_resumen("Total Pagado", ft.Icons.PAYMENTS, "#4caf50", self.res_pagado, "$..."),
            ]),
            padding=ft.padding.only(bottom=20)
        )
        
        self.content = ft.Column([
            # Breadcrumbs
            ft.Row([
                ft.Text("Inicio", size=14, color="#666"),
                ft.Text(" > ", size=14, color="#666"),
                ft.Text("Liquidación Asesores", size=14, weight=ft.FontWeight.BOLD, color="#1976d2"),
            ]),
            ft.Divider(height=20, color="transparent"),
            
            # Header
            ft.Row([
                ft.Text("Liquidación de Asesores", size=28, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    "+ Nueva Liquidación",
                    icon=ft.Icons.ADD,
                    on_click=lambda e: self.on_nueva_liquidacion(),
                    bgcolor="#1976d2",
                    color="white",
                    height=45,
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            ft.Divider(height=20, color="transparent"),
            resumen_section,
            filtros_section,
            ft.Divider(height=20, color="transparent"),
            
            ft.Column(ref=self.tabla_container, spacing=10),
            
            # Paginación
            ft.Container(
                content=self.pagination,
                padding=ft.padding.only(top=10, bottom=20)
            )
        ], scroll=ft.ScrollMode.AUTO, spacing=0)

    def _crear_widget_resumen(self, titulo, icon, color, ref, valor_inicial):
        return ft.Container(
            col={"sm": 12, "md": 4},
            content=ft.Container(
                content=ft.Column([
                    ft.Icon(icon, size=40, color=color),
                    ft.Text(titulo, size=14, color="#666"),
                    ft.Text(ref=ref, value=valor_inicial, size=24, weight=ft.FontWeight.BOLD, color=color)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                bgcolor="white",
                padding=20,
                border_radius=8,
                border=ft.border.all(2, color)
            )
        )

    def did_mount(self):
        self.cargar_datos(mantener_opciones=False)

    def limpiar_filtros(self, e):
        self.filtro_asesor.current.value = None
        self.filtro_periodo.current.value = ""
        self.filtro_estado.current.value = None
        self.update()
        self.cargar_datos(mantener_opciones=True)

    def cargar_datos(self, mantener_opciones=False):
        # Loading State
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
            'asesor': self.filtro_asesor.current.value,
            'periodo': self.filtro_periodo.current.value,
            'estado': self.filtro_estado.current.value,
        }
        
        threading.Thread(target=self._fetch_data_thread, args=(filtros, mantener_opciones), daemon=True).start()

    def _fetch_data_thread(self, filtros, mantener_opciones):
        try:
            # 1. Cargar opciones de asesores si no se deben mantener (primera carga)
            if not mantener_opciones:
                try:
                    asesores = self.servicio_personas.listar_personas(filtro_rol="Asesor", solo_activos=False)
                    opciones = []
                    cache = {}
                    for asesor in asesores:
                        if "Asesor" in asesor.roles:
                            a_id = asesor.datos_roles["Asesor"].id_asesor
                            opciones.append(
                                ft.dropdown.Option(key=str(a_id), text=asesor.nombre_completo)
                            )
                    self.opciones_asesores_dd = opciones
                except Exception as e:
                    pass  # print(f"Error cargando asesores opciones: {e}") [OpSec Removed]
            
            # 2. Cargar cache de noms asesores para la tabla (siempre necesario para mapear ID -> Nombre)
            # Para optimizar, podríamos reusar lo de arriba, pero por seguridad cargamos todo el mapa
            try:
                todos_asesores = self.servicio_personas.listar_personas(filtro_rol="Asesor", solo_activos=False)
                cache_map = {}
                for a in todos_asesores:
                     if "Asesor" in a.roles:
                        cache_map[a.datos_roles["Asesor"].id_asesor] = a.nombre_completo
                self.cache_asesores = cache_map
            except Exception as e:
                pass  # print(f"Error cache asesores: {e}") [OpSec Removed]

            # 3. Cargar Liquidaciones con filtros (PAGINADO)
            id_asesor = int(filtros['asesor']) if filtros['asesor'] else None
            estado = filtros['estado'] if filtros['estado'] != "Todos" else None
            
            result = self.servicio.listar_liq_asesores_paginado(
                page=self.current_page,
                page_size=self.page_size,
                id_asesor=id_asesor,
                periodo=filtros['periodo'] or None,
                estado=estado
            )
            
            self.data_liquidaciones = result.items
            self.total_items = result.total
            
            # 4. Calcular Resúmenes (Ahora usando servicio de métricas para TOTALES GLOBALES filtrados)
            # Solicitamos métricas con los mismos filtros
            metricas = self.servicio.obtener_metricas_filtradas(
                id_asesor=id_asesor,
                periodo=filtros['periodo'] or None,
                estado=estado
            )
            
            resumen = {
                "pend": metricas.get('Pendiente', 0), 
                "aprob": metricas.get('Aprobada', 0), 
                "pag": metricas.get('Pagada', 0)
            }
            
            self._schedule_ui_update(resumen, update_dropdown=not mantener_opciones)
            
        except Exception as e:
            pass  # print(f"Error fetch liquidaciones: {e}") [OpSec Removed]
            import traceback
            traceback.print_exc()
            self.data_liquidaciones = []
            self.total_items = 0
            self._schedule_ui_update(None, error=str(e))

    def _schedule_ui_update(self, resumen=None, update_dropdown=False, error=None):
        if error:
            self.tabla_container.current.controls = [ft.Text(f"Error: {error}", color="red")]
            self.tabla_container.current.update()
            return
            
        # Update dropdown options if needed
        if update_dropdown:
            self.filtro_asesor.current.options = self.opciones_asesores_dd
            self.filtro_asesor.current.hint_text = "Todos"
            self.filtro_asesor.current.update()
        
        # Update Resumen Cards
        if resumen:
            self.res_pendiente.current.value = f"${resumen['pend']:,}"
            self.res_pendiente.current.update()
            self.res_aprobado.current.value = f"${resumen['aprob']:,}"
            self.res_aprobado.current.update()
            self.res_pagado.current.value = f"${resumen['pag']:,}"
            self.res_pagado.current.update()

        # Update Tabla
        if not self.data_liquidaciones:
             self.tabla_container.current.controls = [
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET, size=64, color="#ccc"),
                        ft.Text("No hay liquidaciones para mostrar", size=16, color="#666")
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=40,
                    alignment=ft.alignment.center
                )
            ]
        else:
            filas = []
            for liq in self.data_liquidaciones:
                nombre = self.cache_asesores.get(liq['id_asesor'], f"Asesor #{liq['id_asesor']}")
                color_estado = self._get_color_estado(liq['estado_liquidacion'])
                
                acciones = []
                # VerDetalle
                acciones.append(
                    ft.IconButton(
                        ft.Icons.VISIBILITY, 
                        icon_color="#1976d2", 
                        tooltip="Ver detalle",
                        on_click=lambda e, id=liq['id_liquidacion_asesor']: self.on_ver_detalle(id)
                    )
                )
                
                if liq['estado_liquidacion'] == 'Pagada':
                    # Indicador de Pagada (usando Tooltip wrapper por seguridad)
                    acciones.insert(0, 
                        ft.Tooltip(
                            message="Liquidación Pagada",
                            content=ft.Icon(ft.Icons.PAID, color="#4caf50", size=20)
                        )
                    )
                else:
                    if liq['puede_editarse']:
                         acciones.append(
                             ft.IconButton(
                                 ft.Icons.EDIT_SQUARE, 
                                 icon_color="#2196f3", 
                                 tooltip="Editar liquidación", 
                                 on_click=lambda e, id=liq['id_liquidacion_asesor']: self.on_editar_liquidacion(id)
                             )
                         )
                    
                    if liq['puede_aprobarse']:
                        acciones.append(
                            ft.IconButton(
                                ft.Icons.THUMB_UP, 
                                icon_color="#4caf50", 
                                tooltip="Aprobar para pago", 
                                on_click=lambda e, id=liq['id_liquidacion_asesor']: self.on_aprobar(id)
                            )
                        )
                            
                    if liq['puede_anularse']:
                        acciones.append(
                            ft.IconButton(
                                ft.Icons.BLOCK, 
                                icon_color="#f44336", 
                                tooltip="Anular liquidación", 
                                on_click=lambda e, id=liq['id_liquidacion_asesor']: self.on_anular(id)
                            )
                        )

                filas.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(liq['periodo_liquidacion'], size=13)),
                        ft.DataCell(ft.Text(nombre, size=12)),
                        ft.DataCell(ft.Text(f"Contrato #{liq['id_contrato_a']}", size=12)),
                        ft.DataCell(ft.Text(f"{liq['porcentaje_real']:.2f}%", size=12)),
                        ft.DataCell(ft.Text(f"${liq['comision_bruta']:,}", size=12)),
                        ft.DataCell(ft.Text(f"${liq['total_descuentos']:,}", size=12, color="#f44336" if liq['total_descuentos']>0 else "#666")),
                        ft.DataCell(ft.Text(f"${liq['valor_neto_asesor']:,}", size=13, weight=ft.FontWeight.BOLD)),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(liq['estado_liquidacion'], color="white", size=11, weight=ft.FontWeight.BOLD),
                                bgcolor=color_estado,
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                border_radius=4
                            )
                        ),
                        ft.DataCell(ft.Row(acciones, spacing=0)),
                    ])
                )
            
            tabla = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Período", weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Asesor", weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Contrato", weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("% Cal", weight=ft.FontWeight.BOLD)), # Header corto para espacio
                    ft.DataColumn(ft.Text("Bruto", weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Desc", weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("Neto", weight=ft.FontWeight.BOLD)),
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
                    content=ft.Column([tabla], scroll=ft.ScrollMode.AUTO),
                    border_radius=8,
                    bgcolor="white",
                    padding=10,
                )
            ]
            
        self.tabla_container.current.update()
        
        # Paginador Sync
        self.pagination.set_total_items(self.total_items)
        self.pagination.set_current_page(self.current_page)
        self.pagination.update()

    def _on_page_change(self, page: int):
        self.current_page = page
        self.cargar_datos(mantener_opciones=True)

    def _on_page_size_change(self, page_size: int):
        self.page_size = page_size
        self.current_page = 1
        self.cargar_datos(mantener_opciones=True)
        
    def _reset_pagination(self):
        self.current_page = 1
        self.cargar_datos(mantener_opciones=True)

    def _get_color_estado(self, estado):
        return {
            'Pendiente': '#ff9800',
            'Aprobada': '#2196f3',
            'Pagada': '#4caf50',
            'Anulada': '#9e9e9e'
        }.get(estado, '#666')

def crear_liquidaciones_asesores_list_view(page, servicio_liquidacion_asesores, servicio_personas, on_nueva_liquidacion, on_editar_liquidacion, on_ver_detalle, on_aprobar, on_anular):
    return LiquidacionesAsesoresListView(page, servicio_liquidacion_asesores, servicio_personas, on_nueva_liquidacion, on_editar_liquidacion, on_ver_detalle, on_aprobar, on_anular)
