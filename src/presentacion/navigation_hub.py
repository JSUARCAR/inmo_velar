from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Optional, List
import flet as ft

# Importar vistas (batch 1)
from src.presentacion.views import (
    crear_dashboard_view,
    crear_personas_list_view,
    crear_persona_form_view,
    crear_propiedades_list_view,
    crear_propiedad_form_view,
    crear_contratos_list_view,
    crear_contrato_mandato_form_view,
    crear_contrato_arrendamiento_form_view,
    crear_recaudos_list_view,
    crear_recaudo_form_view,
    crear_liquidaciones_list_view,
    crear_liquidacion_form_view
)
from src.presentacion.views.liquidaciones_asesores_list_view import crear_liquidaciones_asesores_list_view
from src.presentacion.views.liquidacion_asesor_form_view import crear_liquidacion_asesor_form_view
from src.presentacion.views.liquidacion_asesor_detail_view import crear_modal_detalle_liquidacion
from src.presentacion.views.pagos_asesores_list_view import crear_pagos_asesores_list_view
from src.presentacion.views.saldos_favor_list_view import build_saldos_favor_list_view
from src.presentacion.views.saldo_favor_form_view import build_saldo_favor_form_view
from src.presentacion.views.configuracion_view import build_configuracion_view
from src.presentacion.views.usuario_form_view import build_usuario_form_view
from src.presentacion.views.incrementos_view import build_incrementos_view
from src.presentacion.views.desocupaciones_list_view import crear_desocupaciones_list_view
from src.presentacion.views.desocupacion_form_view import crear_desocupacion_form_view
from src.presentacion.views.desocupacion_checklist_view import crear_desocupacion_checklist_view
from src.presentacion.views.seguros_list_view import crear_seguros_list_view
from src.presentacion.views.seguro_form_view import crear_seguro_form_view
from src.presentacion.views.poliza_form_view import crear_poliza_form_view
from src.presentacion.views.recibos_publicos_list_view import crear_recibos_publicos_list_view
from src.presentacion.views.recibo_publico_form_view import crear_recibo_publico_form_view

class NavigationHub:
    """
    Centraliza la lógica de construcción de vistas para el Router.
    Esto permite fragmentar main.py y desacoplar la UI de la lógica de arranque.
    """
    def __init__(self, page: ft.Page, usuario: Any, router: Any, navbar: Any, servicios: Dict[str, Any], on_logout: Callable):
        self.page = page
        self.usuario = usuario
        self.router = router
        self.navbar = navbar
        self.servicios = servicios
        self.on_logout = on_logout

    def registrar_vistas(self):
        """Registra todos los constructores de vista en el router."""
        self.router.registrar_vista("dashboard", self._build_dashboard)
        self.router.registrar_vista("personas", self._build_personas_list)
        self.router.registrar_vista("persona_form", self._build_persona_form)
        self.router.registrar_vista("propiedades", self._build_propiedades_list)
        self.router.registrar_vista("propiedad_form", self._build_propiedad_form)
        self.router.registrar_vista("contratos", self._build_contratos_list)
        self.router.registrar_vista("contrato_mandato", self._build_contrato_mandato)
        self.router.registrar_vista("contrato_arrendamiento", self._build_contrato_arrendamiento)
        self.router.registrar_vista("recaudos", self._build_recaudos_list)
        self.router.registrar_vista("recaudo_form", self._build_recaudo_form)
        self.router.registrar_vista("liquidaciones", self._build_liquidaciones_list)
        self.router.registrar_vista("liquidacion_form", self._build_liquidacion_form)
        self.router.registrar_vista("incidentes", self._build_incidentes_list)
        self.router.registrar_vista("incidente_reportar", self._build_incidente_reportar)
        self.router.registrar_vista("incidente_detalle", self._build_incidente_detalle)
        self.router.registrar_vista("proveedores", self._build_proveedores_list)
        self.router.registrar_vista("proveedor_form", self._build_proveedor_form)
        self.router.registrar_vista("seguros", self._build_seguros_list)
        self.router.registrar_vista("seguro_form", self._build_seguro_form)
        self.router.registrar_vista("poliza_form", self._build_poliza_form)
        self.router.registrar_vista("recibos_publicos", self._build_recibos_publicos_list)
        self.router.registrar_vista("recibo_publico_form", self._build_recibo_publico_form)
        self.router.registrar_vista("liquidaciones_asesores", self._build_liquidaciones_asesores_list)
        self.router.registrar_vista("liquidacion_asesor_form", self._build_liquidacion_asesor_form)
        self.router.registrar_vista("pagos_asesores", self._build_pagos_asesores_list)
        self.router.registrar_vista("saldos_favor", self._build_saldos_favor_list)
        self.router.registrar_vista("saldo_favor_form", self._build_saldo_favor_form)
        self.router.registrar_vista("configuracion", self._build_configuracion)
        self.router.registrar_vista("usuario_form", self._build_usuario_form)
        self.router.registrar_vista("incrementos", self._build_incrementos)
        self.router.registrar_vista("desocupaciones", self._build_desocupaciones_list)
        self.router.registrar_vista("desocupacion_form", self._build_desocupacion_form)
        self.router.registrar_vista("desocupacion_checklist", self._build_desocupacion_checklist)

    def _build_dashboard(self):
        return crear_dashboard_view(self.page, self.usuario, self.on_logout, on_navigate=self.router.navegar_a)

    def _build_personas_list(self):
        def handle_nueva_persona():
            self.router.navegar_a("persona_form")
        
        def handle_editar_persona(id_persona: int):
            self.router.navegar_a("persona_form", persona_id=id_persona)
            
        self.navbar.set_title("Gestión de Personas")
        return crear_personas_list_view(self.page, handle_nueva_persona, handle_editar_persona)

    def _build_persona_form(self, persona_id=None):
        def handle_guardar():
            self.router.refrescar_vista("personas")
            self.router.navegar_a("personas")
            
        self.navbar.set_title(f"{'Editar' if persona_id else 'Nueva'} Persona")
        return crear_persona_form_view(self.page, handle_guardar, lambda: self.router.navegar_a("personas"), persona_id)

    def _build_propiedades_list(self):
        self.navbar.set_title("Gestión de Propiedades")
        return crear_propiedades_list_view(
            self.page, 
            lambda: self.router.navegar_a("propiedad_form"), 
            lambda id_p: self.router.navegar_a("propiedad_form", propiedad_id=id_p)
        )

    def _build_propiedad_form(self, propiedad_id=None):
        def handle_guardar():
            self.router.refrescar_vista("propiedades")
            self.router.navegar_a("propiedades")
            
        self.navbar.set_title("Formulario Propiedad")
        return crear_propiedad_form_view(self.page, handle_guardar, lambda: self.router.navegar_a("propiedades"), propiedad_id)

    def _build_contratos_list(self):
        self.navbar.set_title("Gestión de Contratos")
        return crear_contratos_list_view(
            self.page, 
            self.servicios["contratos"],
            lambda: self.router.navegar_a("contrato_mandato"),
            lambda: self.router.navegar_a("contrato_arrendamiento"),
            lambda id_c: self.router.navegar_a("contrato_mandato", contrato_id=id_c),
            lambda id_c: self.router.navegar_a("contrato_arrendamiento", contrato_id=id_c),
            self._handle_renovar_mandato,
            self._handle_renovar_arrendamiento,
            self._handle_terminar_mandato,
            self._handle_terminar_arrendamiento,
            self._handle_ver_detalle_contrato
        )

    def _build_contrato_mandato(self, contrato_id=None):
        self.navbar.set_title("Contrato de Mandato")
        return crear_contrato_mandato_form_view(
            self.page, 
            lambda: (self.router.refrescar_vista("contratos"), self.router.navegar_a("contratos")), 
            lambda: self.router.navegar_a("contratos"), 
            contrato_id
        )

    def _build_contrato_arrendamiento(self, contrato_id=None):
        self.navbar.set_title("Contrato de Arrendamiento")
        return crear_contrato_arrendamiento_form_view(
            self.page, 
            lambda: (self.router.refrescar_vista("contratos"), self.router.navegar_a("contratos")), 
            lambda: self.router.navegar_a("contratos"), 
            contrato_id
        )

    def _build_recaudos_list(self):
        self.navbar.set_title("Gestión de Recaudos")
        return crear_recaudos_list_view(
            self.page,
            self.servicios["financiero"],
            lambda: self.router.navegar_a("recaudo_form"),
            self._handle_ver_detalle_recaudo,
            on_aprobar=self._handle_aprobar_recaudo,
            on_reversar=self._handle_reversar_recaudo
        )

    def _build_recaudo_form(self):
        self.navbar.set_title("Nuevo Recaudo")
        return crear_recaudo_form_view(
            self.page,
            self.servicios["financiero"],
            self.servicios["contratos"],
            lambda: (self.router.refrescar_vista("recaudos"), self.router.navegar_a("recaudos")),
            lambda: self.router.navegar_a("recaudos")
        )

    def _build_liquidaciones_list(self):
        self.navbar.set_title("Gestión de Liquidaciones")
        return crear_liquidaciones_list_view(
            self.page,
            self.servicios["financiero"],
            lambda: self.router.navegar_a("liquidacion_form"),
            self._handle_ver_detalle_liquidacion,
            self._handle_aprobar_liquidacion,
            self._handle_marcar_pagada_liquidacion,
            self._handle_editar_liquidacion
        )

    def _build_liquidacion_form(self, liquidacion_id=None):
        self.navbar.set_title("Editar Liquidación" if liquidacion_id else "Nueva Liquidación")
        return crear_liquidacion_form_view(
            self.page,
            self.servicios["financiero"],
            self.servicios["contratos"],
            lambda: (self.page.snack_bar_show("✅ Liquidación generada"), self.router.navegar_a("liquidaciones")), # Simplificado
            lambda: self.router.navegar_a("liquidaciones"),
            liquidacion_id
        )

    def _build_incidentes_list(self):
        from src.presentacion.views.incidentes_kanban_view import IncidentesKanbanView
        from src.aplicacion.servicios.servicio_incidentes import ServicioIncidentes
        serv = ServicioIncidentes(self.servicios["db_manager"])
        self.navbar.set_title("Gestión de Incidentes")
        return IncidentesKanbanView(self.page, serv, self.servicios["propiedades"], self.router.navegar_a)

    def _build_incidente_reportar(self):
        from src.presentacion.views.incidente_form_view import IncidenteFormView
        from src.aplicacion.servicios.servicio_incidentes import ServicioIncidentes
        serv = ServicioIncidentes(self.servicios["db_manager"])
        self.navbar.set_title("Reportar Incidente")
        return IncidenteFormView(self.page, serv, self.servicios["db_manager"], lambda r, **kw: (self.router.refrescar_vista("incidentes") if r=="incidentes" else None, self.router.navegar_a(r, **kw)))

    def _build_incidente_detalle(self, id_incidente):
        from src.presentacion.views.incidente_detail_view import IncidenteDetailView
        from src.aplicacion.servicios.servicio_incidentes import ServicioIncidentes
        from src.aplicacion.servicios.servicio_proveedores import ServicioProveedores
        s_inc = ServicioIncidentes(self.servicios["db_manager"])
        s_prov = ServicioProveedores(self.servicios["db_manager"])
        self.navbar.set_title(f"Detalle Incidente #{id_incidente}")
        return IncidenteDetailView(self.page, s_inc, s_prov, id_incidente, self.router.navegar_a, on_refrescar_incidentes=lambda: self.router.refrescar_vista("incidentes"))

    def _build_proveedores_list(self):
        from src.presentacion.views.proveedores_list_view import ProveedoresListView
        from src.aplicacion.servicios.servicio_proveedores import ServicioProveedores
        serv = ServicioProveedores(self.servicios["db_manager"])
        self.navbar.set_title("Gestión de Proveedores")
        return ProveedoresListView(self.page, serv, self.router.navegar_a)

    def _build_proveedor_form(self, id_proveedor=None):
        from src.presentacion.views.proveedor_form_view import ProveedorFormView
        from src.aplicacion.servicios.servicio_proveedores import ServicioProveedores
        s_prov = ServicioProveedores(self.servicios["db_manager"])
        self.navbar.set_title("Registro de Proveedor")
        return ProveedorFormView(self.page, s_prov, self.servicios["personas"], self.router.navegar_a, id_proveedor)

    def _build_seguros_list(self):
        self.navbar.set_title("Gestión de Seguros")
        return crear_seguros_list_view(self.page, lambda: self.router.navegar_a("seguro_form"), lambda id: self.router.navegar_a("seguro_form", seguro_id=id), on_nueva_poliza=lambda: self.router.navegar_a("poliza_form"))

    def _build_poliza_form(self):
        self.navbar.set_title("Asignar Nueva Póliza")
        return crear_poliza_form_view(self.page, lambda: (self.router.refrescar_vista("seguros"), self.router.navegar_a("seguros")), lambda: self.router.navegar_a("seguros"))

    def _build_seguro_form(self, seguro_id=None):
        self.navbar.set_title("Formulario de Seguro")
        return crear_seguro_form_view(self.page, lambda: (self.router.refrescar_vista("seguros"), self.router.navegar_a("seguros")), lambda: self.router.navegar_a("seguros"), seguro_id)

    def _build_recibos_publicos_list(self):
        self.navbar.set_title("Gestión de Recibos Públicos")
        return crear_recibos_publicos_list_view(
            self.page, self.servicios["recibos_publicos"], self.servicios["propiedades"], self.servicios["notificaciones"],
            lambda: self.router.navegar_a("recibo_publico_form"), lambda id: self.router.navegar_a("recibo_publico_form", recibo_id=id),
            self._handle_marcar_pagado_recibo, self._handle_eliminar_recibo, on_ver_detalle=self._handle_ver_detalle_recibo
        )

    def _build_recibo_publico_form(self, recibo_id=None):
        self.navbar.set_title(f"{'Editar' if recibo_id else 'Nuevo'} Recibo Público")
        return crear_recibo_publico_form_view(self.page, self.servicios["recibos_publicos"], self.servicios["propiedades"], lambda: (self.router.refrescar_vista("recibos_publicos"), self.router.navegar_a("recibos_publicos")), lambda: self.router.navegar_a("recibos_publicos"), recibo_id, self.usuario.nombre_usuario)

    def _build_liquidaciones_asesores_list(self):
        self.navbar.set_title("Liquidación de Asesores")
        return crear_liquidaciones_asesores_list_view(
            self.page, self.servicios["liquidacion_asesores"], self.servicios["personas"],
            lambda: self.router.navegar_a("liquidacion_asesor_form"), lambda id: self.router.navegar_a("liquidacion_asesor_form", liquidacion_id=id),
            self._handle_ver_detalle_liq_asesor, self._handle_aprobar_liq_asesor, self._handle_anular_liq_asesor
        )

    def _build_liquidacion_asesor_form(self, liquidacion_id=None):
        self.navbar.set_title(f"{'Editar' if liquidacion_id else 'Nueva'} Liquidación de Asesor")
        return crear_liquidacion_asesor_form_view(self.page, self.servicios["liquidacion_asesores"], self.servicios["contratos"], self.servicios["personas"], self._handle_guardar_liq_asesor, lambda: self.router.navegar_a("liquidaciones_asesores"), liquidacion_id)

    def _build_pagos_asesores_list(self):
        self.navbar.set_title("Gestión de Pagos")
        return crear_pagos_asesores_list_view(self.page, self.servicios["liquidacion_asesores"], self.servicios["personas"], self._handle_registrar_pago_asesor, self._handle_rechazar_pago_asesor, lambda id: None, self._handle_ver_detalle_liq_asesor)

    def _build_saldos_favor_list(self):
        self.navbar.set_title("Gestión de Saldos a Favor")
        # Logica de beneficiarios (propietarios/asesores) omitida para brevedad pero debe incluirse
        return build_saldos_favor_list_view(self.page, self.servicios["saldos_favor"], lambda: self.router.navegar_a("saldo_favor_form"), self._handle_aplicar_saldo, self._handle_devolver_saldo, self._handle_eliminar_saldo, [], [])

    def _build_saldo_favor_form(self, saldo_id=None):
        self.navbar.set_title("Nuevo Saldo a Favor")
        return build_saldo_favor_form_view(self.page, self._handle_guardar_saldo, lambda: self.router.navegar_a("saldos_favor"), [], [], None)

    def _build_configuracion(self):
        self.navbar.set_title("Configuración del Sistema")
        return build_configuracion_view(self.page, self.servicios["configuracion"], self.usuario, lambda: self.router.navegar_a("usuario_form"), lambda id: self.router.navegar_a("usuario_form", usuario_id=id))

    def _build_usuario_form(self, usuario_id=None):
        u_editar = self.servicios["configuracion"].obtener_usuario(usuario_id) if usuario_id else None
        self.navbar.set_title("Editar Usuario" if u_editar else "Nuevo Usuario")
        return build_usuario_form_view(self.page, self.servicios["configuracion"], self.usuario, lambda: (self.router.refrescar_vista("configuracion"), self.router.navegar_a("configuracion")), lambda: self.router.navegar_a("configuracion"), u_editar)

    def _build_incrementos(self):
        self.navbar.set_title("Incrementos de Canon (IPC)")
        return build_incrementos_view(self.page, self.servicios["contratos"], self.usuario)

    def _build_desocupaciones_list(self):
        self.navbar.set_title("Gestión de Desocupaciones")
        return crear_desocupaciones_list_view(self.page, self.servicios["desocupaciones"], self.servicios["documental"], lambda: self.router.navegar_a("desocupacion_form"), lambda id: self.router.navegar_a("desocupacion_checklist", id_desocupacion=id))

    def _build_desocupacion_form(self):
        self.navbar.set_title("Nueva Desocupación")
        return crear_desocupacion_form_view(self.page, self.servicios["desocupaciones"], lambda: self.router.navegar_a("desocupaciones"), lambda: self.router.navegar_a("desocupaciones"))

    def _build_desocupacion_checklist(self, id_desocupacion=None):
        self.navbar.set_title("Checklist de Desocupación")
        return crear_desocupacion_checklist_view(self.page, self.servicios["desocupaciones"], id_desocupacion, lambda: self.router.navegar_a("desocupaciones"))

    def _handle_renovar_mandato(self, id_contrato: int):
        def confirmar(e):
            try:
                self.servicios["contratos"].renovar_mandato(id_contrato, self.usuario.nombre_usuario)
                self.page.close(dlg)
                self.page.snack_bar = ft.SnackBar(ft.Text("Contrato de mandato renovado exitosamente (Sin IPC)"))
                self.page.snack_bar.open = True
                self.page.update()
                self.router.navegar_a("contratos")
            except Exception as ex:
                self.page.close(dlg)
                self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al renovar: {ex}"), bgcolor=ft.Colors.ERROR)
                self.page.snack_bar.open = True
                self.page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar Renovación Mandato"),
            content=ft.Text("¿Está seguro de renovar este mandato?\n\nSe extenderá por su duración original.\nNO se aplicará incremento de IPC (Canon se mantiene igual)."),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.page.close(dlg)),
                ft.TextButton("Renovar", on_click=confirmar),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.open(dlg)

    def _handle_renovar_arrendamiento(self, id_contrato: int):
        def confirmar(e):
            try:
                self.servicios["contratos"].renovar_arrendamiento(id_contrato, self.usuario.nombre_usuario)
                self.page.close(dlg)
                self.page.snack_bar = ft.SnackBar(ft.Text("Contrato renovado exitosamente por 1 periodo"))
                self.page.snack_bar.open = True
                self.page.update()
                self.router.refrescar_vista("contratos")
                self.router.refrescar_vista("propiedades")
                self.router.navegar_a("contratos")
            except Exception as ex:
                self.page.close(dlg)
                self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al renovar: {ex}"), bgcolor=ft.Colors.ERROR)
                self.page.snack_bar.open = True
                self.page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar Renovación"),
            content=ft.Text("¿Está seguro de renovar este contrato?\n\nSe extenderá automáticamente por su duración original y se aplicará el incremento del IPC vigente."),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.page.close(dlg)),
                ft.TextButton("Renovar", on_click=confirmar),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.open(dlg)

    def _handle_terminar_mandato(self, id_contrato: int):
        motivo_field = ft.TextField(label="Motivo de Terminación", multiline=True, autofocus=True)
        def confirmar(e):
            if not motivo_field.value:
                motivo_field.error_text = "El motivo es obligatorio"
                motivo_field.update()
                return
            try:
                self.servicios["contratos"].terminar_mandato(id_contrato, motivo_field.value, self.usuario.nombre_usuario)
                self.page.close(dlg)
                self.page.snack_bar = ft.SnackBar(ft.Text("Mandato terminado exitosamente"))
                self.page.snack_bar.open = True
                self.page.update()
                self.router.navegar_a("contratos")
            except Exception as ex:
                self.page.close(dlg)
                self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al terminar: {ex}"), bgcolor=ft.Colors.RED)
                self.page.snack_bar.open = True
                self.page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Terminar Mandato"),
            content=ft.Column([
                ft.Text("¿Está seguro de terminar este contrato?\nEsta acción no se puede deshacer."),
                motivo_field
            ], tight=True, width=400),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.page.close(dlg)),
                ft.TextButton("TERMINAR", on_click=confirmar, style=ft.ButtonStyle(color=ft.Colors.RED)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.open(dlg)

    def _handle_terminar_arrendamiento(self, id_contrato: int):
        motivo_field = ft.TextField(label="Motivo de Terminación", multiline=True, autofocus=True)
        def confirmar(e):
            if not motivo_field.value:
                motivo_field.error_text = "El motivo es obligatorio"
                motivo_field.update()
                return
            try:
                self.servicios["contratos"].terminar_arrendamiento(id_contrato, motivo_field.value, self.usuario.nombre_usuario)
                self.page.close(dlg)
                self.page.snack_bar = ft.SnackBar(ft.Text("Arrendamiento terminado exitosamente. Propiedad liberada."))
                self.page.snack_bar.open = True
                self.page.update()
                self.router.navegar_a("contratos")
            except Exception as ex:
                self.page.close(dlg)
                self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al terminar: {ex}"), bgcolor=ft.Colors.RED)
                self.page.snack_bar.open = True
                self.page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Terminar Arrendamiento"),
            content=ft.Column([
                ft.Text("¿Está seguro de terminar este contrato?\nSe liberará la propiedad inmediatamente."),
                motivo_field
            ], tight=True, width=400),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.page.close(dlg)),
                ft.TextButton("TERMINAR", on_click=confirmar, style=ft.ButtonStyle(color=ft.Colors.RED)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.open(dlg)

    def _handle_ver_detalle_contrato(self, tipo: str, id_c: int):
        # Lógica de detalle de contrato (idéntica a main.py)
        try:
            detalles = []
            titulo = ""
            if tipo == "MANDATO":
                titulo = f"Detalle Mandato #{id_c}"
                info = self.servicios["contratos"].obtener_detalle_mandato_ui(id_c)
                if info:
                    detalles = [
                        ("ID Contrato", str(info["id_contrato"])),
                        ("Propiedad", f"{info['direccion_propiedad']} (ID: {info['id_propiedad']})"),
                        ("Matrícula", info['matricula']),
                        ("Propietario", f"{info['nombre_propietario']} (ID Rol: {info['id_propietario']})"),
                        ("Asesor", f"{info['nombre_asesor']} (ID Rol: {info['id_asesor']})"),
                        ("Fecha Inicio", info["fecha_inicio"]),
                        ("Fecha Fin", info["fecha_fin"]),
                        ("Duración", f"{info['duracion']} meses"),
                        ("Canon", f"${info['canon']:,.0f}"),
                        ("Comisión", f"{info['comision']/100}%"),
                        ("Estado", info["estado"]),
                        ("Creado el", info["created_at"]),
                    ]
            elif tipo == "ARRIENDO":
                titulo = f"Detalle Arriendo #{id_c}"
                info = self.servicios["contratos"].obtener_detalle_arriendo_ui(id_c)
                if info:
                     detalles = [
                        ("ID Contrato", str(info["id_contrato"])),
                        ("Propiedad", f"{info['direccion_propiedad']} (ID: {info['id_propiedad']})"),
                        ("Matrícula", info['matricula']),
                        ("Inquilino", f"{info['nombre_inquilino']} (ID Rol: {info['id_inquilino']})"),
                        ("Codeudor", f"{info['nombre_codeudor']} (ID Rol: {info['id_codeudor'] if info['id_codeudor'] else 'N/A'})"),
                        ("Fecha Inicio", info["fecha_inicio"]),
                        ("Fecha Fin", info["fecha_fin"]),
                        ("Canon", f"${info['canon']:,.0f}"),
                        ("Depósito", f"${info['deposito']:,.0f}" if info['deposito'] else "$0"),
                        ("Estado", info["estado"]),
                        ("Creado el", info["created_at"]),
                    ]

            if not detalles:
                self.page.snack_bar = ft.SnackBar(ft.Text("No se pudo cargar la información detallada del contrato"))
                self.page.snack_bar.open = True
                self.page.update()
                return

            filas = [
                ft.Row([
                    ft.Text(k, weight=ft.FontWeight.BOLD, width=120, size=13),
                    ft.Text(str(v), size=13, expand=True, selectable=True)
                ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.START)
                for k, v in detalles
            ]
            
            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Text(titulo),
                content=ft.Column(controls=filas, tight=True, width=500, scroll=ft.ScrollMode.AUTO),
                actions=[ft.TextButton("Cerrar", on_click=lambda e: self.page.close(dlg))],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            self.page.open(dlg)
        except Exception as e:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error: {e}"))
            self.page.snack_bar.open = True
            self.page.update()

    def _handle_ver_detalle_recaudo(self, id_recaudo: int):
        from src.presentacion.components.document_manager import DocumentManager
        try:
            info = self.servicios["financiero"].obtener_detalle_recaudo_ui(id_recaudo)
            if not info:
                self.page.snack_bar = ft.SnackBar(ft.Text("No se pudo cargar la información del recaudo"))
                self.page.snack_bar.open = True
                self.page.update()
                return

            filas = []
            for k, v in [
                ("ID Recaudo", str(info['id_recaudo'])),
                ("Fecha de Pago", info['fecha_pago']),
                ("Valor Total", f"${info['valor_total']:,}"),
                ("Método de Pago", info['metodo_pago']),
                ("Referencia Bancaria", info['referencia_bancaria']),
                ("Estado", info['estado_recaudo']),
            ]:
                filas.append(ft.Row([ft.Text(k, weight=ft.FontWeight.BOLD, width=150, size=13), ft.Text(str(v), size=13, expand=True, selectable=True)]))
            
            filas.append(ft.Divider(height=10, color="#e0e0e0"))
            for k, v in [("ID Contrato", str(info['id_contrato_a'])), ("Propiedad", f"{info['direccion_propiedad']} (ID: {info['id_propiedad']})")]:
                filas.append(ft.Row([ft.Text(k, weight=ft.FontWeight.BOLD, width=150, size=13), ft.Text(str(v), size=13, expand=True, selectable=True)]))
            
            filas.append(ft.Divider(height=10, color="#e0e0e0"))
            filas.append(ft.Text("Conceptos del Pago:", weight=ft.FontWeight.BOLD, size=14))
            
            if info['conceptos']:
                tabla = ft.DataTable(
                    columns=[ft.DataColumn(ft.Text("Tipo")), ft.DataColumn(ft.Text("Período")), ft.DataColumn(ft.Text("Valor"))],
                    rows=[ft.DataRow(cells=[ft.DataCell(ft.Text(c['tipo_concepto'])), ft.DataCell(ft.Text(c['periodo'])), ft.DataCell(ft.Text(f"${c['valor']:,}"))]) for c in info['conceptos']],
                    border=ft.border.all(1, "#e0e0e0"),
                    heading_row_color="#f5f5f5",
                )
                filas.append(ft.Container(content=tabla, padding=ft.padding.only(top=5)))
            
            filas.append(ft.Divider(height=10, color="#e0e0e0"))
            filas.append(ft.Row([ft.Text("Observaciones", weight=ft.FontWeight.BOLD, width=150, size=13), ft.Text(info['observaciones'], size=13, expand=True, selectable=True)]))
            
            filas.append(ft.Divider(height=10, color="#e0e0e0"))
            filas.append(ft.Text("Documentos de Soporte:", weight=ft.FontWeight.BOLD, size=14))
            filas.append(ft.Container(content=DocumentManager(entidad_tipo="RECAUDO", entidad_id=str(id_recaudo), page=self.page, height=200), padding=ft.padding.only(top=5)))

            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Text(f"Detalle Recaudo #{id_recaudo}", weight=ft.FontWeight.BOLD),
                content=ft.Column(controls=filas, tight=True, width=600, scroll=ft.ScrollMode.AUTO),
                actions=[
                    ft.TextButton("Imprimir Comprobante", icon=ft.Icons.PRINT, on_click=lambda e: self._handle_imprimir_recaudo(id_recaudo)),
                    ft.TextButton("Cerrar", on_click=lambda e: self.page.close(dlg))
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            self.page.open(dlg)
        except Exception as e:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error: {e}"))
            self.page.snack_bar.open = True
            self.page.update()

    def _handle_imprimir_recaudo(self, id_recaudo: int):
        try:
            path_pdf = self.servicios["financiero"].generar_comprobante_pago(id_recaudo)
            self.page.launch_url(f"file:///{path_pdf.replace('\\', '/')}")
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Comprobante generado"), bgcolor="green")
            self.page.snack_bar.open = True
            self.page.update()
        except Exception as e:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al generar PDF: {e}"), bgcolor="red")
            self.page.snack_bar.open = True
            self.page.update()

    def _handle_aprobar_recaudo(self, id_recaudo: int):
        try:
            self.servicios["financiero"].aprobar_recaudo(id_recaudo, self.usuario.nombre_usuario)
            self.page.snack_bar = ft.SnackBar(ft.Text("Recaudo aprobado exitosamente"), bgcolor="green")
            self.page.snack_bar.open = True
            self.page.update()
            self.router.refrescar_vista("recaudos")
            self.router.navegar_a("recaudos")
        except Exception as e:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al aprobar: {e}"), bgcolor="red")
            self.page.snack_bar.open = True
            self.page.update()

    def _handle_reversar_recaudo(self, id_recaudo: int):
        def confirmar(e):
            try:
                self.servicios["financiero"].reversar_recaudo(id_recaudo, self.usuario.nombre_usuario)
                self.page.close(dlg)
                self.page.snack_bar = ft.SnackBar(ft.Text("Recaudo reversado exitosamente"), bgcolor="orange")
                self.page.snack_bar.open = True
                self.page.update()
                self.router.refrescar_vista("recaudos")
                self.router.navegar_a("recaudos")
            except Exception as ex:
                self.page.close(dlg)
                self.page.snack_bar = ft.SnackBar(ft.Text(f"Error al reversar: {ex}"), bgcolor="red")
                self.page.snack_bar.open = True
                self.page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar Reverso"),
            content=ft.Text("¿Está seguro de anular este recaudo?\nEsta acción no se puede deshacer."),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: self.page.close(dlg)),
                ft.TextButton("Reversar", on_click=confirmar, style=ft.ButtonStyle(color=ft.Colors.RED)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.open(dlg)

    def _build_contrato_mandato(self, contrato_id=None):
        self.navbar.set_title("Contrato de Mandato")
        return crear_contrato_mandato_form_view(
            self.page, 
            lambda: (self.router.refrescar_vista("contratos"), self.router.navegar_a("contratos")), 
            lambda: self.router.navegar_a("contratos"), 
            contrato_id
        )

    def _build_contrato_arrendamiento(self, contrato_id=None):
        self.navbar.set_title("Contrato de Arrendamiento")
        return crear_contrato_arrendamiento_form_view(
            self.page, 
            lambda: (self.router.refrescar_vista("contratos"), self.router.navegar_a("contratos")), 
            lambda: self.router.navegar_a("contratos"), 
            contrato_id
        )

    # --- Handlers de Dominio ---

    def _handle_ver_detalle_liquidacion(self, id_propietario: int, periodo: str):
        try:
            info = self.servicios["financiero"].obtener_detalle_liquidacion_propietario_ui(id_propietario, periodo)
            if not info:
                self.page.snack_bar = ft.SnackBar(ft.Text("No se pudo cargar la información"))
                self.page.snack_bar.open = True
                self.page.update()
                return

            content = ft.Column([
                ft.Text(f"Liquidación: {info['nombre_propietario']} - {info['periodo']}", size=18, weight="bold"),
                ft.Text(f"Neto a Pagar: ${info['neto_total_a_pagar']:,}", size=20, color="blue", weight="bold"),
            ], scroll="auto", height=500, width=700)
            
            dlg = ft.AlertDialog(
                title=ft.Text("Detalle Liquidación"),
                content=content,
                actions=[ft.TextButton("Cerrar", on_click=lambda e: self.page.close(dlg))]
            )
            self.page.open(dlg)
        except Exception as e:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error: {e}"), bgcolor="red")
            self.page.snack_bar.open = True
            self.page.update()

    def _handle_aprobar_liquidacion(self, id_propietario: int, periodo: str):
        try:
            self.servicios["financiero"].aprobar_liquidacion_propietario(id_propietario, periodo, self.usuario.nombre_usuario)
            self.page.snack_bar = ft.SnackBar(ft.Text("Liquidación aprobada"), bgcolor="green")
            self.page.snack_bar.open = True
            self.router.refrescar_vista("liquidaciones")
            self.router.navegar_a("liquidaciones")
        except Exception as e:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error: {e}"), bgcolor="red")
            self.page.snack_bar.open = True
            self.page.update()

    def _handle_marcar_pagada_liquidacion(self, id_propietario: int, periodo: str):
        txt_ref = ft.TextField(label="Referencia de Pago")
        def confirmar(e):
            try:
                self.servicios["financiero"].marcar_liquidacion_propietario_pagada(
                    id_propietario, periodo, datetime.now().strftime("%Y-%m-%d"), "Transferencia", txt_ref.value, self.usuario.nombre_usuario
                )
                self.page.close(dlg)
                self.page.snack_bar = ft.SnackBar(ft.Text("Liquidación pagada"), bgcolor="green")
                self.page.snack_bar.open = True
                self.router.navegar_a("liquidaciones")
            except Exception as ex:
                self.page.snack_bar = ft.SnackBar(ft.Text(f"Error: {ex}"), bgcolor="red")
                self.page.snack_bar.open = True
                self.page.update()

        dlg = ft.AlertDialog(title=ft.Text("Registrar Pago"), content=txt_ref, actions=[ft.TextButton("Confirmar", on_click=confirmar)])
        self.page.open(dlg)

    def _handle_marcar_pagado_recibo(self, id_recibo: int): pass
    def _handle_eliminar_recibo(self, id_recibo: int): pass
    def _handle_ver_detalle_recibo(self, id_recibo: int): pass
    def _handle_editar_liquidacion(self, id_prop, per):
        liq = self.servicios["financiero"].repo_liquidacion.listar_por_propietario_y_periodo(id_prop, per)
        if liq: self.router.navegar_a("liquidacion_form", liquidacion_id=liq[0].id_liquidacion)

    def _handle_ver_detalle_liq_asesor(self, id_l):
        modal = crear_modal_detalle_liquidacion(self.page, self.servicios["liquidacion_asesores"], self.servicios["notificaciones"], id_l, lambda: self.page.close(modal))
        self.page.open(modal)

    def _handle_aprobar_liq_asesor(self, id_l):
        self.servicios["liquidacion_asesores"].aprobar_liquidacion(id_l, self.usuario.nombre_usuario)
        self.router.refrescar_vista("liquidaciones_asesores")
        self.router.navegar_a("liquidaciones_asesores")

    def _handle_anular_liq_asesor(self, id_l): pass
    def _handle_guardar_liq_asesor(self, d): pass
    def _handle_registrar_pago_asesor(self, id_l): pass
    def _handle_rechazar_pago_asesor(self, id_l): pass

    def _handle_aplicar_saldo(self, id_s):
        self.servicios["saldos_favor"].aplicar_saldo(id_s, "Aplicado", self.usuario.nombre_usuario)
        self.router.refrescar_vista("saldos_favor")
        self.router.navegar_a("saldos_favor")

    def _handle_devolver_saldo(self, id_s):
        self.servicios["saldos_favor"].devolver_saldo(id_s, "Devuelto", self.usuario.nombre_usuario)
        self.router.refrescar_vista("saldos_favor")
        self.router.navegar_a("saldos_favor")

    def _handle_eliminar_saldo(self, id_s):
        self.servicios["saldos_favor"].eliminar_saldo(id_s, self.usuario.nombre_usuario)
        self.router.refrescar_vista("saldos_favor")
        self.router.navegar_a("saldos_favor")

    def _handle_guardar_saldo(self, d):
        self.servicios["saldos_favor"].registrar_saldo(**d, usuario=self.usuario.nombre_usuario)
        self.router.refrescar_vista("saldos_favor")
        self.router.navegar_a("saldos_favor")
