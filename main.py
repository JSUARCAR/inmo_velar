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
        
        # Importar componentes necesarios
        from src.presentacion.router import Router
        from src.presentacion.components.sidebar import Sidebar
        from src.presentacion.components.navbar import Navbar
        from src.presentacion.components.shell import Shell
        from src.presentacion.views.alerts_view import AlertsView
        
        from src.aplicacion.servicios.servicio_contratos import ServicioContratos
        from src.aplicacion.servicios.servicio_financiero import ServicioFinanciero
        from src.aplicacion.servicios.servicio_propiedades import ServicioPropiedades
        from src.aplicacion.servicios.servicio_recibos_publicos import ServicioRecibosPublicos
        from src.aplicacion.servicios.servicio_alertas import ServicioAlertas
        from src.infraestructura.repositorios.repositorio_recibo_publico_sqlite import RepositorioReciboPublicoSQLite
        from src.infraestructura.persistencia.repositorio_propiedad_sqlite import RepositorioPropiedadSQLite
        from src.aplicacion.servicios.servicio_dashboard import ServicioDashboard
        
        # Inicializar Servicios
        print("DEBUG: Inicializando Servicios...")
        # Instanciar Repositorios Core (Inyectados en servicios)
        repo_propiedad = RepositorioPropiedadSQLite(db_manager)
        repo_contrato_mandato = RepositorioContratoMandatoSQLite(db_manager)
        repo_contrato_arriendo = RepositorioContratoArrendamientoSQLite(db_manager)
        repo_recaudo = RepositorioRecaudoSQLite(db_manager)
        repo_liquidacion = RepositorioLiquidacionSQLite(db_manager)
        pdf_service = ServicioDocumentosPDF()

        from src.infraestructura.persistencia.repositorio_renovacion_sqlite import RepositorioRenovacionSQLite
        from src.infraestructura.persistencia.repositorio_ipc_sqlite import RepositorioIPCSQLite
        from src.infraestructura.persistencia.repositorio_arrendatario_sqlite import RepositorioArrendatarioSQLite
        from src.infraestructura.persistencia.repositorio_codeudor_sqlite import RepositorioCodeudorSQLite

        repo_renovacion = RepositorioRenovacionSQLite(db_manager)
        repo_ipc = RepositorioIPCSQLite(db_manager)
        repo_arrendatario = RepositorioArrendatarioSQLite(db_manager)
        repo_codeudor = RepositorioCodeudorSQLite(db_manager)

        servicio_contratos = ServicioContratos(
            db_manager,
            repo_mandato=repo_contrato_mandato,
            repo_arriendo=repo_contrato_arriendo,
            repo_propiedad=repo_propiedad,
            repo_renovacion=repo_renovacion,
            repo_ipc=repo_ipc,
            repo_arrendatario=repo_arrendatario,
            repo_codeudor=repo_codeudor
        )
        
        # Inyectar dependencias en ServicioFinanciero
        servicio_financiero = ServicioFinanciero(
            repo_recaudo=repo_recaudo,
            repo_liquidacion=repo_liquidacion,
            repo_propiedad=repo_propiedad,
            repo_arriendo=repo_contrato_arriendo,
            repo_mandato=repo_contrato_mandato,
            pdf_service=pdf_service
        )

        servicio_propiedades = ServicioPropiedades(repo_propiedad=repo_propiedad)
        
        from src.infraestructura.persistencia.repositorio_dashboard_sqlite import RepositorioDashboardSQLite
        repo_dashboard = RepositorioDashboardSQLite(db_manager)
        servicio_dashboard = ServicioDashboard(repo_dashboard=repo_dashboard)
        
        # Inicializar repositorios y servicio de recibos públicos
        repo_recibo_publico = RepositorioReciboPublicoSQLite(db_manager)
        servicio_recibos_publicos = ServicioRecibosPublicos(repo_recibo_publico, repo_propiedad)
        
        # Inicializar repositorios para ServicioPersonas
        from src.infraestructura.repositorios import (
            RepositorioLiquidacionAsesorSQLite,
            RepositorioDescuentoAsesorSQLite,
            RepositorioPagoAsesorSQLite
        )
        from src.infraestructura.persistencia.repositorio_asesor_sqlite import RepositorioAsesorSQLite
        from src.infraestructura.persistencia.repositorio_persona_sqlite import RepositorioPersonaSQLite
        from src.infraestructura.persistencia.repositorio_propietario_sqlite import RepositorioPropietarioSQLite
        from src.infraestructura.persistencia.repositorio_proveedores_sqlite import RepositorioProveedoresSQLite
        from src.aplicacion.servicios.servicio_liquidacion_asesores import ServicioLiquidacionAsesores
        from src.aplicacion.servicios.servicio_personas import ServicioPersonas
        from src.aplicacion.servicios.servicio_saldos_favor import ServicioSaldosFavor
        from src.aplicacion.servicios.servicio_notificaciones import ServicioNotificaciones
        
        repo_persona = RepositorioPersonaSQLite(db_manager)
        repo_asesor = RepositorioAsesorSQLite(db_manager)
        repo_propietario = RepositorioPropietarioSQLite(db_manager)
        # Usar los ya instanciados arriba
        # repo_arrendatario y repo_codeudor ya existen
        repo_proveedor = RepositorioProveedoresSQLite(db_manager)

        repo_liquidacion_asesor = RepositorioLiquidacionAsesorSQLite(db_manager)
        repo_descuento_asesor = RepositorioDescuentoAsesorSQLite(db_manager)
        repo_pago_asesor = RepositorioPagoAsesorSQLite(db_manager)
        
        servicio_liquidacion_asesores = ServicioLiquidacionAsesores(
            repo_liquidacion_asesor, repo_descuento_asesor, repo_pago_asesor,
            repo_contrato_arriendo, repo_propiedad, pdf_service,
            repo_asesor, repo_persona
        )
        
        servicio_personas = ServicioPersonas(
            repo_persona=repo_persona,
            repo_asesor=repo_asesor,
            repo_propietario=repo_propietario,
            repo_arrendatario=repo_arrendatario,
            repo_codeudor=repo_codeudor,
            repo_proveedor=repo_proveedor
        )
        servicio_saldos_favor = ServicioSaldosFavor(db_manager)
        servicio_notificaciones = ServicioNotificaciones()
        
        from src.aplicacion.servicios.servicio_documental import ServicioDocumental
        from src.infraestructura.repositorios.repositorio_documento_sqlite import RepositorioDocumentoSQLite
        repo_documento = RepositorioDocumentoSQLite(db_manager)
        servicio_documental = ServicioDocumental(repo_documento)

        from src.aplicacion.servicios.servicio_desocupaciones import ServicioDesocupaciones
        servicio_desocupaciones = ServicioDesocupaciones(db_manager)
        
        servicio_alertas = ServicioAlertas()
        
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
        
        # --- Arquitectura Shell ---
        navbar_singleton = Navbar("Dashboard", abrir_alertas)
        router_temp = Router(page, usuario, shell=None)
        sidebar_singleton = Sidebar(usuario, router_temp.navegar_a, on_logout)
        shell = Shell(sidebar=sidebar_singleton, navbar=navbar_singleton)
        router_temp.shell = shell
        router = router_temp
        
        page.clean()
        page.add(shell)
        page.update()
        
        # --- Registrar Vistas vía NavigationHub ---
        from src.presentacion.navigation_hub import NavigationHub
        
        servicios = {
            "contratos": servicio_contratos,
            "financiero": servicio_financiero,
            "propiedades": servicio_propiedades,
            "dashboard": servicio_dashboard,
            "recibos_publicos": servicio_recibos_publicos,
            "liquidacion_asesores": servicio_liquidacion_asesores,
            "personas": servicio_personas,
            "saldos_favor": servicio_saldos_favor,
            "notificaciones": servicio_notificaciones,
            "documental": servicio_documental,
            "desocupaciones": servicio_desocupaciones,
            "alertas": servicio_alertas,
            "configuracion": servicio_configuracion,
            "db_manager": db_manager
        }
        
        hub = NavigationHub(page, usuario, router, navbar_singleton, servicios, on_logout)
        hub.registrar_vistas()
        
        # Pre-cargar vistas principales
        mostrar_loading_y_precargar(page, router, usuario)
    
    def mostrar_loading_y_precargar(page: ft.Page, router, usuario):
        import time
        from src.presentacion.views.loading_view import crear_loading_view
        
        loading_view = crear_loading_view(page)
        page.clean()
        page.add(loading_view)
        page.update()
        
        vistas_principales = [
            ("dashboard", "Dashboard"),
            ("personas", "Gestión de Personas"),
            ("propiedades", "Gestión de Propiedades"),
            ("contratos", "Gestión de Contratos"),
            ("recaudos", "Recaudos"),
            ("liquidaciones", "Liquidaciones"),
        ]
        
        total = len(vistas_principales)
        for i, (nombre_vista, titulo) in enumerate(vistas_principales):
            progreso = int(((i) / total) * 100)
            loading_view.actualizar_progreso(progreso, f"Cargando {titulo}...")
            page.update()
            
            try:
                router.pre_construir_vista(nombre_vista)
            except Exception as e:
                print(f"⚠️ Error pre-construyendo {nombre_vista}: {e}")
            
            time.sleep(0.05)
        
        loading_view.actualizar_progreso(100, "¡Sistema listo!")
        page.update()
        time.sleep(0.3)
        
        page.clean()
        if hasattr(router, 'shell') and router.shell:
             page.add(router.shell)
        router.navegar_a("dashboard")
        page.update()

    # Iniciar con login
    page.add(crear_login_view(page, on_login_success))
    page.update()


if __name__ == "__main__":
    ft.app(target=main)
