from typing import Callable
import flet as ft
from src.aplicacion.servicios.servicio_incidentes import ServicioIncidentes
from src.aplicacion.servicios.servicio_proveedores import ServicioProveedores
from src.presentacion.components.document_manager import DocumentManager

class IncidenteDetailView(ft.Column):
    def __init__(self, page: ft.Page, servicio_incidentes: ServicioIncidentes, servicio_proveedores: ServicioProveedores, id_incidente: int, on_navigate: Callable, on_refrescar_incidentes: Callable = None):
        super().__init__(scroll=ft.ScrollMode.AUTO, expand=True)
        self.page = page
        self.servicio = servicio_incidentes
        self.servicio_proveedores = servicio_proveedores
        self.id_incidente = id_incidente
        self.on_navigate = on_navigate
        self.on_refrescar_incidentes = on_refrescar_incidentes
        self.detalle = None

        self._construir_vista()
        
    def _construir_vista(self):
        """Construye o reconstruye la vista completa."""
        self.cargar_datos()
        
        if not self.detalle:
             self.controls = [ft.Text("Incidente no encontrado o error de carga.")]
             return
             
        inc = self.detalle['incidente']
        propiedad = self.detalle.get('propiedad')
        
        # Header con estado
        header = self._crear_header(inc)
        
        # Info principal
        info_panel = self._crear_info_panel(inc, propiedad)
        
        # Panel de cotizaciones
        cotizaciones_panel = self._crear_cotizaciones_panel(inc)
        
        # Panel de historial
        historial_panel = self._crear_historial_panel()
        
        # Panel de documentos
        documentos_panel = self._crear_documentos_panel(inc)
        
        # Acciones contextuales
        acciones = self._crear_acciones(inc)
        
        self.controls = [
            header,
            ft.Divider(),
            info_panel,
            ft.Divider(),
            cotizaciones_panel,
            ft.Divider(),
            historial_panel,
            ft.Divider(),
            documentos_panel,
            ft.Divider(),
            ft.Row(acciones, wrap=True, spacing=10)
        ]

    def _crear_header(self, inc):
        """Crea el header con título y badge de estado."""
        return ft.Row(
            controls=[
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    tooltip="Volver a Incidentes",
                    on_click=lambda _: self.on_navigate("incidentes")
                ),
                ft.Text(f"Incidente #{inc.id_incidente}", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=ft.Text(inc.estado, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                    bgcolor=self._get_color_estado(inc.estado),
                    padding=ft.padding.symmetric(horizontal=15, vertical=8),
                    border_radius=20
                ),
                ft.Container(
                    content=ft.Text(inc.prioridad, color=ft.Colors.WHITE, size=12),
                    bgcolor=self._get_color_prioridad(inc.prioridad),
                    padding=ft.padding.symmetric(horizontal=10, vertical=5),
                    border_radius=10
                )
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=15
        )
    
    def _crear_info_panel(self, inc, propiedad):
        """Crea el panel de información del incidente."""
        direccion_display = propiedad.direccion_propiedad if propiedad else f"Propiedad ID: {inc.id_propiedad}"
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.HOME, color=ft.Colors.BLUE_400),
                    ft.Text(direccion_display, size=16, weight=ft.FontWeight.W_500),
                ], spacing=10),
                ft.Row([
                    ft.Column([
                        ft.Text("Origen", size=12, color=ft.Colors.GREY_600),
                        ft.Text(inc.origen_reporte, weight=ft.FontWeight.BOLD),
                    ], spacing=2),
                    ft.Column([
                        ft.Text("Fecha Reporte", size=12, color=ft.Colors.GREY_600),
                        ft.Text(str(inc.fecha_incidente)[:10] if inc.fecha_incidente else "N/A", weight=ft.FontWeight.BOLD),
                    ], spacing=2),
                    ft.Column([
                        ft.Text("Días sin Resolver", size=12, color=ft.Colors.GREY_600),
                        ft.Text(str(inc.dias_sin_resolver), weight=ft.FontWeight.BOLD, 
                               color=ft.Colors.RED_600 if inc.dias_sin_resolver > 7 else ft.Colors.GREEN_600),
                    ], spacing=2),
                    ft.Column([
                        ft.Text("Responsable Pago", size=12, color=ft.Colors.GREY_600),
                        ft.Text(inc.responsable_pago or "Sin asignar", weight=ft.FontWeight.BOLD),
                    ], spacing=2) if inc.responsable_pago else ft.Container(),
                ], spacing=30),
                ft.Divider(height=10),
                ft.Text("Descripción:", weight=ft.FontWeight.BOLD, size=14),
                ft.Container(
                    content=ft.Text(inc.descripcion_incidente, size=14),
                    bgcolor=ft.Colors.GREY_100,
                    padding=15,
                    border_radius=10
                ),
            ], spacing=15),
            padding=20,
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=10
        )
    
    def _crear_cotizaciones_panel(self, inc):
        """Crea el panel de cotizaciones con botones de aprobar/rechazar."""
        cotizaciones_controls = []
        
        # Cotizaciones pendientes (con botones de acción)
        cotizaciones_pendientes = [c for c in self.detalle['cotizaciones'] if c.estado_cotizacion == "Pendiente"]
        cotizaciones_rechazadas = [c for c in self.detalle['cotizaciones'] if c.estado_cotizacion == "Rechazada"]
        cotizacion_aprobada = next((c for c in self.detalle['cotizaciones'] if c.estado_cotizacion == "Aprobada"), None)
        
        # Mostrar cotización aprobada si existe
        if cotizacion_aprobada:
            cotizaciones_controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Container(
                                content=ft.Text("✅ APROBADA", size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                                bgcolor=ft.Colors.GREEN_600,
                                padding=ft.padding.symmetric(horizontal=12, vertical=6),
                                border_radius=15
                            ),
                        ]),
                        ft.Divider(height=10),
                        ft.Text(f"Proveedor ID: {cotizacion_aprobada.id_proveedor}", weight=ft.FontWeight.BOLD, size=16),
                        ft.Row([
                            ft.Column([
                                ft.Text("💵 Materiales", size=12, color=ft.Colors.GREY_700),
                                ft.Text(f"${cotizacion_aprobada.valor_materiales:,.0f}", size=14, weight=ft.FontWeight.BOLD),
                            ], spacing=2),
                            ft.Column([
                                ft.Text("👷 Mano de Obra", size=12, color=ft.Colors.GREY_700),
                                ft.Text(f"${cotizacion_aprobada.valor_mano_obra:,.0f}", size=14, weight=ft.FontWeight.BOLD),
                            ], spacing=2),
                            ft.Column([
                                ft.Text("📅 Días Estimados", size=12, color=ft.Colors.GREY_700),
                                ft.Text(f"{cotizacion_aprobada.dias_estimados}", size=14, weight=ft.FontWeight.BOLD),
                            ], spacing=2),
                        ], spacing=20),
                        ft.Divider(height=10),
                        ft.Row([
                            ft.Text("Total:", size=16, color=ft.Colors.GREY_700),
                            ft.Text(f"${cotizacion_aprobada.valor_total:,.0f}", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_700),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Text(cotizacion_aprobada.descripcion_trabajo or "Sin descripción", size=12, italic=True),
                    ], spacing=10),
                    padding=15,
                    border=ft.border.all(2, ft.Colors.GREEN_300),
                    border_radius=10,
                    bgcolor=ft.Colors.GREEN_50
                )
            )
        
        # Mostrar cotizaciones pendientes (solo si el estado lo permite)
        if cotizaciones_pendientes and inc.estado in ["Reportado", "En Revision", "Cotizado"]:
            cotizaciones_controls.append(
                ft.Text("Cotizaciones Pendientes", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_700)
            )
            for cot in cotizaciones_pendientes:
                cotizaciones_controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Container(
                                content=ft.Text("⏳ Pendiente", size=11, color=ft.Colors.WHITE),
                                bgcolor=ft.Colors.ORANGE_600,
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                border_radius=10
                            ),
                            ft.Column([
                                ft.Text(f"Proveedor ID: {cot.id_proveedor}", weight=ft.FontWeight.BOLD),
                                ft.Text(f"Total: ${cot.valor_total:,.0f} | {cot.dias_estimados} días", size=12),
                                ft.Text(cot.descripcion_trabajo or "Sin descripción", size=11, color=ft.Colors.GREY_600),
                            ], spacing=2, expand=True),
                            ft.Row([
                                ft.ElevatedButton(
                                    "Aprobar",
                                    icon=ft.Icons.CHECK_CIRCLE,
                                    bgcolor=ft.Colors.GREEN_600,
                                    color=ft.Colors.WHITE,
                                    on_click=lambda _, id_c=cot.id_cotizacion: self.aprobar_cot(id_c)
                                ),
                                ft.ElevatedButton(
                                    "Rechazar",
                                    icon=ft.Icons.CANCEL,
                                    bgcolor=ft.Colors.RED_600,
                                    color=ft.Colors.WHITE,
                                    on_click=lambda _, id_c=cot.id_cotizacion: self.abrir_modal_rechazo(id_c)
                                ),
                            ], spacing=5)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        padding=12,
                        border=ft.border.all(1, ft.Colors.ORANGE_300),
                        border_radius=8,
                        margin=ft.margin.only(bottom=8)
                    )
                )
        
        # Mostrar cotizaciones rechazadas (colapsable)
        if cotizaciones_rechazadas:
            rechazadas_items = []
            for cot in cotizaciones_rechazadas:
                rechazadas_items.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Text("❌", size=14),
                            ft.Column([
                                ft.Text(f"Proveedor ID: {cot.id_proveedor}", size=12, color=ft.Colors.GREY_600),
                                ft.Text(f"${cot.valor_total:,.0f}", size=11, color=ft.Colors.GREY_500),
                            ], spacing=1, expand=True),
                        ], spacing=10),
                        padding=8,
                        bgcolor=ft.Colors.GREY_100,
                        border_radius=5,
                        margin=ft.margin.only(bottom=5)
                    )
                )
            
            cotizaciones_controls.append(
                ft.ExpansionTile(
                    title=ft.Text(f"Cotizaciones Rechazadas ({len(cotizaciones_rechazadas)})", 
                                 size=13, color=ft.Colors.GREY_600),
                    controls=rechazadas_items,
                    initially_expanded=False,
                    tile_padding=ft.padding.symmetric(horizontal=10, vertical=5),
                )
            )
        
        # Si no hay cotizaciones
        if not self.detalle['cotizaciones']:
            cotizaciones_controls.append(
                ft.Container(
                    content=ft.Text("No hay cotizaciones registradas.", italic=True, color=ft.Colors.GREY_600),
                    padding=20,
                    alignment=ft.alignment.center
                )
            )
        
        # Botón agregar cotización
        boton_agregar = ft.Container()
        if inc.estado in ["Reportado", "En Revision", "Cotizado"]:
            boton_agregar = ft.ElevatedButton(
                "➕ Agregar Cotización", 
                on_click=self.abrir_modal_cotizacion,
                bgcolor=ft.Colors.BLUE_600,
                color=ft.Colors.WHITE
            )
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Cotizaciones", size=18, weight=ft.FontWeight.BOLD),
                    boton_agregar,
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Column(cotizaciones_controls, scroll=ft.ScrollMode.AUTO, height=300 if len(self.detalle['cotizaciones']) > 2 else None),
            ], spacing=10),
            padding=10
        )
    
    def _crear_historial_panel(self):
        """Crea el panel de historial de cambios."""
        historial = self.servicio.obtener_historial(self.id_incidente)
        
        if not historial:
            return ft.Container(
                content=ft.Column([
                    ft.Text("Historial de Cambios", size=16, weight=ft.FontWeight.BOLD),
                    ft.Text("No hay historial registrado.", italic=True, color=ft.Colors.GREY_600),
                ]),
                padding=10
            )
        
        historial_items = []
        for h in historial:
            icono, color = self._get_icono_tipo_accion(h.tipo_accion)
            historial_items.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(icono, color=color, size=20),
                        ft.Column([
                            ft.Row([
                                ft.Text(h.tipo_accion.replace("_", " ").title(), weight=ft.FontWeight.BOLD, size=12),
                                ft.Text(f"por {h.usuario}", size=11, color=ft.Colors.GREY_600),
                            ], spacing=10),
                            ft.Text(
                                f"{h.estado_anterior or 'N/A'} → {h.estado_nuevo}" if h.estado_nuevo else (h.comentario or "Sin comentario"),
                                size=11, color=ft.Colors.GREY_700
                            ),
                            ft.Text(str(h.fecha_cambio)[:19], size=10, color=ft.Colors.GREY_500),
                        ], spacing=2, expand=True),
                    ], spacing=15),
                    padding=10,
                    border=ft.border.only(left=ft.BorderSide(3, color)),
                    margin=ft.margin.only(bottom=5)
                )
            )
        
        return ft.ExpansionTile(
            title=ft.Text(f"Historial de Cambios ({len(historial)})", size=16, weight=ft.FontWeight.BOLD),
            controls=historial_items,
            initially_expanded=False,
        )
        
    def _crear_documentos_panel(self, inc):
        """Crea el panel de gestión documental."""
        return ft.ExpansionTile(
            title=ft.Text("Documentos y Evidencias", size=16, weight=ft.FontWeight.BOLD),
            controls=[
                ft.Container(
                    content=DocumentManager(
                        entidad_tipo="INCIDENTE",
                        entidad_id=str(inc.id_incidente),
                        page=self.page
                    ),
                    padding=10
                )
            ],
            initially_expanded=False
        )
    
    def _crear_acciones(self, inc):
        """Crea los botones de acción según el estado del incidente."""
        acciones = []
        
        if inc.estado == "Aprobado":
            acciones.append(ft.ElevatedButton(
                "🔧 Iniciar Reparación", 
                icon=ft.Icons.BUILD, 
                on_click=self.iniciar_reparacion,
                bgcolor=ft.Colors.BLUE_600,
                color=ft.Colors.WHITE
            ))
        
        elif inc.estado == "En Reparacion":
            acciones.append(ft.ElevatedButton(
                "✅ Finalizar Incidente", 
                icon=ft.Icons.CHECK_CIRCLE, 
                on_click=self.abrir_modal_finalizacion,
                bgcolor=ft.Colors.GREEN_600,
                color=ft.Colors.WHITE
            ))
        
        # Botón cancelar disponible para estados no finales
        if inc.estado not in ["Finalizado", "Cancelado"]:
            acciones.append(ft.ElevatedButton(
                "❌ Cancelar Incidente", 
                icon=ft.Icons.CANCEL,
                on_click=self.abrir_modal_cancelacion,
                bgcolor=ft.Colors.RED_400,
                color=ft.Colors.WHITE
            ))
        
        return acciones

    def _get_color_estado(self, estado):
        """Retorna el color según el estado."""
        colores = {
            "Reportado": ft.Colors.BLUE_600,
            "En Revision": ft.Colors.ORANGE_600,
            "Cotizado": ft.Colors.PURPLE_600,
            "Aprobado": ft.Colors.TEAL_600,
            "En Reparacion": ft.Colors.AMBER_700,
            "Finalizado": ft.Colors.GREEN_600,
            "Cancelado": ft.Colors.GREY_600,
        }
        return colores.get(estado, ft.Colors.BLUE_600)
    
    def _get_color_prioridad(self, prioridad):
        """Retorna el color según la prioridad."""
        colores = {
            "Baja": ft.Colors.GREEN_400,
            "Media": ft.Colors.AMBER_600,
            "Alta": ft.Colors.ORANGE_600,
            "Urgente": ft.Colors.RED_600,
        }
        return colores.get(prioridad, ft.Colors.GREY_600)
    
    def _get_icono_tipo_accion(self, tipo_accion):
        """Retorna icono y color según el tipo de acción."""
        iconos = {
            "CREACION": (ft.Icons.ADD_CIRCLE, ft.Colors.BLUE_600),
            "CAMBIO_ESTADO": (ft.Icons.SWAP_HORIZ, ft.Colors.PURPLE_600),
            "COTIZACION_AGREGADA": (ft.Icons.REQUEST_QUOTE, ft.Colors.ORANGE_600),
            "COTIZACION_APROBADA": (ft.Icons.CHECK_CIRCLE, ft.Colors.GREEN_600),
            "COTIZACION_RECHAZADA": (ft.Icons.CANCEL, ft.Colors.RED_400),
            "ASIGNACION_PROVEEDOR": (ft.Icons.PERSON_ADD, ft.Colors.TEAL_600),
            "MODIFICACION_COSTO": (ft.Icons.ATTACH_MONEY, ft.Colors.AMBER_600),
            "CANCELACION": (ft.Icons.BLOCK, ft.Colors.RED_600),
        }
        return iconos.get(tipo_accion, (ft.Icons.INFO, ft.Colors.GREY_600))

    def cargar_datos(self):
        self.detalle = self.servicio.obtener_detalle(self.id_incidente)
    
    def refrescar_vista(self):
        """Refresca la vista reconstruyendo todos los controles."""
        self.controls.clear()
        self._construir_vista()
        self.update()
        
    def aprobar_cot(self, id_cotizacion):
        try:
            self.servicio.aprobar_cotizacion(self.id_incidente, id_cotizacion, "Sistema", "Inquilino")
            self.page.snack_bar = ft.SnackBar(ft.Text("✅ Cotización aprobada exitosamente."), bgcolor=ft.Colors.GREEN_600)
            self.page.snack_bar.open = True
            self.page.update()
            # Invalidar caché del tablero kanban
            if self.on_refrescar_incidentes:
                self.on_refrescar_incidentes()
            self.on_navigate("incidente_detalle", id_incidente=self.id_incidente)
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error: {str(ex)}"), bgcolor=ft.Colors.RED_600)
            self.page.snack_bar.open = True
            self.page.update()
    
    def abrir_modal_rechazo(self, id_cotizacion):
        """Abre modal para rechazar una cotización con motivo."""
        txt_motivo = ft.TextField(
            label="Motivo del rechazo",
            multiline=True,
            min_lines=2,
            max_lines=4,
            hint_text="Ingrese el motivo por el cual rechaza esta cotización..."
        )
        
        # Contenedor para referencia del modal (permite que las closures lo capturen)
        modal_container = [None]
        
        def cerrar_modal(e):
            if modal_container[0]:
                self.page.close(modal_container[0])
        
        def confirmar_rechazo(e):
            print("DEBUG: confirmar_rechazo INICIADO")
            print(f"DEBUG: id_incidente={self.id_incidente}, id_cotizacion={id_cotizacion}")
            print(f"DEBUG: motivo='{txt_motivo.value}'")
            try:
                print("DEBUG: Llamando servicio.rechazar_cotizacion...")
                self.servicio.rechazar_cotizacion(
                    self.id_incidente, 
                    id_cotizacion, 
                    "Sistema", 
                    txt_motivo.value
                )
                print("DEBUG: rechazar_cotizacion completado exitosamente")
                print("DEBUG: Cerrando modal...")
                if modal_container[0]:
                    self.page.close(modal_container[0])
                print("DEBUG: Modal cerrado")
                self.page.snack_bar = ft.SnackBar(ft.Text("❌ Cotización rechazada."), bgcolor=ft.Colors.ORANGE_600)
                self.page.snack_bar.open = True
                # Invalidar caché del tablero kanban
                if self.on_refrescar_incidentes:
                    self.on_refrescar_incidentes()
                print("DEBUG: Navegando a incidente_detalle...")
                self.on_navigate("incidente_detalle", id_incidente=self.id_incidente)
                print("DEBUG: confirmar_rechazo COMPLETADO")
            except Exception as ex:
                print(f"DEBUG: EXCEPCIÓN en confirmar_rechazo: {type(ex).__name__}: {ex}")
                import traceback
                traceback.print_exc()
                self.page.snack_bar = ft.SnackBar(ft.Text(f"Error: {str(ex)}"), bgcolor=ft.Colors.RED_600)
                self.page.snack_bar.open = True
                self.page.update()
        
        modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("Rechazar Cotización"),
            content=ft.Column([
                ft.Text("¿Está seguro de rechazar esta cotización?"),
                txt_motivo,
            ], tight=True, width=400),
            actions=[
                ft.TextButton("Cancelar", on_click=cerrar_modal),
                ft.ElevatedButton("Rechazar", on_click=confirmar_rechazo, bgcolor=ft.Colors.RED_600, color=ft.Colors.WHITE),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        modal_container[0] = modal  # Asignar referencia al contenedor
        self.page.open(modal)
    
    def iniciar_reparacion(self, e):
        """Inicia la reparación del incidente."""
        try:
            self.servicio.iniciar_reparacion(self.id_incidente, "Sistema")
            self.page.snack_bar = ft.SnackBar(ft.Text("🔧 Reparación iniciada."), bgcolor=ft.Colors.BLUE_600)
            self.page.snack_bar.open = True
            # Invalidar caché del tablero kanban
            if self.on_refrescar_incidentes:
                self.on_refrescar_incidentes()
            self.on_navigate("incidente_detalle", id_incidente=self.id_incidente)
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error: {str(ex)}"), bgcolor=ft.Colors.RED_600)
            self.page.snack_bar.open = True
            self.page.update()
    
    def abrir_modal_finalizacion(self, e):
        """Abre modal para finalizar incidente con costo final opcional."""
        inc = self.detalle['incidente']
        
        txt_costo_final = ft.TextField(
            label="Costo Final Real",
            value=str(inc.costo_incidente),
            keyboard_type=ft.KeyboardType.NUMBER,
            hint_text="Ingrese el costo real si difiere del presupuesto"
        )
        txt_comentario = ft.TextField(
            label="Comentario de cierre",
            multiline=True,
            min_lines=2,
            hint_text="Observaciones finales..."
        )
        
        # Contenedor para referencia del modal
        modal_container = [None]
        
        def cerrar_modal(e):
            if modal_container[0]:
                self.page.close(modal_container[0])
        
        def confirmar_finalizacion(e):
            try:
                costo_final = int(txt_costo_final.value) if txt_costo_final.value else None
                self.servicio.finalizar_incidente(
                    self.id_incidente,
                    "Sistema",
                    costo_final=costo_final,
                    comentario=txt_comentario.value
                )
                if modal_container[0]:
                    self.page.close(modal_container[0])
                self.page.snack_bar = ft.SnackBar(ft.Text("✅ Incidente finalizado exitosamente."), bgcolor=ft.Colors.GREEN_600)
                self.page.snack_bar.open = True
                # Invalidar caché del tablero kanban
                if self.on_refrescar_incidentes:
                    self.on_refrescar_incidentes()
                self.on_navigate("incidentes")
            except Exception as ex:
                self.page.snack_bar = ft.SnackBar(ft.Text(f"Error: {str(ex)}"), bgcolor=ft.Colors.RED_600)
                self.page.snack_bar.open = True
                self.page.update()
        
        modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("Finalizar Incidente"),
            content=ft.Column([
                ft.Text(f"Costo presupuestado: ${inc.costo_incidente:,.0f}"),
                txt_costo_final,
                txt_comentario,
            ], tight=True, width=400, spacing=15),
            actions=[
                ft.TextButton("Cancelar", on_click=cerrar_modal),
                ft.ElevatedButton("Finalizar", on_click=confirmar_finalizacion, bgcolor=ft.Colors.GREEN_600, color=ft.Colors.WHITE),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        modal_container[0] = modal
        self.page.open(modal)
    
    def abrir_modal_cancelacion(self, e):
        """Abre modal para cancelar incidente con motivo obligatorio."""
        txt_motivo = ft.TextField(
            label="Motivo de cancelación *",
            multiline=True,
            min_lines=2,
            max_lines=4,
            hint_text="Este campo es obligatorio..."
        )
        
        # Contenedor para referencia del modal
        modal_container = [None]
        
        def cerrar_modal(e):
            if modal_container[0]:
                self.page.close(modal_container[0])
        
        def confirmar_cancelacion(e):
            if not txt_motivo.value or not txt_motivo.value.strip():
                self.page.snack_bar = ft.SnackBar(ft.Text("El motivo es obligatorio"), bgcolor=ft.Colors.ORANGE_600)
                self.page.snack_bar.open = True
                self.page.update()
                return
            
            try:
                self.servicio.cancelar_incidente(self.id_incidente, "Sistema", txt_motivo.value)
                if modal_container[0]:
                    self.page.close(modal_container[0])
                self.page.snack_bar = ft.SnackBar(ft.Text("❌ Incidente cancelado."), bgcolor=ft.Colors.RED_600)
                self.page.snack_bar.open = True
                # Invalidar caché del tablero kanban
                if self.on_refrescar_incidentes:
                    self.on_refrescar_incidentes()
                self.on_navigate("incidentes")
            except Exception as ex:
                self.page.snack_bar = ft.SnackBar(ft.Text(f"Error: {str(ex)}"), bgcolor=ft.Colors.RED_600)
                self.page.snack_bar.open = True
                self.page.update()
        
        modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("⚠️ Cancelar Incidente"),
            content=ft.Column([
                ft.Text("Esta acción no se puede deshacer.", color=ft.Colors.RED_600, weight=ft.FontWeight.BOLD),
                txt_motivo,
            ], tight=True, width=400),
            actions=[
                ft.TextButton("Volver", on_click=cerrar_modal),
                ft.ElevatedButton("Confirmar Cancelación", on_click=confirmar_cancelacion, bgcolor=ft.Colors.RED_600, color=ft.Colors.WHITE),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        modal_container[0] = modal
        self.page.open(modal)
        
    def abrir_modal_cotizacion(self, e):
        try:
            proveedores = self.servicio_proveedores.listar_proveedores()
            
            if not proveedores:
                def cerrar_advertencia(e):
                    self.page.close(dlg)
                    
                dlg = ft.AlertDialog(
                    title=ft.Text("Atención"),
                    content=ft.Text("No hay proveedores registrados en el sistema. Debe registrar al menos un proveedor antes de crear una cotización."),
                    actions=[ft.TextButton("Entendido", on_click=cerrar_advertencia)]
                )
                self.page.open(dlg)
                return

            dd_proveedor = ft.Dropdown(
                label="Proveedor",
                options=[ft.dropdown.Option(key=str(p.id_proveedor), text=f"{p.especialidad} - {p.nombre_completo}") for p in proveedores],
                width=350
            )
            txt_materiales = ft.TextField(label="Costo Materiales", value="0", keyboard_type=ft.KeyboardType.NUMBER)
            txt_mano_obra = ft.TextField(label="Costo Mano de Obra", value="0", keyboard_type=ft.KeyboardType.NUMBER)
            txt_dias = ft.TextField(label="Días Estimados", value="1", keyboard_type=ft.KeyboardType.NUMBER)
            txt_descripcion = ft.TextField(label="Descripción Trabajo", multiline=True, min_lines=2)

            def cerrar_modal(e):
                self.page.close(modal)

            def guardar_cotizacion(e):
                if not dd_proveedor.value:
                    self.page.snack_bar = ft.SnackBar(ft.Text("Seleccione un proveedor"))
                    self.page.snack_bar.open = True
                    self.page.update()
                    return

                try:
                    datos = {
                        "id_incidente": self.id_incidente,
                        "id_proveedor": int(dd_proveedor.value),
                        "materiales": float(txt_materiales.value or 0),
                        "mano_obra": float(txt_mano_obra.value or 0),
                        "descripcion": txt_descripcion.value,
                        "dias": int(txt_dias.value or 1)
                    }
                    
                    self.servicio.registrar_cotizacion(self.id_incidente, datos, "Sistema")
                    self.page.close(modal)
                    self.page.snack_bar = ft.SnackBar(ft.Text("✅ Cotización agregada exitosamente"), bgcolor=ft.Colors.GREEN_600)
                    self.page.snack_bar.open = True
                    # Invalidar caché del tablero kanban
                    if self.on_refrescar_incidentes:
                        self.on_refrescar_incidentes()
                    self.on_navigate("incidente_detalle", id_incidente=self.id_incidente)
                    
                except Exception as ex:
                    self.page.snack_bar = ft.SnackBar(ft.Text(f"Error: {str(ex)}"), bgcolor=ft.Colors.RED_600)
                    self.page.snack_bar.open = True
                    self.page.update()

            modal = ft.AlertDialog(
                modal=True,
                title=ft.Text("Agregar Cotización"),
                content=ft.Column([
                    dd_proveedor,
                    txt_materiales,
                    txt_mano_obra,
                    txt_dias,
                    txt_descripcion
                ], tight=True, width=400, spacing=10),
                actions=[
                    ft.TextButton("Cancelar", on_click=cerrar_modal),
                    ft.ElevatedButton("Guardar", on_click=guardar_cotizacion, bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE)
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )

            self.page.open(modal)
        
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error interno: {str(ex)}"), bgcolor=ft.Colors.RED_600)
            self.page.snack_bar.open = True
            self.page.update()
