"""
Vista: Gestión de Pagos de Asesores
Lista pagos pendientes/programados con acciones para registrar, rechazar y anular.
Refactorizado a UserControl asíncrono.
Adaptado a Flet moderno (sin UserControl).
"""

import flet as ft
import threading
from typing import Callable, Optional

class PagosAsesoresListView(ft.Container):
    def __init__(
        self,
        page: ft.Page,
        servicio_liquidacion_asesores,
        servicio_personas,
        on_registrar_pago: Callable[[int], None],
        on_rechazar_pago: Callable[[int], None],
        on_anular_pago: Callable[[int], None],
        on_ver_liquidacion: Callable[[int], None]
    ):
        super().__init__(expand=True, padding=30)
        self.page_ref = page
        self.servicio = servicio_liquidacion_asesores
        self.servicio_personas = servicio_personas
        self.on_registrar_pago = on_registrar_pago
        self.on_rechazar_pago = on_rechazar_pago
        self.on_anular_pago = on_anular_pago
        self.on_ver_liquidacion = on_ver_liquidacion
        
        # State
        self.pagos = []
        self.asesores_cache = {}
        self.opciones_asesores = []
        
        # Controls
        self.filtro_asesor = ft.Ref[ft.Dropdown]()
        self.filtro_estado = ft.Ref[ft.Dropdown]()
        self.tabla_container = ft.Ref[ft.Column]()
        self.resumen_pendiente = ft.Ref[ft.Text]()
        self.resumen_programado = ft.Ref[ft.Text]()
        self.resumen_pagado = ft.Ref[ft.Text]()
        self.loading = ft.ProgressBar(width=400, color="blue", visible=False)

        # --- Construcción UI (adaptado de build) ---

        # Filtros
        filtros_section = ft.Container(
            content=ft.Column([
                ft.Text("Filtros", size=18, weight=ft.FontWeight.BOLD),
                ft.Divider(height=1, color="#e0e0e0"),
                ft.ResponsiveRow([
                    ft.Dropdown(
                        ref=self.filtro_asesor,
                        col={"sm": 12, "md": 6},
                        label="Asesor",
                        hint_text="Cargando...",
                        options=[], # Async
                        prefix_icon=ft.Icons.PERSON,
                        on_change=lambda e: self.cargar_datos(mantener_opciones=True)
                    ),
                    ft.Dropdown(
                        ref=self.filtro_estado,
                        col={"sm": 12, "md": 6},
                        label="Estado",
                        hint_text="Todos",
                        options=[
                            ft.dropdown.Option("Todos"), ft.dropdown.Option("Pendiente"),
                            ft.dropdown.Option("Programado"), ft.dropdown.Option("Pagado"),
                        ],
                        on_change=lambda e: self.cargar_datos(mantener_opciones=True)
                    ),
                ]),
                ft.Row([
                    ft.ElevatedButton("Aplicar", icon=ft.Icons.FILTER_ALT, on_click=lambda e: self.cargar_datos(mantener_opciones=True), bgcolor="#4caf50", color="white"),
                    ft.OutlinedButton("Limpiar", icon=ft.Icons.CLEAR, on_click=self.limpiar_filtros),
                ], spacing=10),
            ]),
            bgcolor="white", padding=20, border_radius=8, border=ft.border.all(1, "#e0e0e0"),
        )
        
        # Resumen Widgets
        resumen_section = ft.Container(
            content=ft.ResponsiveRow([
                self._crear_card_resumen("Por Pagar", ft.Icons.PENDING_ACTIONS, "#ff9800", self.resumen_pendiente),
                self._crear_card_resumen("Liquidaciones Aprobadas", ft.Icons.SCHEDULE, "#2196f3", self.resumen_programado, is_count=True),
                self._crear_card_resumen("Total Pagado", ft.Icons.CHECK_CIRCLE, "#4caf50", self.resumen_pagado),
            ]),
            padding=ft.padding.only(bottom=20)
        )

        self.content = ft.Column([
            ft.Row([ ft.Text("Inicio", size=14, color="#666"), ft.Text(" > ", size=14, color="#666"), ft.Text("Pagos Asesores", size=14, weight="bold", color="#1976d2")]),
            ft.Divider(height=20, color="transparent"),
            ft.Text("Gestión de Pagos", size=28, weight="bold"),
            ft.Divider(height=20, color="transparent"),
            resumen_section,
            filtros_section,
            ft.Divider(height=20, color="transparent"),
            ft.Container(content=self.loading, alignment=ft.alignment.center),
            ft.Column(ref=self.tabla_container, spacing=10)
        ], scroll=ft.ScrollMode.AUTO, spacing=0)

    def _crear_card_resumen(self, titulo, icon, color, ref, is_count=False):
        val = "0" if is_count else "$0"
        return ft.Container(
            col={"sm": 12, "md": 4},
            content=ft.Container(
                content=ft.Column([
                    ft.Icon(icon, size=40, color=color),
                    ft.Text(titulo, size=14, color="#666"),
                    ft.Text(ref=ref, value=val, size=24, weight="bold", color=color)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                bgcolor="white", padding=20, border_radius=8, border=ft.border.all(2, color)
            )
        )

    def did_mount(self):
        self.cargar_datos(mantener_opciones=False)

    def limpiar_filtros(self, e):
        self.filtro_asesor.current.value = None
        self.filtro_estado.current.value = None
        self.update()
        self.cargar_datos(mantener_opciones=True)

    def cargar_datos(self, mantener_opciones=False):
        self.loading.visible = True
        self.tabla_container.current.visible = False
        self.update()
        
        filtros = {
            'asesor': self.filtro_asesor.current.value,
            'estado': self.filtro_estado.current.value
        }
        
        threading.Thread(target=self._fetch_data, args=(filtros, mantener_opciones), daemon=True).start()

    def _fetch_data(self, filtros, mantener_opciones):
        try:
            # 1. Cargar opciones asesores (primera vez)
            if not mantener_opciones:
                try:
                    asesores = self.servicio_personas.listar_personas(filtro_rol="Asesor")
                    opciones = []
                    cache = {}
                    for a in asesores:
                        opciones.append(ft.dropdown.Option(key=str(a.persona.id_persona), text=a.nombre_completo))
                        cache[a.persona.id_persona] = a.nombre_completo
                    self.opciones_asesores = opciones
                    self.asesores_cache = cache
                except Exception as e: print(f"Error asesores: {e}")

            # 2. Listar Pagos
            id_asesor = int(filtros['asesor']) if filtros['asesor'] else None
            estado = filtros['estado'] if filtros['estado'] != "Todos" else None
            
            # Usamos listar_liquidaciones como proxy de pagos por ahora
            liquidaciones = self.servicio.listar_liquidaciones(
                id_asesor=id_asesor,
                estado='Aprobada' # Traemos aprobadas que son las que generan pagos
            )
            
            # Filter in memory if needed or if service doesn't support all combos
            # The original code filtered 'Aprobada' hardcoded but then iterated.
            # We follow original logic but allow filtering.
            
            if estado and estado != 'Todos':
                # Map estado pago to estado liquidacion roughly
                if estado == 'Pendiente': liquidaciones = [l for l in liquidaciones if l['estado_liquidacion'] == 'Aprobada']
                elif estado == 'Pagado': liquidaciones = [l for l in liquidaciones if l['estado_liquidacion'] == 'Pagada']
                # Programado logic? Original code says Programado in summary but mapped to len(liquidaciones)
            
            self.pagos = liquidaciones
            
            # 3. Resumes
            total_pend = sum(l['valor_neto_asesor'] for l in liquidaciones if l['estado_liquidacion'] == 'Aprobada')
            total_pagd = sum(l['valor_neto_asesor'] for l in liquidaciones if l['estado_liquidacion'] == 'Pagada')
            prog_count = len(liquidaciones) # As per original logic
            
            self._schedule_ui_update(
                resumen={'pend': total_pend, 'pagd': total_pagd, 'prog': prog_count},
                update_opciones=not mantener_opciones
            )

        except Exception as e:
            pass  # print(f"Error pagos: {e}") [OpSec Removed]
            self._schedule_ui_update(error=str(e))

    def _schedule_ui_update(self, resumen=None, update_opciones=False, error=None):
        if error:
            self.loading.visible = False
            self.tabla_container.current.controls = [ft.Text(f"Error: {error}", color="red")]
            self.tabla_container.current.update()
            return
            
        if update_opciones:
            self.filtro_asesor.current.options = self.opciones_asesores
            self.filtro_asesor.current.update()
            
        if resumen:
            self.resumen_pendiente.current.value = f"${resumen['pend']:,}"
            self.resumen_pagado.current.value = f"${resumen['pagd']:,}"
            self.resumen_programado.current.value = str(resumen['prog'])
            self.resumen_pendiente.current.update()
            self.resumen_pagado.current.update()
            self.resumen_programado.current.update()

        # Update Table
        self.tabla_container.current.controls = [self._crear_tabla()]
        self.loading.visible = False
        self.loading.update()  # FIX: Actually hide the loading bar
        self.tabla_container.current.visible = True
        self.tabla_container.current.update()

    def _crear_tabla(self):
        if not self.pagos:
            return ft.Container(content=ft.Text("No hay pagos pendientes", size=16), padding=50, alignment=ft.alignment.center)
            
        filas = []
        for liq in self.pagos:
            nombre = self.asesores_cache.get(liq['id_asesor'], f"Asesor #{liq['id_asesor']}")
            color = {'Pendiente':'#ff9800', 'Pagado':'#4caf50', 'Aprobada':'#2196f3'}.get(liq['estado_liquidacion'], 'grey')
            
            acciones = []
            if liq['estado_liquidacion'] == 'Aprobada':
                acciones.append(ft.ElevatedButton("Pagar", icon=ft.Icons.PAYMENT, bgcolor="#4caf50", color="white", height=35,
                    on_click=lambda e, id=liq['id_liquidacion_asesor']: self.on_registrar_pago(id)))
                acciones.append(ft.IconButton(ft.Icons.CANCEL, icon_color="#f44336", tooltip="Rechazar",
                    on_click=lambda e, id=liq['id_liquidacion_asesor']: self.on_rechazar_pago(id)))
            
            acciones.append(ft.IconButton(ft.Icons.VISIBILITY, icon_color="#1976d2", tooltip="Ver",
                on_click=lambda e, id=liq['id_liquidacion_asesor']: self.on_ver_liquidacion(id)))
                
            filas.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(liq['periodo_liquidacion'])),
                ft.DataCell(ft.Text(nombre)),
                ft.DataCell(ft.Text(f"#{liq['id_contrato_a']}")),
                ft.DataCell(ft.Text(f"${liq['valor_neto_asesor']:,}", weight="bold", color="#4caf50")),
                ft.DataCell(ft.Container(content=ft.Text(liq['estado_liquidacion'], color="white", size=11), bgcolor=color, padding=5, border_radius=4)),
                ft.DataCell(ft.Row(acciones, spacing=5))
            ]))

        return ft.Container(
            content=ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Período")), ft.DataColumn(ft.Text("Asesor")),
                    ft.DataColumn(ft.Text("Contrato")), ft.DataColumn(ft.Text("Valor a Pagar")),
                    ft.DataColumn(ft.Text("Estado")), ft.DataColumn(ft.Text("Acciones")),
                ],
                rows=filas, border=ft.border.all(1, "#e0e0e0"), border_radius=8
            ),
            bgcolor="white", padding=10, border_radius=8
        )

def crear_pagos_asesores_list_view(page, servicio_liquidacion_asesores, servicio_personas, on_registrar_pago, on_rechazar_pago, on_anular_pago, on_ver_liquidacion):
    return PagosAsesoresListView(page, servicio_liquidacion_asesores, servicio_personas, on_registrar_pago, on_rechazar_pago, on_anular_pago, on_ver_liquidacion)
