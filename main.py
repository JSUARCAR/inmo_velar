"""
Entry Point: Sistema de Gestión Inmobiliaria

Punto de entrada principal de la aplicación de escritorio.
"""

import flet as ft
from pathlib import Path
from datetime import datetime

from src.infraestructura.configuracion.settings import obtener_configuracion
from src.infraestructura.persistencia.database import db_manager
from src.presentacion.views.login_view import crear_login_view


def main(page: ft.Page):
    """
    Función principal de la aplicación Flet.
    
    Args:
        page: Página principal de Flet
    """
    # Obtener configuración
    config = obtener_configuracion()
    
    # Configurar página
    page.title = config.app_name
    page.window_width = 1200
    page.window_height = 800
    page.window_min_width = 400
    page.window_min_height = 600
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    
    # Inicializar base de datos si existe el esquema
    schema_path = Path("src/infraestructura/migraciones/schema.sql")
    if schema_path.exists():
        try:
            db_manager.inicializar_base_datos(schema_path)
        except Exception as e:
            print(f"Error inicializando BD: {e}")
    
    def on_login_success(usuario):
        """Callback al iniciar sesión exitosamente."""
        print(f"Login exitoso para: {usuario.nombre_usuario}") 
        print("DEBUG: Entrando a on_login_success") 
        
        # Importar componentes necesarios
        from src.presentacion.router import Router
        from src.presentacion.components.sidebar import Sidebar
        from src.presentacion.components.navbar import Navbar
        from src.presentacion.components.shell import Shell
        from src.presentacion.views.alerts_view import AlertsView
        from src.presentacion.theme import colors
        from src.presentacion.views import (
            crear_dashboard_view,
            crear_personas_list_view,
            crear_persona_form_view,
            crear_propiedades_list_view,
            crear_propiedad_form_view,
            crear_contratos_list_view,
            crear_contrato_mandato_form_view,
            crear_contrato_arrendamiento_form_view
        )
        from src.presentacion.views.recaudos_list_view import crear_recaudos_list_view
        from src.presentacion.views.recaudo_form_view import crear_recaudo_form_view
        from src.presentacion.views.liquidaciones_list_view import crear_liquidaciones_list_view
        from src.presentacion.views.liquidacion_form_view import crear_liquidacion_form_view
        from src.presentacion.views.seguros_list_view import crear_seguros_list_view
        from src.presentacion.views.seguro_form_view import crear_seguro_form_view
        from src.presentacion.views.poliza_form_view import crear_poliza_form_view
        from src.presentacion.views.recibos_publicos_list_view import crear_recibos_publicos_list_view
        from src.presentacion.views.recibo_publico_form_view import crear_recibo_publico_form_view
        from src.presentacion.views.liquidaciones_asesores_list_view import crear_liquidaciones_asesores_list_view
        from src.presentacion.views.liquidacion_asesor_form_view import crear_liquidacion_asesor_form_view
        from src.presentacion.views.liquidacion_asesor_detail_view import crear_modal_detalle_liquidacion
        from src.presentacion.views.pagos_asesores_list_view import crear_pagos_asesores_list_view
        from src.presentacion.views.saldos_favor_list_view import build_saldos_favor_list_view
        from src.presentacion.views.saldo_favor_form_view import build_saldo_favor_form_view
        from src.presentacion.views.configuracion_view import build_configuracion_view
        from src.presentacion.views.configuracion_view import build_configuracion_view
        from src.presentacion.views.usuario_form_view import build_usuario_form_view
        from src.presentacion.views.incrementos_view import build_incrementos_view

        from src.presentacion.views.desocupaciones_list_view import crear_desocupaciones_list_view
        from src.presentacion.views.desocupacion_form_view import crear_desocupacion_form_view
        from src.presentacion.views.desocupacion_checklist_view import crear_desocupacion_checklist_view
        from src.presentacion.components.document_manager import DocumentManager
        
        
        from src.aplicacion.servicios.servicio_contratos import ServicioContratos # Importar Servicio
        from src.aplicacion.servicios.servicio_financiero import ServicioFinanciero
        from src.aplicacion.servicios.servicio_propiedades import ServicioPropiedades
        from src.aplicacion.servicios.servicio_recibos_publicos import ServicioRecibosPublicos
        from src.aplicacion.servicios.servicio_alertas import ServicioAlertas
        from src.infraestructura.repositorios.repositorio_recibo_publico_sqlite import RepositorioReciboPublicoSQLite
        from src.infraestructura.persistencia.repositorio_propiedad_sqlite import RepositorioPropiedadSQLite
        from src.aplicacion.servicios.servicio_dashboard import ServicioDashboard
        
        # NOTA: Router se inicializa después de crear el Shell (línea ~180)
        
        # Inicializar Servicios
        print("DEBUG: Inicializando Servicios...")
        servicio_contratos = ServicioContratos(db_manager)
        servicio_financiero = ServicioFinanciero(db_manager)
        servicio_propiedades = ServicioPropiedades(db_manager)
        servicio_dashboard = ServicioDashboard(db_manager)
        
        # Inicializar repositorios y servicio de recibos públicos
        print("DEBUG: Inicializando Repositorios...")
        repo_recibo_publico =RepositorioReciboPublicoSQLite(db_manager)
        repo_propiedad = RepositorioPropiedadSQLite(db_manager)
        servicio_recibos_publicos = ServicioRecibosPublicos(repo_recibo_publico, repo_propiedad)
        
        # Inicializar repositorios y servicio de liquidaciones asesores
        from src.infraestructura.repositorios import (
            RepositorioLiquidacionAsesorSQLite,
            RepositorioDescuentoAsesorSQLite,
            RepositorioPagoAsesorSQLite
        )
        from src.infraestructura.persistencia.repositorio_asesor_sqlite import RepositorioAsesorSQLite
        from src.infraestructura.persistencia.repositorio_persona_sqlite import RepositorioPersonaSQLite
        from src.infraestructura.servicios.servicio_documentos_pdf import ServicioDocumentosPDF
        from src.infraestructura.persistencia.repositorio_contrato_arrendamiento_sqlite import RepositorioContratoArrendamientoSQLite
        from src.aplicacion.servicios.servicio_liquidacion_asesores import ServicioLiquidacionAsesores
        from src.aplicacion.servicios.servicio_personas import ServicioPersonas
        from src.aplicacion.servicios.servicio_saldos_favor import ServicioSaldosFavor
        from src.aplicacion.servicios.servicio_notificaciones import ServicioNotificaciones
        
        repo_liquidacion_asesor = RepositorioLiquidacionAsesorSQLite(db_manager)
        repo_descuento_asesor = RepositorioDescuentoAsesorSQLite(db_manager)
        repo_pago_asesor = RepositorioPagoAsesorSQLite(db_manager)
        repo_contrato_arrendamiento = RepositorioContratoArrendamientoSQLite(db_manager)
        repo_asesor = RepositorioAsesorSQLite(db_manager)
        repo_persona = RepositorioPersonaSQLite(db_manager)
        servicio_documentos_pdf = ServicioDocumentosPDF()
        
        servicio_liquidacion_asesores = ServicioLiquidacionAsesores(
            repo_liquidacion_asesor,
            repo_descuento_asesor,
            repo_pago_asesor,
            repo_contrato_arrendamiento,
            repo_propiedad,
            servicio_documentos_pdf,
            repo_asesor,
            repo_persona
        )
        servicio_personas = ServicioPersonas(db_manager)

        servicio_saldos_favor = ServicioSaldosFavor(db_manager)

        servicio_notificaciones = ServicioNotificaciones()
        
        from src.aplicacion.servicios.servicio_documental import ServicioDocumental
        from src.infraestructura.repositorios.repositorio_documento_sqlite import RepositorioDocumentoSQLite
        
        repo_documento = RepositorioDocumentoSQLite(db_manager)
        servicio_documental = ServicioDocumental(repo_documento)

        from src.aplicacion.servicios.servicio_desocupaciones import ServicioDesocupaciones
        servicio_desocupaciones = ServicioDesocupaciones(db_manager)
        
        # Inicializar Servicio de Alertas
        servicio_alertas = ServicioAlertas()
        
        # Inicializar Servicio de Configuración
        from src.aplicacion.servicios.servicio_configuracion import ServicioConfiguracion
        servicio_configuracion = ServicioConfiguracion(db_manager)

        # Drawer de alertas
        drawer_alertas = AlertsView(servicio_alertas, servicio_recibos_publicos, servicio_dashboard, servicio_liquidacion_asesores)
        page.drawer = drawer_alertas
        
        def abrir_alertas():
            page.drawer.open = True
            page.drawer.update()
        
        def on_logout():
            print("Cerrando sesión...")
            page.clean()
            page.drawer = None
            page.add(crear_login_view(page, on_login_success))
            page.update()
        
        # =======================
        # ARQUITECTURA SHELL (Optimización 17.2)
        # =======================
        
        # Crear componentes singleton (solo se crean una vez)
        print("DEBUG: Creando Shell...")
        print("🔨 Creando Shell con componentes estáticos...")
        sidebar_singleton = None  # Se creará después con referencia a router
        navbar_singleton = Navbar("Dashboard", abrir_alertas)  # Navbar genérico inicial
        
        # Crear Router temporal (se actualizará con Shell)
        router_temp = Router(page, usuario, shell=None)
        
        # Ahora crear Sidebar con router (necesita callback navegar_a)
        sidebar_singleton = Sidebar(usuario, router_temp.navegar_a, on_logout)
        
        # Crear Shell con componentes estáticos
        shell = Shell(sidebar=sidebar_singleton, navbar=navbar_singleton)
        
        # Actualizar Router con referencia a Shell
        router_temp.shell = shell
        router = router_temp  # Router final con Shell
        
        print(f"✅ Shell creado exitosamente con Sidebar y Navbar estáticos")
        
        # Montar Shell en página (UNA SOLA VEZ - nunca se destruye)
        page.clean()
        page.add(shell)
        page.update()
        print("✅ Shell montado en página")
        
        # --- Registrar Vistas en el Router ---
        
        def build_dashboard():
            """Constructor de vista Dashboard."""
            return crear_dashboard_view(page, usuario, on_logout, on_navigate=router.navegar_a)
        
        def build_personas_list():
            """Constructor de vista Listado de Personas."""
            print("\n>>> BUILD_PERSONAS_LIST: Iniciando construcción...")
            
            def handle_nueva_persona():
                print(">>> BUILD_PERSONAS_LIST: Handle nueva persona")
                router.navegar_a("persona_form")
            
            def handle_editar_persona(id_persona: int):
                print(f">>> BUILD_PERSONAS_LIST: Handle editar persona {id_persona}")
                router.navegar_a("persona_form", persona_id=id_persona)
            
            # Actualizar título del Navbar singleton
            navbar_singleton.set_title("Gestión de Personas")
            
            print(">>> BUILD_PERSONAS_LIST: Llamando crear_personas_list_view...")
            vista_personas = crear_personas_list_view(page, handle_nueva_persona, handle_editar_persona)
            print(f">>> BUILD_PERSONAS_LIST: Vista creada: {type(vista_personas).__name__}")
            
            return vista_personas
        
        def build_persona_form(persona_id=None):
            """Constructor de vista Formulario de Persona."""
            def handle_guardar():
                # Invalidar caché de la vista de personas
                router.refrescar_vista("personas")
                # Volver al listado
                router.navegar_a("personas")
            
            def handle_cancelar():
                # Volver al listado
                router.navegar_a("personas")
            
            # Actualizar título
            navbar_singleton.set_title(f"{'Editar' if persona_id else 'Nueva'} Persona")
            
            return crear_persona_form_view(page, handle_guardar, handle_cancelar, persona_id)
        
        # Registrar vistas
        router.registrar_vista("dashboard", build_dashboard)
        router.registrar_vista("personas", build_personas_list)
        router.registrar_vista("persona_form", build_persona_form)
        
        # --- Rutas de Propiedades ---
        
        def build_propiedades_list():
            """Constructor de vista Listado de Propiedades."""
            
            def handle_nueva_propiedad():
                router.navegar_a("propiedad_form")
            
            def handle_editar_propiedad(id_propiedad: int):
                router.navegar_a("propiedad_form", propiedad_id=id_propiedad)
            
            navbar_singleton.set_title("Gestión de Propiedades")
            
            vista_propiedades = crear_propiedades_list_view(page, handle_nueva_propiedad, handle_editar_propiedad)
            
            return vista_propiedades
        
        def build_propiedad_form(propiedad_id=None):
            """Constructor de vista Formulario Propiedad."""
            navbar_singleton.set_title("Formulario Propiedad")
            
            # id_propiedad ya viene como argumento gracias al Router
            print(f"DEBUG: propiedad_id recibido: {propiedad_id}")
            
            def handle_guardar():
                # Invalidar caché de propiedades
                router.refrescar_vista("propiedades")
                router.navegar_a("propiedades")

            def handle_cancelar():
                router.navegar_a("propiedades")

            form = crear_propiedad_form_view(page, handle_guardar, handle_cancelar, propiedad_id)
            return form

        def build_contratos_list():
            """Constructor de vista Listado de Contratos."""
            print("\n>>> BUILD_CONTRATOS_LIST: Iniciando construcción...")
            
            def handle_nuevo_mandato():
                router.navegar_a("contrato_mandato")
                
            def handle_nuevo_arriendo():
                router.navegar_a("contrato_arrendamiento")
                
            def handle_editar_mandato(id_contrato: int):
                router.navegar_a("contrato_mandato", contrato_id=id_contrato)

            def handle_editar_arriendo(id_contrato: int):
                router.navegar_a("contrato_arrendamiento", contrato_id=id_contrato)

            def handle_renovar_arrendamiento(id_contrato: int):
                def confirmar_renovacion(e):
                    try:
                        servicio_contratos.renovar_arrendamiento(id_contrato, usuario.nombre_usuario)
                        page.close(dlg_renovacion)
                        page.snack_bar = ft.SnackBar(ft.Text("Contrato renovado exitosamente por 1 periodo"))
                        page.snack_bar.open = True
                        page.update()
                        # Invalidar caché de contratos y propiedades
                        router.refrescar_vista("contratos")
                        router.refrescar_vista("propiedades")
                        router.navegar_a("contratos")
                    except Exception as ex:
                        page.close(dlg_renovacion)
                        page.snack_bar = ft.SnackBar(ft.Text(f"Error al renovar: {ex}"), bgcolor=ft.Colors.ERROR)
                        page.snack_bar.open = True
                        page.update()

                def cancelar_renovacion(e):
                    page.close(dlg_renovacion)

                dlg_renovacion = ft.AlertDialog(
                    modal=True,
                    title=ft.Text("Confirmar Renovación"),
                    content=ft.Text("¿Está seguro de renovar este contrato?\n\nSe extenderá automáticamente por su duración original y se aplicará el incremento del IPC vigente."),
                    actions=[
                        ft.TextButton("Cancelar", on_click=cancelar_renovacion),
                        ft.TextButton("Renovar", on_click=confirmar_renovacion),
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
                page.open(dlg_renovacion)

            def handle_renovar_mandato(id_contrato: int):
                def confirmar_renovacion_m(e):
                    try:
                        servicio_contratos.renovar_mandato(id_contrato, usuario.nombre_usuario)
                        page.close(dlg_renovacion_m)
                        page.snack_bar = ft.SnackBar(ft.Text("Contrato de mandato renovado exitosamente (Sin IPC)"))
                        page.snack_bar.open = True
                        page.update()
                        router.navegar_a("contratos")
                    except Exception as ex:
                        page.close(dlg_renovacion_m)
                        page.snack_bar = ft.SnackBar(ft.Text(f"Error al renovar: {ex}"), bgcolor=ft.Colors.ERROR)
                        page.snack_bar.open = True
                        page.update()

                def cancelar_renovacion_m(e):
                    page.close(dlg_renovacion_m)

                dlg_renovacion_m = ft.AlertDialog(
                    modal=True,
                    title=ft.Text("Confirmar Renovación Mandato"),
                    content=ft.Text("¿Está seguro de renovar este mandato?\n\nSe extenderá por su duración original.\nNO se aplicará incremento de IPC (Canon se mantiene igual)."),
                    actions=[
                        ft.TextButton("Cancelar", on_click=cancelar_renovacion_m),
                        ft.TextButton("Renovar", on_click=confirmar_renovacion_m),
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
                page.open(dlg_renovacion_m)

            def handle_terminar_mandato(id_contrato: int):
                motivo_field = ft.TextField(label="Motivo de Terminación", multiline=True, autofocus=True)
                
                def confirmar_terminacion_m(e):
                    if not motivo_field.value:
                        motivo_field.error_text = "El motivo es obligatorio"
                        motivo_field.update()
                        return

                    try:
                        servicio_contratos.terminar_mandato(id_contrato, motivo_field.value, usuario.nombre_usuario)
                        page.close(dlg_term_m)
                        page.snack_bar = ft.SnackBar(ft.Text("Mandato terminado exitosamente"))
                        page.snack_bar.open = True
                        page.update()
                        router.navegar_a("contratos")
                    except Exception as ex:
                        page.close(dlg_term_m)
                        page.snack_bar = ft.SnackBar(ft.Text(f"Error al terminar: {ex}"), bgcolor=ft.Colors.RED)
                        page.snack_bar.open = True
                        page.update()

                def cancelar_term_m(e):
                    page.close(dlg_term_m)

                dlg_term_m = ft.AlertDialog(
                    modal=True,
                    title=ft.Text("Terminar Mandato"),
                    content=ft.Column([
                        ft.Text("¿Está seguro de terminar este contrato?\nEsta acción no se puede deshacer."),
                        motivo_field
                    ], tight=True, width=400),
                    actions=[
                        ft.TextButton("Cancelar", on_click=cancelar_term_m),
                        ft.TextButton("TERMINAR", on_click=confirmar_terminacion_m, style=ft.ButtonStyle(color=ft.Colors.RED)),
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
                page.open(dlg_term_m)

            def handle_terminar_arrendamiento(id_contrato: int):
                motivo_field = ft.TextField(label="Motivo de Terminación", multiline=True, autofocus=True)
                
                def confirmar_terminacion_a(e):
                    if not motivo_field.value:
                        motivo_field.error_text = "El motivo es obligatorio"
                        motivo_field.update()
                        return

                    try:
                        servicio_contratos.terminar_arrendamiento(id_contrato, motivo_field.value, usuario.nombre_usuario)
                        page.close(dlg_term_a)
                        page.snack_bar = ft.SnackBar(ft.Text("Arrendamiento terminado exitosamente. Propiedad liberada."))
                        page.snack_bar.open = True
                        page.update()
                        router.navegar_a("contratos")
                    except Exception as ex:
                        page.close(dlg_term_a)
                        page.snack_bar = ft.SnackBar(ft.Text(f"Error al terminar: {ex}"), bgcolor=ft.Colors.RED)
                        page.snack_bar.open = True
                        page.update()

                def cancelar_term_a(e):
                    page.close(dlg_term_a)

                dlg_term_a = ft.AlertDialog(
                    modal=True,
                    title=ft.Text("Terminar Arrendamiento"),
                    content=ft.Column([
                        ft.Text("¿Está seguro de terminar este contrato?\nSe liberará la propiedad inmediatamente."),
                        motivo_field
                    ], tight=True, width=400),
                    actions=[
                        ft.TextButton("Cancelar", on_click=cancelar_term_a),
                        ft.TextButton("TERMINAR", on_click=confirmar_terminacion_a, style=ft.ButtonStyle(color=ft.Colors.RED)),
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
                page.open(dlg_term_a)

            def handle_ver_detalle(tipo: str, id_c: int):
                try:
                    detalles = []
                    titulo = ""
                    
                    if tipo == "MANDATO":
                        titulo = f"Detalle Mandato #{id_c}"
                        info = servicio_contratos.obtener_detalle_mandato_ui(id_c)
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
                        info = servicio_contratos.obtener_detalle_arriendo_ui(id_c)
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
                        page.snack_bar = ft.SnackBar(ft.Text("No se pudo cargar la información detallada del contrato"))
                        page.snack_bar.open = True
                        page.update()
                        return

                    # Construir contenido del diálogo
                    filas = []
                    for k, v in detalles:
                        filas.append(
                            ft.Row([
                                ft.Text(k, weight=ft.FontWeight.BOLD, width=120, size=13),
                                ft.Text(str(v), size=13, expand=True, selectable=True)
                            ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.START)
                        )
                    
                    content = ft.Column(
                        controls=filas,
                        tight=True,
                        width=500,
                        scroll=ft.ScrollMode.AUTO
                    )
                    
                    def close_dlg(e):
                        page.close(dlg)
                    
                    dlg = ft.AlertDialog(
                        modal=True,
                        title=ft.Text(titulo),
                        content=content,
                        actions=[
                            ft.TextButton("Cerrar", on_click=close_dlg)
                        ],
                        actions_alignment=ft.MainAxisAlignment.END,
                    )
                    
                    page.open(dlg)

                except Exception as e:
                    print(f"Error mostrando detalle: {e}")
                    import traceback
                    traceback.print_exc()
                    page.snack_bar = ft.SnackBar(ft.Text(f"Error: {e}"))
                    page.snack_bar.open = True
                    page.update()
            
            navbar_singleton.set_title("Gestión de Contratos")
            
            vista = crear_contratos_list_view(
                page, 
                servicio_contratos, # Injected service
                handle_nuevo_mandato, 
                handle_nuevo_arriendo,
                handle_editar_mandato,
                handle_editar_arriendo,
                handle_renovar_mandato,
                handle_renovar_arrendamiento,
                handle_terminar_mandato,
                handle_terminar_arrendamiento,
                handle_ver_detalle
            )
            return vista

        def build_contrato_mandato(contrato_id=None):
            """Constructor de vista Formulario Mandato."""
            def handle_guardar():
                router.refrescar_vista("contratos")
                router.navegar_a("contratos")
            
            def handle_cancelar():
                router.navegar_a("contratos")

            navbar_singleton.set_title("Contrato de Mandato")
            return crear_contrato_mandato_form_view(page, handle_guardar, handle_cancelar, contrato_id)

        def build_contrato_arrendamiento(contrato_id=None):
            """Constructor de vista Formulario Arriendo."""
            def handle_guardar():
                router.refrescar_vista("contratos")
                router.navegar_a("contratos")
            
            def handle_cancelar():
                router.navegar_a("contratos")

            navbar_singleton.set_title("Contrato de Arrendamiento")
            return crear_contrato_arrendamiento_form_view(page, handle_guardar, handle_cancelar, contrato_id)
        
        def build_recaudos_list():
            """Constructor de vista Listado de Recaudos."""
            
            def handle_nuevo_recaudo():
                router.navegar_a("recaudo_form")
            
            def handle_ver_detalle_recaudo(id_recaudo: int):
                """Muestra el detalle completo de un recaudo en un diálogo"""
                try:
                    info = servicio_financiero.obtener_detalle_recaudo_ui(id_recaudo)
                    
                    if not info:
                        page.snack_bar = ft.SnackBar(ft.Text("No se pudo cargar la información del recaudo"))
                        page.snack_bar.open = True
                        page.update()
                        return
                    
                    # Construir sección de información básica
                    detalles_basicos = [
                        ("ID Recaudo", str(info['id_recaudo'])),
                        ("Fecha de Pago", info['fecha_pago']),
                        ("Valor Total", f"${info['valor_total']:,}"),
                        ("Método de Pago", info['metodo_pago']),
                        ("Referencia Bancaria", info['referencia_bancaria']),
                        ("Estado", info['estado_recaudo']),
                    ]
                    
                    # Construir sección de contrato/propiedad
                    detalles_contrato = [
                        ("ID Contrato", str(info['id_contrato_a'])),
                        ("Propiedad", f"{info['direccion_propiedad']} (ID: {info['id_propiedad']})"),
                    ]
                    
                    # Construir filas de información básica
                    filas = []
                    for k, v in detalles_basicos:
                        filas.append(
                            ft.Row([
                                ft.Text(k, weight=ft.FontWeight.BOLD, width=150, size=13),
                                ft.Text(str(v), size=13, expand=True, selectable=True)
                            ], alignment=ft.MainAxisAlignment.START)
                        )
                    
                    # Agregar separador
                    filas.append(ft.Divider(height=10, color="#e0e0e0"))
                    
                    # Agregar información del contrato
                    for k, v in detalles_contrato:
                        filas.append(
                            ft.Row([
                                ft.Text(k, weight=ft.FontWeight.BOLD, width=150, size=13),
                                ft.Text(str(v), size=13, expand=True, selectable=True)
                            ], alignment=ft.MainAxisAlignment.START)
                        )
                    
                    # Agregar separador y título de conceptos
                    filas.append(ft.Divider(height=10, color="#e0e0e0"))
                    filas.append(ft.Text("Conceptos del Pago:", weight=ft.FontWeight.BOLD, size=14))
                    
                    # Agregar tabla de conceptos
                    if info['conceptos']:
                        conceptos_rows = []
                        for concepto in info['conceptos']:
                            conceptos_rows.append(
                                ft.DataRow(
                                    cells=[
                                        ft.DataCell(ft.Text(concepto['tipo_concepto'], size=12)),
                                        ft.DataCell(ft.Text(concepto['periodo'], size=12)),
                                        ft.DataCell(ft.Text(f"${concepto['valor']:,}", size=12)),
                                    ]
                                )
                            )
                        
                        tabla_conceptos = ft.DataTable(
                            columns=[
                                ft.DataColumn(ft.Text("Tipo", weight=ft.FontWeight.BOLD, size=12)),
                                ft.DataColumn(ft.Text("Período", weight=ft.FontWeight.BOLD, size=12)),
                                ft.DataColumn(ft.Text("Valor", weight=ft.FontWeight.BOLD, size=12)),
                            ],
                            rows=conceptos_rows,
                            border=ft.border.all(1, "#e0e0e0"),
                            heading_row_color="#f5f5f5",
                        )
                        filas.append(ft.Container(content=tabla_conceptos, padding=ft.padding.only(top=5)))
                    else:
                        filas.append(ft.Text("Sin conceptos registrados", size=12, italic=True, color="#666"))
                    
                    # Agregar observaciones
                    filas.append(ft.Divider(height=10, color="#e0e0e0"))
                    filas.append(
                        ft.Row([
                            ft.Text("Observaciones", weight=ft.FontWeight.BOLD, width=150, size=13),
                            ft.Text(info['observaciones'], size=13, expand=True, selectable=True)
                        ], alignment=ft.MainAxisAlignment.START)
                    )
                    
                    # Agregar auditoría si está disponible
                    filas.append(ft.Divider(height=10, color="#e0e0e0"))
                    filas.append(ft.Text("Auditoría:", weight=ft.FontWeight.BOLD, size=12, color="#666"))
                    filas.append(
                        ft.Text(f"Creado: {info['created_at']} por {info['created_by']}", size=11, color="#666")
                    )
                    if info['updated_at']:
                        filas.append(
                            ft.Text(f"Actualizado: {info['updated_at']} por {info['updated_by']}", size=11, color="#666")
                        )
                    
                    # Agregar Sección Documentos
                    filas.append(ft.Divider(height=10, color="#e0e0e0"))
                    filas.append(ft.Text("Documentos de Soporte:", weight=ft.FontWeight.BOLD, size=14))
                    filas.append(
                        ft.Container(
                            content=DocumentManager(
                                entidad_tipo="RECAUDO",
                                entidad_id=str(id_recaudo),
                                page=page,
                                height=200 # Altura reducida para el dialog
                            ),
                            padding=ft.padding.only(top=5)
                        )
                    )

                    # Crear contenido del diálogo
                    content = ft.Column(
                        controls=filas,
                        tight=True,
                        width=600,
                        scroll=ft.ScrollMode.AUTO
                    )
                    
                    def close_dlg(e):
                        page.close(dlg)
                    
                    dlg = ft.AlertDialog(
                        modal=True,
                        title=ft.Text(f"Detalle Recaudo #{id_recaudo}", weight=ft.FontWeight.BOLD),
                        content=content,
                        actions=[
                            ft.TextButton("Imprimir Comprobante", icon=ft.Icons.PRINT, on_click=lambda e: handle_imprimir_recaudo(id_recaudo)),
                            ft.TextButton("Cerrar", on_click=close_dlg)
                        ],
                        actions_alignment=ft.MainAxisAlignment.END,
                    )
                    
                    page.open(dlg)
                    
                except Exception as e:
                    print(f"Error mostrando detalle de recaudo: {e}")
                    import traceback
                    traceback.print_exc()
                    page.snack_bar = ft.SnackBar(ft.Text(f"Error: {e}"))
                    page.snack_bar.open = True
                    page.update()
            
            def handle_imprimir_recaudo(id_recaudo: int):
                try:
                    path_pdf = servicio_financiero.generar_comprobante_pago(id_recaudo)
                    page.launch_url(f"file:///{path_pdf.replace('\\', '/')}")
                    page.snack_bar = ft.SnackBar(ft.Text(f"Comprobante generado: {path_pdf}"), bgcolor="green")
                    page.snack_bar.open = True
                    page.update()
                except Exception as e:
                    page.snack_bar = ft.SnackBar(ft.Text(f"Error al generar PDF: {e}"), bgcolor="red")
                    page.snack_bar.open = True
                    page.update()

            
            def handle_aprobar_recaudo(id_recaudo: int):
                try:
                    servicio_financiero.aprobar_recaudo(id_recaudo, usuario.nombre_usuario)
                    page.snack_bar = ft.SnackBar(ft.Text("Recaudo aprobado exitosamente"), bgcolor="green")
                    page.snack_bar.open = True
                    page.update()
                    # Invalidar caché de recaudos
                    router.refrescar_vista("recaudos")
                    router.navegar_a("recaudos")
                except Exception as e:
                    page.snack_bar = ft.SnackBar(ft.Text(f"Error al aprobar: {e}"), bgcolor="red")
                    page.snack_bar.open = True
                    page.update()

            def handle_reversar_recaudo(id_recaudo: int):
                def confirmar_reverso(e):
                    try:
                        servicio_financiero.reversar_recaudo(id_recaudo, usuario.nombre_usuario)
                        page.close(dlg_reverso)
                        page.snack_bar = ft.SnackBar(ft.Text("Recaudo reversado exitosamente"), bgcolor="orange")
                        page.snack_bar.open = True
                        page.update()
                        # Invalidar caché de recaudos
                        router.refrescar_vista("recaudos")
                        router.navegar_a("recaudos")
                    except Exception as ex:
                        page.close(dlg_reverso)
                        page.snack_bar = ft.SnackBar(ft.Text(f"Error al reversar: {ex}"), bgcolor="red")
                        page.snack_bar.open = True
                        page.update()

                def cancelar_reverso(e):
                    page.close(dlg_reverso)

                dlg_reverso = ft.AlertDialog(
                    modal=True,
                    title=ft.Text("Confirmar Reverso"),
                    content=ft.Text("¿Está seguro de anular este recaudo?\nEsta acción no se puede deshacer."),
                    actions=[
                        ft.TextButton("Cancelar", on_click=cancelar_reverso),
                        ft.TextButton("Reversar", on_click=confirmar_reverso, style=ft.ButtonStyle(color=ft.Colors.RED)),
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
                page.open(dlg_reverso)
            
            navbar_singleton.set_title("Gestión de Recaudos")
            
            vista = crear_recaudos_list_view(
                page,
                servicio_financiero,
                handle_nuevo_recaudo,
                handle_ver_detalle_recaudo,
                on_aprobar=handle_aprobar_recaudo,
                on_reversar=handle_reversar_recaudo
            )
            return vista
        
        def build_recaudo_form():
            """Constructor de vista Formulario de Recaudo."""
            
            def handle_guardar():
                # Invalidar caché de recaudos
                router.refrescar_vista("recaudos")
                router.navegar_a("recaudos")
            
            def handle_cancelar():
                router.navegar_a("recaudos")
            
            navbar_singleton.set_title("Nuevo Recaudo")
            
            form = crear_recaudo_form_view(
                page,
                servicio_financiero,
                servicio_contratos,
                handle_guardar,
                handle_cancelar
            )
            return form
        
        def build_liquidaciones_list():
            """Constructor de vista Listado de Liquidaciones."""
            
            def handle_nueva_liquidacion():
                router.navegar_a("liquidacion_form")
            
            def handle_ver_detalle_liquidacion(id_propietario: int, periodo: str):
                try:
                    info = servicio_financiero.obtener_detalle_liquidacion_propietario_ui(id_propietario, periodo)
                    
                    if not info:
                        page.snack_bar = ft.SnackBar(ft.Text("No se pudo cargar la información"))
                        page.snack_bar.open = True
                        page.update()
                        return

                    # --- Construcción del Diálogo de Detalle ---
                    
                    # 1. Encabezado
                    header_content = ft.Column([
                        ft.Text(f"Liquidación Propietario: {info['nombre_propietario']} - {info['periodo']}", size=18, weight=ft.FontWeight.BOLD),
                        ft.Text(f"Documento: {info['documento_propietario']} | {info['cantidad_contratos']} contrato(s)", size=14, color="#666"),
                        ft.Container(
                            content=ft.Text(info['estado_consolidado'], color="white", size=12, weight=ft.FontWeight.BOLD),
                            bgcolor={
                                'En Proceso': '#ff9800', 
                                'Aprobada': '#2196f3', 
                                'Pagada': '#4caf50', 
                                'Cancelada': '#f44336',
                                'Mixto': '#9c27b0'
                            }.get(info['estado_consolidado'], "grey"),
                            padding=5,
                            border_radius=4
                        )
                    ], spacing=5)

                    # 2. Información General - Consolidada
                    filas_info = [
                        ("Propietario", info['nombre_propietario']),
                        ("Documento", info['documento_propietario']),
                        ("Período", info['periodo']),
                        ("Cantidad Contratos", str(info['cantidad_contratos'])),
                    ]
                    
                    if info['estado_consolidado'] == 'Pagada' and info.get('fecha_pago'):
                        filas_info.extend([
                            ("Fecha Pago", info['fecha_pago']),
                        ])
                    
                    col_info = ft.Column([
                        ft.Text("Información General", weight=ft.FontWeight.BOLD, color="#1976d2"),
                        ft.Column([
                            ft.Row([
                                ft.Text(k, weight=ft.FontWeight.BOLD, width=150, size=12),
                                ft.Text(str(v), size=12, expand=True)
                            ], vertical_alignment=ft.CrossAxisAlignment.START)
                            for k, v in filas_info
                        ], spacing=2)
                    ])

                    # 3. Financiero CONSOLIDADO
                    col_fin = ft.Column([
                        ft.Text("Totales Consolidados", weight=ft.FontWeight.BOLD, color="#1976d2", size=16),
                        # Ingresos
                        ft.Row([ft.Text("Total Canon:", width=150, weight=ft.FontWeight.BOLD), ft.Text(f"${info['total_canon_bruto']:,}", weight=ft.FontWeight.BOLD)]),
                        ft.Row([ft.Text("Total Ingresos:", width=150, weight=ft.FontWeight.BOLD), ft.Text(f"${info['total_ingresos']:,}", color="green", weight=ft.FontWeight.BOLD)]),
                        ft.Row([ft.Text("Total Egresos:", width=150, weight=ft.FontWeight.BOLD), ft.Text(f"${info['total_egresos']:,}", color="red", weight=ft.FontWeight.BOLD)]),
                        
                        ft.Divider(height=10),
                        
                        # Neto
                        ft.Container(
                            content=ft.Row([
                                ft.Text("NETO TOTAL A PAGAR:", size=16, weight=ft.FontWeight.BOLD),
                                ft.Text(f"${info['neto_total_a_pagar']:,}", size=18, weight=ft.FontWeight.BOLD, color="#1976d2")
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            bgcolor="#e3f2fd", padding=15, border_radius=5
                        )
                    ])
                    
                    
                    # 4. Detalles por Contrato (Tabla expandida con TODOS los egresos/deducciones)
                    tabla_contratos_rows = []
                    for contrato in info.get('contratos', []):
                        tabla_contratos_rows.append(
                            ft.DataRow(cells=[
                                ft.DataCell(ft.Text(contrato['direccion'], size=10)),
                                ft.DataCell(ft.Text(f"${contrato['canon_bruto']:,}", size=10)),
                                ft.DataCell(ft.Text(f"${contrato.get('otros_ingresos', 0):,}", size=10)),
                                ft.DataCell(ft.Text(f"${contrato['total_ingresos']:,}", size=10, weight=ft.FontWeight.BOLD)),
                                ft.DataCell(ft.Text(f"${contrato['comision_monto']:,}", size=10, color="#f44336")),
                                ft.DataCell(ft.Text(f"${contrato.get('iva_comision', 0):,}", size=10, color="#f44336")),
                                ft.DataCell(ft.Text(f"${contrato.get('impuesto_4x1000', 0):,}", size=10, color="#f44336")),
                                ft.DataCell(ft.Text(f"${contrato.get('gastos_administracion', 0):,}", size=10, color="#f44336")),
                                ft.DataCell(ft.Text(f"${contrato.get('gastos_servicios', 0):,}", size=10, color="#f44336")),
                                ft.DataCell(ft.Text(f"${contrato.get('gastos_reparaciones', 0):,}", size=10, color="#f44336")),
                                ft.DataCell(ft.Text(f"${contrato.get('otros_egresos', 0):,}", size=10, color="#f44336")),
                                ft.DataCell(ft.Text(f"${contrato['total_egresos']:,}", size=10, weight=ft.FontWeight.BOLD, color="#f44336")),
                                ft.DataCell(ft.Text(f"${contrato['neto_a_pagar']:,}", size=11, weight=ft.FontWeight.BOLD, color="#1976d2")),
                            ])
                        )
                    
                    tabla_contratos = ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("Propiedad", size=10, weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("Canon", size=10, weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("Otros Ing.", size=10, weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("Total Ing.", size=10, weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("Comisión", size=10, weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("IVA Com.", size=10, weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("4x1000", size=10, weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("G.Admin", size=10, weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("G.Serv.", size=10, weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("G.Rep.", size=10, weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("Otros Egr.", size=10, weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("Total Egr.", size=10, weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("NETO", size=11, weight=ft.FontWeight.BOLD)),
                        ],
                        rows=tabla_contratos_rows,
                        border=ft.border.all(1, "#e0e0e0"),
                        heading_row_color="#f5f5f5",
                        horizontal_lines=ft.border.BorderSide(1, "#f5f5f5"),
                        column_spacing=8,
                    )
                    
                    col_contratos = ft.Column([
                        ft.Text("Detalle por Contrato (Egresos/Deducciones)", weight=ft.FontWeight.BOLD, color="#1976d2", size=14),
                        ft.Text("Tabla completa con desglose de todos los conceptos", size=11, color="#666", italic=True),
                        ft.Container(
                            content=ft.Row([tabla_contratos], scroll=ft.ScrollMode.AUTO),
                            border=ft.border.all(1, "#ddd"), 
                            border_radius=4
                        )
                    ], spacing=5)

                    # 5. Observaciones por Contrato (si existen)
                    observaciones_contratos = []
                    for idx, contrato in enumerate(info.get('contratos', []), 1):
                        if contrato.get('observaciones'):
                            observaciones_contratos.append(
                                ft.Container(
                                    content=ft.Column([
                                        ft.Text(f"Contrato {idx} - {contrato['direccion']}", 
                                               size=12, weight=ft.FontWeight.BOLD, color="#1976d2"),
                                        ft.Text(contrato['observaciones'], size=11, color="#333")
                                    ], spacing=3),
                                    padding=8,
                                    bgcolor="#f9f9f9",
                                    border_radius=4,
                                    border=ft.border.all(1, "#e0e0e0")
                                )
                            )
                    
                    col_obs = ft.Column([
                        ft.Text("Observaciones", weight=ft.FontWeight.BOLD, color="#1976d2"),
                        ft.Column(observaciones_contratos, spacing=8) if observaciones_contratos else ft.Text("Sin observaciones", size=12, italic=True, color="#999")
                    ])


                    # 5. Documentos
                    docs_manager = DocumentManager(
                        entidad_tipo="LIQUIDACION_PROPIETARIO",
                        entidad_id=f"{id_propietario}_{periodo}",  # Combinación de propietario y período
                        page=page,
                        height=200
                    )

                    # Layout Content
                    content = ft.Column([
                        header_content,
                        ft.Divider(),
                        col_info,
                        ft.Divider(),
                        col_fin,
                        ft.Divider(),
                        col_contratos,  # Tabla de detalles por contrato
                        ft.Divider(),
                        col_obs,
                        ft.Divider(),
                        docs_manager
                    ], scroll=ft.ScrollMode.AUTO, height=650, width=800, spacing=15)


                    def handle_imprimir_liquidacion(e):
                        try:
                            path_pdf = servicio_financiero.generar_estado_cuenta_pdf(id_liquidacion)
                            page.launch_url(f"file:///{path_pdf.replace('\\', '/')}")
                            page.snack_bar = ft.SnackBar(ft.Text(f"Estado de cuenta generado"), bgcolor="green")
                            page.snack_bar.open = True
                            page.update()
                        except Exception as ex:
                            page.snack_bar = ft.SnackBar(ft.Text(f"Error al generar PDF: {ex}"), bgcolor="red")
                            page.snack_bar.open = True
                            page.update()

                    def close_dlg(e):
                        page.close(dlg)

                    dlg = ft.AlertDialog(
                        modal=True,
                        title=ft.Text(f"Liquidación Propietario: {info['nombre_propietario']}"),
                        content=content,
                        actions=[
                            ft.TextButton("Ver Estado de Cuenta", icon=ft.Icons.PICTURE_AS_PDF, on_click=handle_imprimir_liquidacion),
                            ft.TextButton("Cerrar", on_click=close_dlg)
                        ],
                        actions_alignment=ft.MainAxisAlignment.END,
                    )
                    page.open(dlg)

                except Exception as ex:
                    print(f"ERROR MOSTRANDO DETALLE: {ex}")
                    import traceback
                    traceback.print_exc()
                    page.snack_bar = ft.SnackBar(ft.Text(f"Error interno: {ex}"), bgcolor="red")
                    page.snack_bar.open = True
                    page.update()
            
            def handle_aprobar_liquidacion(id_propietario: int, periodo: str):
                try:
                    affected = servicio_financiero.aprobar_liquidacion_propietario(id_propietario, periodo, usuario.nombre_usuario)
                    page.snack_bar = ft.SnackBar(ft.Text(f"{affected} liquidación(es) aprobada(s) exitosamente"), bgcolor="#4caf50")
                    page.snack_bar.open = True
                    router.navegar_a("liquidaciones")  # Recargar
                except Exception as ex:
                    page.snack_bar = ft.SnackBar(ft.Text(f"Error: {ex}"), bgcolor="#f44336")
                    page.snack_bar.open = True
                page.update()
            
            def handle_marcar_pagada_liquidacion(id_propietario: int, periodo: str):
                # Dialog para ingresar datos de pago
                txt_fecha = ft.TextField(label="Fecha de Pago", value=datetime.now().date().isoformat())
                txt_metodo = ft.TextField(label="Método de Pago", value="Transferencia Electrónica")
                txt_referencia = ft.TextField(label="Número de Comprobante", autofocus=True)
                
                def confirmar_pago(e):
                    if not txt_referencia.value:
                        txt_referencia.error_text = "El comprobante es obligatorio"
                        txt_referencia.update()
                        return
                    
                    try:
                        affected = servicio_financiero.marcar_liquidacion_propietario_pagada(
                            id_propietario,
                            periodo,
                            txt_fecha.value,
                            txt_metodo.value,
                            txt_referencia.value,
                            usuario.nombre_usuario
                        )
                        page.close(dlg)
                        page.snack_bar = ft.SnackBar(ft.Text(f"{affected} liquidación(es) marcada(s) como pagada(s)"), bgcolor="#4caf50")
                        page.snack_bar.open = True
                        router.navegar_a("liquidaciones")  # Recargar
                    except Exception as ex:
                        page.close(dlg)
                        page.snack_bar = ft.SnackBar(ft.Text(f"Error: {ex}"), bgcolor="#f44336")
                        page.snack_bar.open = True
                    page.update()
                
                def cancelar(e):
                    page.close(dlg)
                
                dlg = ft.AlertDialog(
                    modal=True,
                    title=ft.Text("Registrar Pago a Propietario"),
                    content=ft.Column([
                        txt_fecha,
                        txt_metodo,
                        txt_referencia,
                    ], tight=True, width=400),
                    actions=[
                        ft.TextButton("Cancelar", on_click=cancelar),
                        ft.TextButton("CONFIRMAR PAGO", on_click=confirmar_pago, style=ft.ButtonStyle(color="#4caf50")),
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
                page.open(dlg)
            
            def handle_editar_liquidacion(id_propietario: int, periodo: str):
                """
                Permite editar una liquidación en estado 'En Proceso'.
                Navega al formulario de liquidación con el ID de la primera liquidación encontrada.
                """
                try:
                    # Obtener las liquidaciones del propietario para el período
                    liquidaciones = servicio_financiero.repo_liquidacion.listar_por_propietario_y_periodo(id_propietario, periodo)
                    
                    if not liquidaciones:
                        page.snack_bar = ft.SnackBar(ft.Text("No se encontraron liquidaciones para editar"), bgcolor="#f44336")
                        page.snack_bar.open = True
                        page.update()
                        return
                    
                    # Validar que estén en estado "En Proceso"
                    if liquidaciones[0].estado_liquidacion != 'En Proceso':
                        page.snack_bar = ft.SnackBar(
                            ft.Text(f"Solo se pueden editar liquidaciones en estado 'En Proceso' (Estado actual: {liquidaciones[0].estado_liquidacion})"), 
                            bgcolor="#f44336"
                        )
                        page.snack_bar.open = True
                        page.update()
                        return
                    
                    # Navegar al formulario de edición con el ID de la primera liquidación
                    # Nota: Si hay múltiples contratos, se editará el primero
                    router.navegar_a("liquidacion_form", liquidacion_id=liquidaciones[0].id_liquidacion)
                    
                except Exception as ex:
                    print(f"Error al editar liquidación: {ex}")
                    import traceback
                    traceback.print_exc()
                    page.snack_bar = ft.SnackBar(ft.Text(f"Error: {ex}"), bgcolor="#f44336")
                    page.snack_bar.open = True
                    page.update()
            
            navbar_singleton.set_title("Gestión de Liquidaciones")
            
            vista = crear_liquidaciones_list_view(
                page,
                servicio_financiero,
                handle_nueva_liquidacion,
                handle_ver_detalle_liquidacion,
                handle_aprobar_liquidacion,
                handle_marcar_pagada_liquidacion,
                handle_editar_liquidacion
            )
            return vista
        
        def build_liquidacion_form(liquidacion_id=None):
            """Constructor de vista Formulario de Liquidación."""
            
            def handle_guardar():
                print("\n=== DEBUG [main.py]: handle_guardar (callback principal) INICIADO ===")
                # Mostrar feedback de éxito
                print("DEBUG [main.py]: Creando SnackBar...")
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("✅ Liquidación generada exitosamente"),
                    bgcolor="#4caf50",
                    duration=3000
                )
                page.snack_bar.open = True
                print("DEBUG [main.py]: SnackBar.open = True")
                page.update()
                print("DEBUG [main.py]: page.update() ejecutado")
                
                # Navegar a la lista
                print("DEBUG [main.py]: Navegando a 'liquidaciones'...")
                router.navegar_a("liquidaciones")
                print("=== DEBUG [main.py]: handle_guardar FINALIZADO ===\n")
            
            def handle_cancelar():
                router.navegar_a("liquidaciones")
            
            # Actualizar título según si es nueva o edición
            if liquidacion_id:
                navbar_singleton.set_title("Editar Liquidación")
            else:
                navbar_singleton.set_title("Nueva Liquidación")
            
            form = crear_liquidacion_form_view(
                page,
                servicio_financiero,
                servicio_contratos,
                handle_guardar,
                handle_cancelar,
                liquidacion_id  # Pasar el ID al formulario
            )
            return form
        
        # --- Rutas de Incidentes ---
        
        def build_incidentes_list():
            """Constructor de vista Listado de Incidentes."""
            from src.presentacion.views.incidentes_kanban_view import IncidentesKanbanView
            from src.aplicacion.servicios.servicio_incidentes import ServicioIncidentes
            
            servicio_incidentes = ServicioIncidentes(db_manager)
            from src.aplicacion.servicios.servicio_propiedades import ServicioPropiedades
            servicio_propiedades = ServicioPropiedades(db_manager)
            
            navbar_singleton.set_title("Gestión de Incidentes")
            
            vista = IncidentesKanbanView(page, servicio_incidentes, servicio_propiedades, router.navegar_a)
            
            return vista
        
        def build_incidente_reportar():
            """Constructor de vista Reportar Incidente."""
            from src.presentacion.views.incidente_form_view import IncidenteFormView
            from src.aplicacion.servicios.servicio_incidentes import ServicioIncidentes
            
            servicio_incidentes = ServicioIncidentes(db_manager)
            
            navbar_singleton.set_title("Reportar Incidente")
            
            def on_navigate_wrapper(route, **kwargs):
                # Si volvemos al listado, refrescamos el caché para mostrar el nuevo incidente
                if route == "incidentes":
                    router.refrescar_vista("incidentes")
                router.navegar_a(route, **kwargs)
            
            vista = IncidenteFormView(page, servicio_incidentes, db_manager, on_navigate_wrapper)
            
            return vista
        
        def build_incidente_detalle(id_incidente):
            """Constructor de vista Detalle de Incidente."""
            from src.presentacion.views.incidente_detail_view import IncidenteDetailView
            from src.aplicacion.servicios.servicio_incidentes import ServicioIncidentes
            from src.aplicacion.servicios.servicio_proveedores import ServicioProveedores
            
            servicio_incidentes = ServicioIncidentes(db_manager)
            servicio_proveedores = ServicioProveedores(db_manager)
            
            # Callback para invalidar el caché del tablero kanban
            def refrescar_incidentes():
                router.refrescar_vista("incidentes")
            
            navbar_singleton.set_title(f"Detalle Incidente #{id_incidente}")
            
            vista = IncidenteDetailView(
                page, 
                servicio_incidentes, 
                servicio_proveedores, 
                id_incidente, 
                router.navegar_a,
                on_refrescar_incidentes=refrescar_incidentes
            )
            
            return vista
        
        def build_proveedores_list():
            """Constructor de vista Listado de Proveedores."""
            from src.presentacion.views.proveedores_list_view import ProveedoresListView
            from src.aplicacion.servicios.servicio_proveedores import ServicioProveedores
            
            servicio_proveedores = ServicioProveedores(db_manager)
            
            navbar_singleton.set_title("Gestión de Proveedores")
            
            vista = ProveedoresListView(page, servicio_proveedores, router.navegar_a)
            
            return vista
            
        def build_proveedor_form(id_proveedor=None):
            """Constructor de vista Formulario de Proveedor."""
            from src.presentacion.views.proveedor_form_view import ProveedorFormView
            from src.aplicacion.servicios.servicio_proveedores import ServicioProveedores
            from src.aplicacion.servicios.servicio_personas import ServicioPersonas
            
            servicio_proveedores = ServicioProveedores(db_manager)
            servicio_personas = ServicioPersonas(db_manager)
            
            navbar_singleton.set_title("Registro de Proveedor")
            
            vista = ProveedorFormView(page, servicio_proveedores, servicio_personas, router.navegar_a, id_proveedor)
            
            return vista

        def build_seguros_list():
            """Constructor de vista Listado de Seguros."""
            
            def handle_nuevo_seguro():
                router.navegar_a("seguro_form")
            
            def handle_editar_seguro(id_seguro: int):
                router.navegar_a("seguro_form", seguro_id=id_seguro)
            
            def handle_nueva_poliza():
                router.navegar_a("poliza_form")
            
            navbar_singleton.set_title("Gestión de Seguros")
            
            vista = crear_seguros_list_view(
                page,
                handle_nuevo_seguro,
                handle_editar_seguro,
                on_nueva_poliza=handle_nueva_poliza
            )
            return vista
        
        def build_poliza_form():
            """Constructor de formulario de Nueva Póliza."""
            def handle_guardar():
                router.refrescar_vista("seguros")
                router.navegar_a("seguros")
            
            def handle_cancelar():
                router.navegar_a("seguros")
                
            navbar_singleton.set_title("Asignar Nueva Póliza")
            return crear_poliza_form_view(page, handle_guardar, handle_cancelar)
        
        def build_seguro_form(seguro_id=None):
            """Constructor de vista Formulario de Seguro."""
            
            def handle_guardar():
                # Invalidar caché de seguros
                router.refrescar_vista("seguros")
                router.navegar_a("seguros")
            
            def handle_cancelar():
                router.navegar_a("seguros")
            
            navbar_singleton.set_title("Formulario de Seguro")
            
            form = crear_seguro_form_view(page, handle_guardar, handle_cancelar, seguro_id)
            return form
        
        # --- Rutas de Recibos Públicos ---
        
        def build_recibos_publicos_list():
            """Constructor de vista Listado de Recibos Públicos."""
            
            def handle_nuevo_recibo():
                router.navegar_a("recibo_publico_form")
            
            def handle_editar_recibo(id_recibo: int):
                router.navegar_a("recibo_publico_form", recibo_id=id_recibo)
            
            def handle_marcar_pagado(id_recibo: int):
                """Muestra modal para marcar un recibo como pagado"""
                txt_fecha_pago = ft.Ref[ft.TextField]()
                txt_comprobante = ft.Ref[ft.TextField]()
                
                # DatePicker para fecha de pago
                date_picker_pago = ft.DatePicker(
                    first_date=datetime(2020, 1, 1),
                    last_date=datetime(2035, 12, 31),
                    on_change=lambda e: actualizar_fecha_pago(e.control.value),
                )
                
                page.overlay.append(date_picker_pago)
                
                def actualizar_fecha_pago(fecha):
                    if fecha:
                        txt_fecha_pago.current.value = fecha.strftime("%Y-%m-%d")
                        page.update()
                
                def abrir_picker_pago(e):
                    page.open(date_picker_pago)
                
                def confirmar_pago(e):
                    try:
                        if not txt_fecha_pago.current.value:
                            page.snack_bar = ft.SnackBar(content=ft.Text("La fecha de pago es obligatoria"), bgcolor="red")
                            page.snack_bar.open = True
                            page.update()
                            return
                        
                        if not txt_comprobante.current.value:
                            page.snack_bar = ft.SnackBar(content=ft.Text("El comprobante es obligatorio"), bgcolor="red")
                            page.snack_bar.open = True
                            page.update()
                            return
                        
                        servicio_recibos_publicos.marcar_como_pagado(
                            id_recibo,
                            txt_fecha_pago.current.value,
                            txt_comprobante.current.value,
                            usuario.nombre_usuario
                        )
                        
                        page.close(dlg_pago)
                        page.snack_bar = ft.SnackBar(content=ft.Text("Recibo marcado como pagado exitosamente"), bgcolor="green")
                        page.snack_bar.open = True
                        page.update()
                        
                        router.refrescar_vista("recibos_publicos")
                        router.navegar_a("recibos_publicos")
                        
                    except Exception as ex:
                        page.close(dlg_pago)
                        page.snack_bar = ft.SnackBar(content=ft.Text(f"Error: {str(ex)}"), bgcolor="red")
                        page.snack_bar.open = True
                        page.update()
                
                def cancelar_pago(e):
                    page.close(dlg_pago)
                
                dlg_pago = ft.AlertDialog(
                    modal=True,
                    title=ft.Text("Marcar Recibo como Pagado"),
                    content=ft.Column([
                        ft.TextField(
                            ref=txt_fecha_pago,
                            label="Fecha de Pago *",
                            hint_text="YYYY-MM-DD",
                            read_only=True,
                            suffix=ft.IconButton(
                                icon=ft.Icons.CALENDAR_MONTH,
                                icon_color="#4caf50",
                                tooltip="Seleccionar fecha",
                                on_click=abrir_picker_pago,
                            ),
                        ),
                        ft.TextField(
                            ref=txt_comprobante,
                            label="Comprobante *",
                            hint_text="Número de referencia o transacción",
                        ),
                    ], tight=True, width=400),
                    actions=[
                        ft.TextButton("Cancelar", on_click=cancelar_pago),
                        ft.TextButton("Marcar como Pagado", on_click=confirmar_pago),
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
                page.open(dlg_pago)
            
            def handle_eliminar_recibo(id_recibo: int):
                """Confirma y elimina un recibo"""
                def confirmar_eliminacion(e):
                    try:
                        servicio_recibos_publicos.eliminar_recibo(id_recibo)
                        page.close(dlg_eliminar)
                        page.snack_bar = ft.SnackBar(content=ft.Text("Recibo eliminado exitosamente"), bgcolor="green")
                        page.snack_bar.open = True
                        page.update()
                        
                        router.refrescar_vista("recibos_publicos")
                        router.navegar_a("recibos_publicos")
                        
                    except Exception as ex:
                        page.close(dlg_eliminar)
                        page.snack_bar = ft.SnackBar(content=ft.Text(f"Error: {str(ex)}"), bgcolor="red")
                        page.snack_bar.open = True
                        page.update()
                
                def cancelar_eliminacion(e):
                    page.close(dlg_eliminar)
                
                dlg_eliminar = ft.AlertDialog(
                    modal=True,
                    title=ft.Text("Confirmar Eliminación"),
                    content=ft.Text("¿Está seguro de eliminar este recibo?\\n\\nEsta acción no se puede deshacer."),
                    actions=[
                        ft.TextButton("Cancelar", on_click=cancelar_eliminacion),
                        ft.TextButton("Eliminar", on_click=confirmar_eliminacion, style=ft.ButtonStyle(color=ft.Colors.RED)),
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
                page.open(dlg_eliminar)

            def handle_ver_detalle_recibo(id_recibo: int):
                """Muestra el detalle completo de un recibo público"""
                try:
                    info = servicio_recibos_publicos.obtener_detalle_ui(id_recibo)
                    
                    if not info:
                        page.snack_bar = ft.SnackBar(ft.Text("No se pudo cargar la información del recibo"), bgcolor="red")
                        page.snack_bar.open = True
                        page.update()
                        return
                    
                    # Construir filas de información
                    filas = [
                        ("Servicio", f"{info['tipo_servicio']}"),
                        ("Propiedad", f"{info['direccion_propiedad']} (ID: {info['id_propiedad']})"),
                        ("Período", info['periodo']),
                        ("Valor", f"${info['valor']:,}"),
                        ("Vencimiento", info['fecha_vencimiento']),
                        ("Estado", info['estado']),
                    ]
                    
                    if info['esta_pagado']:
                        filas.append(("Fecha Pago", info['fecha_pago']))
                        filas.append(("Comprobante", info['comprobante']))
                    
                    content_rows = []
                    for k, v in filas:
                        content_rows.append(
                            ft.Row([
                                ft.Text(k, weight=ft.FontWeight.BOLD, width=120, size=13),
                                ft.Text(str(v), size=13, expand=True, selectable=True)
                            ], alignment=ft.MainAxisAlignment.START)
                        )
                    
                    # Auditoría
                    content_rows.append(ft.Divider(height=10, color="#e0e0e0"))
                    content_rows.append(ft.Text("Auditoría:", weight=ft.FontWeight.BOLD, size=12, color="#666"))
                    content_rows.append(ft.Text(f"Registrado por: {info['created_by']} el {info['created_at']}", size=11, color="#666"))
                    
                    content = ft.Column(
                        controls=content_rows,
                        tight=True,
                        width=500,
                        scroll=ft.ScrollMode.AUTO
                    )
                    
                    def close_dlg(e):
                        page.close(dlg)
                    
                    dlg = ft.AlertDialog(
                        modal=True,
                        title=ft.Text(f"Detalle Recibo #{id_recibo}", weight=ft.FontWeight.BOLD),
                        content=content,
                        actions=[
                            ft.TextButton("Cerrar", on_click=close_dlg)
                        ],
                        actions_alignment=ft.MainAxisAlignment.END,
                    )
                    
                    page.open(dlg)
                    
                except Exception as ex:
                    print(f"Error detalle recibo: {ex}")
                    page.snack_bar = ft.SnackBar(ft.Text(f"Error: {str(ex)}"), bgcolor="red")
                    page.snack_bar.open = True
                    page.update()
            
            navbar_singleton.set_title("Gestión de Recibos Públicos")
            
            vista = crear_recibos_publicos_list_view(
                page,
                servicio_recibos_publicos,
                servicio_propiedades,
                servicio_notificaciones,
                handle_nuevo_recibo,
                handle_editar_recibo,
                handle_marcar_pagado,
                handle_eliminar_recibo,
                on_ver_detalle=handle_ver_detalle_recibo
            )
            return vista
        
        def build_recibo_publico_form(recibo_id=None):
            """Constructor de vista Formulario de Recibo Público."""
            
            def handle_guardar():
                router.refrescar_vista("recibos_publicos")
                router.navegar_a("recibos_publicos")
            
            def handle_cancelar():
                router.navegar_a("recibos_publicos")
            
            navbar_singleton.set_title(f"{'Editar' if recibo_id else 'Nuevo'} Recibo Público")
            
            form = crear_recibo_publico_form_view(
                page,
                servicio_recibos_publicos,
                servicio_propiedades,
                handle_guardar,
                handle_cancelar,
                recibo_id,
                usuario.nombre_usuario
            )
            return form
        
        # --- Rutas de Liquidaciones de Asesores ---
        
        def build_liquidaciones_asesores_list():
            """Constructor de vista Listado de Liquidaciones de Asesores."""
            
            def handle_nueva_liquidacion():
                router.navegar_a("liquidacion_asesor_form")
            
            def handle_editar_liquidacion(id_liquidacion: int):
                router.navegar_a("liquidacion_asesor_form", liquidacion_id=id_liquidacion)
            
            def handle_ver_detalle(id_liquidacion: int):
                """Muestra el detalle de una liquidación en modal"""
                try:
                    def cerrar_modal():
                        page.close(modal)
                        page.update()
                        
                    modal = crear_modal_detalle_liquidacion(
                        page,
                        servicio_liquidacion_asesores,
                        servicio_notificaciones,
                        id_liquidacion,
                        cerrar_modal
                    )
                    page.open(modal)
                except Exception as e:
                    page.snack_bar = ft.SnackBar(content=ft.Text(f"Error: {str(e)}"), bgcolor="red")
                    page.snack_bar.open = True
                    page.update()
            
            def handle_aprobar(id_liquidacion: int):
                """Aprueba una liquidación"""
                try:
                    servicio_liquidacion_asesores.aprobar_liquidacion(id_liquidacion, usuario.nombre_usuario)
                    page.snack_bar = ft.SnackBar(content=ft.Text("Liquidación aprobada exitosamente"), bgcolor="green")
                    page.snack_bar.open = True
                    router.refrescar_vista("liquidaciones_asesores")
                    router.navegar_a("liquidaciones_asesores")
                except Exception as e:
                    page.snack_bar = ft.SnackBar(content=ft.Text(f"Error: {str(e)}"), bgcolor="red")
                    page.snack_bar.open = True
                    page.update()
            
            def handle_anular(id_liquidacion: int):
                """Anula una liquidación con confirmación"""
                txt_motivo = ft.Ref[ft.TextField]()
                
                def confirmar_anular(e):
                    try:
                        if not txt_motivo.current.value:
                            page.snack_bar = ft.SnackBar(content=ft.Text("El motivo es obligatorio"), bgcolor="red")
                            page.snack_bar.open = True
                            page.update()
                            return
                        
                        servicio_liquidacion_asesores.anular_liquidacion(
                            id_liquidacion,
                            txt_motivo.current.value,
                            usuario.nombre_usuario
                        )
                        page.close(dlg)
                        page.snack_bar = ft.SnackBar(content=ft.Text("Liquidación anulada"), bgcolor="orange")
                        page.snack_bar.open = True
                        router.refrescar_vista("liquidaciones_asesores")
                        router.navegar_a("liquidaciones_asesores")
                    except Exception as ex:
                        page.close(dlg)
                        page.snack_bar = ft.SnackBar(content=ft.Text(f"Error: {str(ex)}"), bgcolor="red")
                        page.snack_bar.open = True
                        page.update()
                
                dlg = ft.AlertDialog(
                    modal=True,
                    title=ft.Text("Anular Liquidación"),
                    content=ft.Column([
                        ft.Text("¿Está seguro de anular esta liquidación?"),
                        ft.TextField(ref=txt_motivo, label="Motivo de anulación *", multiline=True)
                    ], tight=True, width=400),
                    actions=[
                        ft.TextButton("Cancelar", on_click=lambda e: page.close(dlg)),
                        ft.TextButton("Anular", on_click=confirmar_anular),
                    ],
                )
                page.open(dlg)
            
            navbar_singleton.set_title("Liquidación de Asesores")
            
            vista = crear_liquidaciones_asesores_list_view(
                page,
                servicio_liquidacion_asesores,
                servicio_personas,
                handle_nueva_liquidacion,
                handle_editar_liquidacion,
                handle_ver_detalle,
                handle_aprobar,
                handle_anular
            )
            return vista
        
        def build_liquidacion_asesor_form(liquidacion_id=None):
            """Constructor de vista Formulario de Liquidación de Asesor."""
            
            def handle_guardar(datos: dict):
                """Guarda la liquidación con validaciones"""
                print("\n" + "="*80)
                print("[DEBUG LAYER 2: MAIN.PY] ===== HANDLE_GUARDAR LLAMADO =====")
                print(f"[DEBUG LAYER 2: MAIN.PY] Datos recibidos: {datos.keys()}")
                print(f"[DEBUG LAYER 2: MAIN.PY] liquidacion_id: {liquidacion_id}")
                print("="*80 + "\n")
                
                try:
                    if liquidacion_id:
                        print("[DEBUG LAYER 2: MAIN.PY] MODO: Edición")
                        # Edición: solo permite modificar porcentaje y observaciones
                        servicio_liquidacion_asesores.actualizar_liquidacion(
                            liquidacion_id,
                            {
                                'porcentaje_comision': datos['porcentaje_comision'],
                                'observaciones_liquidacion': datos.get('observaciones')
                            },
                            usuario.nombre_usuario
                        )
                        mensaje = "Liquidación actualizada exitosamente"
                        print(f"[DEBUG LAYER 2: MAIN.PY] ✓ Liquidación {liquidacion_id} actualizada")
                    else:
                        print("[DEBUG LAYER 2: MAIN.PY] MODO: Creación nueva (MULTI-CONTRATO)")
                        # Creación nueva - Convertir porcentaje a formato INTEGER
                        porcentaje_int = int(datos['porcentaje_comision'] * 100)
                        print(f"[DEBUG LAYER 2: MAIN.PY] Porcentaje convertido: {datos['porcentaje_comision']} -> {porcentaje_int}")
                        
                        # Generar liquidación multi-contrato
                        print("[DEBUG LAYER 2: MAIN.PY] Llamando servicio.generar_liquidacion_multi_contrato...")
                        print(f"[DEBUG LAYER 2: MAIN.PY] ID Asesor: {datos['id_asesor']}")
                        print(f"[DEBUG LAYER 2: MAIN.PY] Período: {datos['periodo']}")
                        print(f"[DEBUG LAYER 2: MAIN.PY] Contratos: {len(datos.get('contratos_lista', []))} contratos")
                        
                        liquidacion = servicio_liquidacion_asesores.generar_liquidacion_multi_contrato(
                            id_asesor=datos['id_asesor'],
                            periodo=datos['periodo'],
                            contratos_lista=datos.get('contratos_lista', []),  # Lista de {'id': x, 'canon': y}
                            porcentaje_comision=porcentaje_int,
                            datos_adicionales={'observaciones': datos.get('observaciones')},
                            usuario=usuario.nombre_usuario
                        )
                        print(f"[DEBUG LAYER 2: MAIN.PY] ✓ Liquidación multi-contrato creada, ID: {liquidacion.id_liquidacion_asesor}")
                        
                        # Agregar descuentos si hay
                        descuentos = datos.get('descuentos', [])
                        print(f"[DEBUG LAYER 2: MAIN.PY] Agregando {len(descuentos)} descuentos...")
                        for i, desc in enumerate(descuentos):
                            print(f"[DEBUG LAYER 2: MAIN.PY]   Descuento {i+1}: {desc['tipo']} - ${desc['valor']}")
                            servicio_liquidacion_asesores.agregar_descuento(
                                liquidacion.id_liquidacion_asesor,
                                desc['tipo'],
                                desc['descripcion'],
                                desc['valor'],
                                usuario.nombre_usuario
                            )
                        print(f"[DEBUG LAYER 2: MAIN.PY] ✓ {len(descuentos)} descuentos agregados")
                        
                        mensaje = "Liquidación multi-contrato creada exitosamente"
                    
                    print("[DEBUG LAYER 2: MAIN.PY] Configurando SnackBar...")
                    page.snack_bar = ft.SnackBar(content=ft.Text(mensaje), bgcolor="green")
                    page.snack_bar.open = True
                    print(f"[DEBUG LAYER 2: MAIN.PY] SnackBar configurado: {mensaje}")
                    
                    print("[DEBUG LAYER 2: MAIN.PY] Llamando page.update()...")
                    page.update()  # Render the SnackBar before navigating
                    print("[DEBUG LAYER 2: MAIN.PY] ✓ page.update() completado")
                    
                    print("[DEBUG LAYER 2: MAIN.PY] Refrescando vista...")
                    router.refrescar_vista("liquidaciones_asesores")
                    print("[DEBUG LAYER 2: MAIN.PY] ✓ Vista refrescada")
                    
                    print("[DEBUG LAYER 2: MAIN.PY] Navegando a liquidaciones_asesores...")
                    router.navegar_a("liquidaciones_asesores")
                    print("[DEBUG LAYER 2: MAIN.PY] ✓ Navegación completada")
                    print("[DEBUG LAYER 2: MAIN.PY] ===== HANDLE_GUARDAR COMPLETADO =====\n")
                    
                except Exception as e:
                    print("\n" + "!"*80)
                    print(f"[DEBUG LAYER 2: MAIN.PY] ❌ EXCEPCIÓN EN handle_guardar")
                    print(f"[DEBUG LAYER 2: MAIN.PY] Tipo: {type(e).__name__}")
                    print(f"[DEBUG LAYER 2: MAIN.PY] Mensaje: {str(e)}")
                    print("!"*80 + "\n")
                    
                    # Mostrar SnackBar para feedback inmediato
                    page.snack_bar = ft.SnackBar(content=ft.Text(f"Error: {str(e)}"), bgcolor="red")
                    page.snack_bar.open = True
                    page.update()
                    
                    import traceback
                    traceback.print_exc()
                    
                    # RE-LANZAR excepción para que el formulario la capture y muestre el Banner
                    raise
            
            def handle_cancelar():
                router.navegar_a("liquidaciones_asesores")
            
            navbar_singleton.set_title(f"{'Editar' if liquidacion_id else 'Nueva'} Liquidación de Asesor")
            
            form = crear_liquidacion_asesor_form_view(
                page,
                servicio_liquidacion_asesores,
                servicio_contratos,
                servicio_personas,
                handle_guardar,
                handle_cancelar,
                liquidacion_id
            )
            return form
        
        # --- Rutas de Pagos de Asesores ---
        
        def build_pagos_asesores_list():
            """Constructor de vista Gestión de Pagos de Asesores."""
            
            def handle_registrar_pago(id_liquidacion: int):
                """Muestra modal para registrar pago de una liquidación"""
                print("\n" + "="*80)
                print("[DEBUG PAGOS] ===== HANDLE_REGISTRAR_PAGO LLAMADO =====")
                print(f"[DEBUG PAGOS] id_liquidacion: {id_liquidacion}")
                print("="*80 + "\n")
                
                txt_referencia = ft.Ref[ft.TextField]()
                dd_metodo = ft.Ref[ft.Dropdown]()
                
                def confirmar_pago(e):
                    print("[DEBUG PAGOS] Confirmar pago - iniciando...")
                    try:
                        if not txt_referencia.current.value:
                            print("[DEBUG PAGOS] ERROR: Referencia vacía")
                            page.snack_bar = ft.SnackBar(content=ft.Text("La referencia es obligatoria"), bgcolor="red")
                            page.snack_bar.open = True
                            page.update()
                            return
                        
                        print(f"[DEBUG PAGOS] Obteniendo liquidación {id_liquidacion}...")
                        # Obtener la liquidación para extraer los datos necesarios
                        detalle = servicio_liquidacion_asesores.obtener_detalle_completo(id_liquidacion)
                        liquidacion_data = detalle['liquidacion']  # Acceder a la liquidación dentro del detalle
                        
                        print(f"[DEBUG PAGOS] Liquidación obtenida: Asesor={liquidacion_data['id_asesor']}, Valor={liquidacion_data['valor_neto_asesor']}")
                        
                        # Fecha programada = hoy
                        from datetime import datetime
                        fecha_hoy = datetime.now().strftime('%Y-%m-%d')
                        medio_pago = dd_metodo.current.value or "Transferencia"
                        
                        print(f"[DEBUG PAGOS] Programando pago...")
                        print(f"[DEBUG PAGOS]   - id_liquidacion: {id_liquidacion}")
                        print(f"[DEBUG PAGOS]   - id_asesor: {liquidacion_data['id_asesor']}")
                        print(f"[DEBUG PAGOS]   - valor: {liquidacion_data['valor_neto_asesor']}")
                        print(f"[DEBUG PAGOS]   - fecha_programada: {fecha_hoy}")
                        print(f"[DEBUG PAGOS]   - medio_pago: {medio_pago}")
                        
                        # Programar pago con TODOS los parámetros requeridos
                        pago = servicio_liquidacion_asesores.programar_pago(
                            id_liquidacion=id_liquidacion,
                            id_asesor=liquidacion_data['id_asesor'],
                            valor=liquidacion_data['valor_neto_asesor'],
                            fecha_programada=fecha_hoy,
                            medio_pago=medio_pago,
                            datos_adicionales={
                                'referencia': txt_referencia.current.value,
                                'observaciones': f"Pago registrado vía sistema"
                            },
                            usuario=usuario.nombre_usuario
                        )
                        print(f"[DEBUG PAGOS] Pago programado, ID: {pago.id_pago_asesor}")
                        
                        # Registrar como pagado
                        print(f"[DEBUG PAGOS] Registrando pago {pago.id_pago_asesor} como pagado...")
                        servicio_liquidacion_asesores.registrar_pago(
                            pago.id_pago_asesor,
                            medio_pago,
                            txt_referencia.current.value,
                            usuario.nombre_usuario
                        )
                        print("[DEBUG PAGOS] Pago registrado exitosamente")
                        
                        page.close(dlg_pago)
                        page.snack_bar = ft.SnackBar(content=ft.Text("Pago registrado exitosamente"), bgcolor="green")
                        page.snack_bar.open = True
                        page.update()  # Actualizar antes de navegar
                        router.refrescar_vista("pagos_asesores")
                        router.refrescar_vista("liquidaciones_asesores")
                        router.navegar_a("pagos_asesores")
                    except Exception as ex:
                        print("\n" + "!"*80)
                        print(f"[DEBUG PAGOS] ❌ EXCEPCIÓN en confirmar_pago")
                        print(f"[DEBUG PAGOS] Tipo: {type(ex).__name__}")
                        print(f"[DEBUG PAGOS] Mensaje: {str(ex)}")
                        print("!"*80 + "\n")
                        
                        page.close(dlg_pago)
                        page.snack_bar = ft.SnackBar(content=ft.Text(f"Error: {str(ex)}"), bgcolor="red")
                        page.snack_bar.open = True
                        page.update()
                        
                        import traceback
                        traceback.print_exc()
                
                print("[DEBUG PAGOS] Creando diálogo de pago...")
                dlg_pago = ft.AlertDialog(
                    modal=True,
                    title=ft.Text("Registrar Pago"),
                    content=ft.Column([
                        ft.Text("Complete los datos del pago:"),
                        ft.Dropdown(
                            ref=dd_metodo,
                            label="Método de Pago",
                            value="Transferencia",
                            options=[
                                ft.dropdown.Option("Transferencia"),
                                ft.dropdown.Option("Cheque"),
                                ft.dropdown.Option("Efectivo"),
                                ft.dropdown.Option("Consignación"),
                            ]
                        ),
                        ft.TextField(
                            ref=txt_referencia,
                            label="Referencia/Comprobante *",
                            hint_text="Número de transacción"
                        ),
                    ], tight=True, width=400),
                    actions=[
                        ft.TextButton("Cancelar", on_click=lambda e: page.close(dlg_pago)),
                        ft.ElevatedButton("Registrar Pago", on_click=confirmar_pago, bgcolor="#4caf50", color="white"),
                    ],
                )
                print("[DEBUG PAGOS] Abriendo diálogo...")
                page.open(dlg_pago)
                print("[DEBUG PAGOS] Diálogo abierto exitosamente")
                print("[DEBUG PAGOS] ===== HANDLE_REGISTRAR_PAGO COMPLETADO =====\n")
            
            def handle_rechazar_pago(id_liquidacion: int):
                """Rechaza/anula una liquidación"""
                txt_motivo = ft.Ref[ft.TextField]()
                
                def confirmar_rechazo(e):
                    try:
                        if not txt_motivo.current.value:
                            page.snack_bar = ft.SnackBar(content=ft.Text("El motivo es obligatorio"), bgcolor="red")
                            page.snack_bar.open = True
                            page.update()
                            return
                        
                        servicio_liquidacion_asesores.anular_liquidacion(
                            id_liquidacion,
                            txt_motivo.current.value,
                            usuario.nombre_usuario
                        )
                        
                        page.close(dlg_rechazo)
                        page.snack_bar = ft.SnackBar(content=ft.Text("Liquidación rechazada"), bgcolor="orange")
                        page.snack_bar.open = True
                        router.refrescar_vista("pagos_asesores")
                        router.refrescar_vista("liquidaciones_asesores")
                        router.navegar_a("pagos_asesores")
                    except Exception as ex:
                        page.close(dlg_rechazo)
                        page.snack_bar = ft.SnackBar(content=ft.Text(f"Error: {str(ex)}"), bgcolor="red")
                        page.snack_bar.open = True
                        page.update()
                
                dlg_rechazo = ft.AlertDialog(
                    modal=True,
                    title=ft.Text("Rechazar Pago"),
                    content=ft.Column([
                        ft.Text("¿Está seguro de rechazar esta liquidación?"),
                        ft.TextField(ref=txt_motivo, label="Motivo *", multiline=True),
                    ], tight=True, width=400),
                    actions=[
                        ft.TextButton("Cancelar", on_click=lambda e: page.close(dlg_rechazo)),
                        ft.TextButton("Rechazar", on_click=confirmar_rechazo, style=ft.ButtonStyle(color="red")),
                    ],
                )
                page.open(dlg_rechazo)
            
            def handle_anular_pago(id_pago: int):
                """Anula un pago específico"""
                page.snack_bar = ft.SnackBar(content=ft.Text("Funcionalidad de anular pago individual pendiente"), bgcolor="orange")
                page.snack_bar.open = True
                page.update()
            
            def handle_ver_liquidacion(id_liquidacion: int):
                """Muestra el detalle de la liquidación"""
                try:
                    def cerrar_modal():
                        page.close(modal)
                        page.update()
                    
                    modal = crear_modal_detalle_liquidacion(
                        page,
                        servicio_liquidacion_asesores,
                        servicio_notificaciones,  # FIX: Added missing parameter
                        id_liquidacion,
                        cerrar_modal
                    )
                    page.open(modal)
                except Exception as ex:
                    page.snack_bar = ft.SnackBar(content=ft.Text(f"Error: {str(ex)}"), bgcolor="red")
                    page.snack_bar.open = True
                    page.update()
            
            navbar_singleton.set_title("Gestión de Pagos")
            
            vista = crear_pagos_asesores_list_view(
                page,
                servicio_liquidacion_asesores,
                servicio_personas,
                handle_registrar_pago,
                handle_rechazar_pago,
                handle_anular_pago,
                handle_ver_liquidacion
            )
            return vista
        
        # --- Rutas de Saldos a Favor ---
        
        def build_saldos_favor_list():
            """Constructor de vista Listado de Saldos a Favor."""
            
            # Obtener datos de propietarios y asesores para mostrar nombres
            propietarios_data = []
            asesores_data = []
            
            try:
                with db_manager.obtener_conexion() as conn:
                    cursor = conn.cursor()
                    # Propietarios
                    cursor.execute("""
                        SELECT pr.ID_PROPIETARIO, p.NOMBRE_COMPLETO
                        FROM PROPIETARIOS pr
                        JOIN PERSONAS p ON pr.ID_PERSONA = p.ID_PERSONA
                        WHERE pr.ESTADO_PROPIETARIO = 1
                    """)
                    for row in cursor.fetchall():
                        propietarios_data.append({'id_propietario': row[0], 'nombre': row[1]})
                    
                    # Asesores
                    cursor.execute("""
                        SELECT a.ID_ASESOR, p.NOMBRE_COMPLETO
                        FROM ASESORES a
                        JOIN PERSONAS p ON a.ID_PERSONA = p.ID_PERSONA
                        WHERE a.ESTADO = 1
                    """)
                    for row in cursor.fetchall():
                        asesores_data.append({'id_asesor': row[0], 'nombre': row[1]})
            except Exception as e:
                print(f"Error cargando beneficiarios: {e}")
            
            def handle_nuevo():
                router.navegar_a("saldo_favor_form")
            
            def handle_aplicar(id_saldo: int):
                try:
                    servicio_saldos_favor.aplicar_saldo(id_saldo, "Aplicado desde UI", usuario.nombre_usuario)
                    page.snack_bar = ft.SnackBar(content=ft.Text("Saldo aplicado exitosamente"), bgcolor="green")
                    page.snack_bar.open = True
                    router.refrescar_vista("saldos_favor")
                    router.navegar_a("saldos_favor")
                except Exception as e:
                    page.snack_bar = ft.SnackBar(content=ft.Text(f"Error: {str(e)}"), bgcolor="red")
                    page.snack_bar.open = True
                    page.update()
            
            def handle_devolver(id_saldo: int):
                try:
                    servicio_saldos_favor.devolver_saldo(id_saldo, "Devuelto desde UI", usuario.nombre_usuario)
                    page.snack_bar = ft.SnackBar(content=ft.Text("Saldo devuelto exitosamente"), bgcolor="green")
                    page.snack_bar.open = True
                    router.refrescar_vista("saldos_favor")
                    router.navegar_a("saldos_favor")
                except Exception as e:
                    page.snack_bar = ft.SnackBar(content=ft.Text(f"Error: {str(e)}"), bgcolor="red")
                    page.snack_bar.open = True
                    page.update()
            
            def handle_eliminar(id_saldo: int):
                def confirmar(e):
                    try:
                        servicio_saldos_favor.eliminar_saldo(id_saldo, usuario.nombre_usuario)
                        page.close(dlg)
                        page.snack_bar = ft.SnackBar(content=ft.Text("Saldo eliminado"), bgcolor="green")
                        page.snack_bar.open = True
                        router.refrescar_vista("saldos_favor")
                        router.navegar_a("saldos_favor")
                    except Exception as ex:
                        page.close(dlg)
                        page.snack_bar = ft.SnackBar(content=ft.Text(f"Error: {str(ex)}"), bgcolor="red")
                        page.snack_bar.open = True
                        page.update()
                
                dlg = ft.AlertDialog(
                    modal=True,
                    title=ft.Text("Confirmar Eliminación"),
                    content=ft.Text("¿Está seguro de eliminar este saldo a favor?"),
                    actions=[
                        ft.TextButton("Cancelar", on_click=lambda e: page.close(dlg)),
                        ft.TextButton("Eliminar", on_click=confirmar, style=ft.ButtonStyle(color="red")),
                    ],
                )
                page.open(dlg)
            
            navbar_singleton.set_title("Gestión de Saldos a Favor")
            
            vista = build_saldos_favor_list_view(
                page,
                servicio_saldos_favor,
                handle_nuevo,
                handle_aplicar,
                handle_devolver,
                handle_eliminar,
                propietarios_data,
                asesores_data
            )
            return vista
        
        def build_saldo_favor_form(saldo_id=None):
            """Constructor de vista Formulario de Saldo a Favor."""
            
            # Obtener datos de propietarios y asesores
            propietarios = []
            asesores = []
            
            try:
                with db_manager.obtener_conexion() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT pr.ID_PROPIETARIO, p.NOMBRE_COMPLETO
                        FROM PROPIETARIOS pr
                        JOIN PERSONAS p ON pr.ID_PERSONA = p.ID_PERSONA
                        WHERE pr.ESTADO_PROPIETARIO = 1
                    """)
                    for row in cursor.fetchall():
                        propietarios.append({'id_propietario': row[0], 'nombre': row[1]})
                    
                    cursor.execute("""
                        SELECT a.ID_ASESOR, p.NOMBRE_COMPLETO
                        FROM ASESORES a
                        JOIN PERSONAS p ON a.ID_PERSONA = p.ID_PERSONA
                        WHERE a.ESTADO = 1
                    """)
                    for row in cursor.fetchall():
                        asesores.append({'id_asesor': row[0], 'nombre': row[1]})
            except Exception as e:
                print(f"Error cargando beneficiarios: {e}")
            
            saldo_actual = None
            if saldo_id:
                saldo_actual = servicio_saldos_favor.obtener_saldo(saldo_id)
            
            def handle_guardar(datos):
                try:
                    if 'id_saldo_favor' in datos:
                        # Edición no implementada, solo crear nuevos
                        pass
                    else:
                        servicio_saldos_favor.registrar_saldo(
                            tipo_beneficiario=datos['tipo_beneficiario'],
                            id_beneficiario=datos['id_beneficiario'],
                            valor=datos['valor'],
                            motivo=datos['motivo'],
                            observaciones=datos.get('observaciones'),
                            usuario=usuario.nombre_usuario
                        )
                    
                    page.snack_bar = ft.SnackBar(content=ft.Text("Saldo guardado exitosamente"), bgcolor="green")
                    page.snack_bar.open = True
                    router.refrescar_vista("saldos_favor")
                    router.navegar_a("saldos_favor")
                except Exception as e:
                    page.snack_bar = ft.SnackBar(content=ft.Text(f"Error: {str(e)}"), bgcolor="red")
                    page.snack_bar.open = True
                    page.update()
            
            def handle_cancelar():
                router.navegar_a("saldos_favor")
            
            navbar_singleton.set_title("Nuevo Saldo a Favor")
            
            form = build_saldo_favor_form_view(
                page,
                handle_guardar,
                handle_cancelar,
                propietarios,
                asesores,
                saldo_actual
            )
            return form
        
        # Registrar rutas
        router.registrar_vista("dashboard", build_dashboard)
        router.registrar_vista("personas", build_personas_list)
        router.registrar_vista("persona_form", build_persona_form)
        router.registrar_vista("propiedades", build_propiedades_list)
        router.registrar_vista("propiedad_form", build_propiedad_form)
        router.registrar_vista("contratos", build_contratos_list)
        router.registrar_vista("contrato_mandato", build_contrato_mandato)
        router.registrar_vista("contrato_arrendamiento", build_contrato_arrendamiento)
        router.registrar_vista("recaudos", build_recaudos_list)
        router.registrar_vista("recaudo_form", build_recaudo_form)
        router.registrar_vista("liquidaciones", build_liquidaciones_list)
        router.registrar_vista("liquidacion_form", build_liquidacion_form)
        router.registrar_vista("incidentes", build_incidentes_list)
        router.registrar_vista("incidente_reportar", build_incidente_reportar)
        router.registrar_vista("incidente_detalle", build_incidente_detalle)
        router.registrar_vista("proveedores", build_proveedores_list)
        router.registrar_vista("proveedor_form", build_proveedor_form)
        router.registrar_vista("seguros", build_seguros_list)
        router.registrar_vista("seguro_form", build_seguro_form)
        router.registrar_vista("poliza_form", build_poliza_form)
        router.registrar_vista("recibos_publicos", build_recibos_publicos_list)
        router.registrar_vista("recibo_publico_form", build_recibo_publico_form)
        router.registrar_vista("liquidaciones_asesores", build_liquidaciones_asesores_list)
        router.registrar_vista("liquidacion_asesor_form", build_liquidacion_asesor_form)
        router.registrar_vista("pagos_asesores", build_pagos_asesores_list)
        router.registrar_vista("saldos_favor", build_saldos_favor_list)
        router.registrar_vista("saldo_favor_form", build_saldo_favor_form)
        
        # --- Rutas de Configuración del Sistema ---
        
        def build_configuracion():
            """Constructor de vista Configuración del Sistema."""
            if usuario.rol != "Administrador":
                # Redirigir si no es administrador
                page.snack_bar = ft.SnackBar(ft.Text("Acceso denegado: Solo administradores"), bgcolor=ft.Colors.RED)
                page.snack_bar.open = True
                page.update()
                router.navegar_a("dashboard")
                return ft.Container()
            
            def handle_nuevo_usuario():
                router.navegar_a("usuario_form")
            
            def handle_editar_usuario(id_usuario: int):
                router.navegar_a("usuario_form", usuario_id=id_usuario)
            
            navbar_singleton.set_title("Configuración del Sistema")
            
            vista = build_configuracion_view(
                page,
                servicio_configuracion,
                usuario,
                handle_nuevo_usuario,
                handle_editar_usuario,
            )
            return vista
        
        def build_usuario_form(usuario_id=None):
            """Constructor de vista Formulario de Usuario."""
            if usuario.rol != "Administrador":
                router.navegar_a("dashboard")
                return ft.Container()
            
            usuario_editar = None
            if usuario_id:
                usuario_editar = servicio_configuracion.obtener_usuario(usuario_id)
            
            def handle_guardar():
                router.refrescar_vista("configuracion")
                router.navegar_a("configuracion")
            
            def handle_cancelar():
                router.navegar_a("configuracion")
            
            navbar_singleton.set_title("Nuevo Usuario" if not usuario_editar else "Editar Usuario")
            
            form = build_usuario_form_view(
                page,
                servicio_configuracion,
                usuario,
                handle_guardar,
                handle_cancelar,
                usuario_editar,
            )
            return form
        
        def build_incrementos():
            """Constructor de vista Incrementos IPC."""
            navbar_singleton.set_title("Incrementos de Canon (IPC)")
            return build_incrementos_view(page, servicio_contratos, usuario)


        def build_desocupaciones_list():
            """Constructor de vista Lista de Desocupaciones."""
            navbar_singleton.set_title("Gestión de Desocupaciones")
            
            def handle_nueva():
                router.navegar_a("desocupacion_form")
            
            def handle_ver_checklist(id_desocupacion):
                router.navegar_a("desocupacion_checklist", id_desocupacion=id_desocupacion)
            
            return crear_desocupaciones_list_view(
                page,
                servicio_desocupaciones,
                servicio_documental,
                handle_nueva,
                handle_ver_checklist
            )
        
        def build_desocupacion_form():
            """Constructor de vista Formulario de Desocupación."""
            navbar_singleton.set_title("Nueva Desocupación")
            
            def handle_guardar():
                router.navegar_a("desocupaciones")
            
            def handle_cancelar():
                router.navegar_a("desocupaciones")
            
            return crear_desocupacion_form_view(
                page,
                servicio_desocupaciones,
                handle_guardar,
                handle_cancelar
            )
        
        def build_desocupacion_checklist(id_desocupacion=None):
            """Constructor de vista Checklist de Desocupación."""
            navbar_singleton.set_title("Checklist de Desocupación")
            
            if not id_desocupacion:
                router.navegar_a("desocupaciones")
                return ft.Container()
            
            def handle_volver():
                router.navegar_a("desocupaciones")
            
            return crear_desocupacion_checklist_view(
                page,
                servicio_desocupaciones,
                id_desocupacion,
                handle_volver
            )

        router.registrar_vista("configuracion", build_configuracion)
        router.registrar_vista("usuario_form", build_usuario_form)
        router.registrar_vista("incrementos", build_incrementos)
        router.registrar_vista("desocupaciones", build_desocupaciones_list)
        router.registrar_vista("desocupacion_form", build_desocupacion_form)
        router.registrar_vista("desocupacion_checklist", build_desocupacion_checklist)
        
        # Pre-cargar vistas principales con loading page
        print("DEBUG: Llamando mostrar_loading_y_precargar...")
        mostrar_loading_y_precargar(page, router, usuario)
    
    def mostrar_loading_y_precargar(page: ft.Page, router, usuario):
        """
        Muestra la loading page y pre-construye las vistas principales.
        
        Args:
            page: Página de Flet
            router: Instancia del Router
            usuario: Usuario autenticado
        """
        import time
        print("DEBUG: Dentro de mostrar_loading_y_precargar")
        from src.presentacion.views.loading_view import crear_loading_view
        
        # 1. Crear y mostrar loading view
        loading_view = crear_loading_view(page)
        page.clean()
        page.add(loading_view)
        page.update()
        
        # 2. Lista de vistas a pre-cargar (solo vistas principales sin parámetros)
        vistas_principales = [
            ("dashboard", "Dashboard"),
            ("personas", "Gestión de Personas"),
            ("propiedades", "Gestión de Propiedades"),
            ("contratos", "Gestión de Contratos"),
            ("recaudos", "Recaudos"),
            ("liquidaciones", "Liquidaciones"),
            ("incidentes", "Gestión de Incidentes"),
            ("proveedores", "Gestión de Proveedores"),
            ("seguros", "Gestión de Seguros"),
        ]
        
        # 3. Pre-construir cada vista con feedback visual
        total = len(vistas_principales)
        for i, (nombre_vista, titulo) in enumerate(vistas_principales):
            # Actualizar loading page ANTES de construir
            progreso = int(((i) / total) * 100)
            loading_view.actualizar_progreso(progreso, f"Cargando {titulo}...")
            page.update()
            
            # Pre-construir vista
            try:
                router.pre_construir_vista(nombre_vista)
            except Exception as e:
                print(f"⚠️ Error pre-construyendo {nombre_vista}: {e}")
            
            # Pausa mínima solo para feedback visual (reducida a 50ms)
            time.sleep(0.05)
        
        # 4. Completar loading
        loading_view.actualizar_progreso(100, "¡Sistema listo!")
        page.update()
        time.sleep(0.3)  # Reducido de 0.5s a 0.3s
        
        # 5. Navegar al dashboard (ya pre-construido)
        try:
            # Restaurar Shell antes de navegar, para que el Router actualice un Shell visible
            page.clean()
            if hasattr(router, 'shell') and router.shell:
                 page.add(router.shell)
                 page.update() # IMPORTANTE: Renderizar Shell para que el cliente conozca los controles antes de actualizar el contenido
            
            # Navegar (esto actualizará el contenido del Shell de forma segura)
            router.navegar_a("dashboard")
        except Exception as e:
            print(f"Error cargando dashboard: {e}")
            import traceback
            traceback.print_exc()
            page.clean()
            page.add(ft.Text(f"Error cargando dashboard: {e}", color=ft.Colors.RED))
            page.update()


    # Cargar vista de login
    login_view = crear_login_view(page, on_login_success)
    page.add(login_view)


if __name__ == "__main__":
    # Ejecutar en modo web por defecto
    # Para modo escritorio, usar: ft.app(target=main)
    ft.app(
        target=main,
        view=ft.AppView.WEB_BROWSER,
        port=8080,
        upload_dir="uploads"
    )
