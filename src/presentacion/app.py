"""
Aplicacion Principal - Inmobiliaria Velar
Punto de entrada del sistema Flet.
"""

import reflex as rx

from src.presentacion.theme import colors as app_colors
from src.presentacion.views.login_view import crear_login_view


class InmobiliariaVelarApp:
    """Control principal de la aplicacion."""

    def __init__(self, page: ft.Page):
        self.page = page
        self.usuario_actual = None
        self.router = None

        # Configurar pagina
        self.page.title = "Inmobiliaria Velar - Sistema de Gestion"
        self.page.window_width = 1366
        self.page.window_height = 768
        self.page.padding = 0
        self.page.bgcolor = app_colors.BACKGROUND

        # Estado de la sidebar (persistente)
        self.sidebar_collapsed = False

        # Mostrar login
        self._mostrar_login()

    def _mostrar_login(self):
        """Muestra la pantalla de login."""
        self.page.clean()
        login_view = crear_login_view(self.page, self._on_login_success)
        self.page.add(login_view)

    def _on_login_success(self, usuario):
        """Callback cuando el login es exitoso."""
        self.usuario_actual = usuario
        self._inicializar_router()
        self.router.navegar_a("dashboard")

    def _toggle_sidebar(self):
        """Alterna el estado de la sidebar y recarga la vista actual si es necesario."""
        self.sidebar_collapsed = not self.sidebar_collapsed
        # No necesitamos recargar toda la vista si la sidebar maneja su propio estado visual,
        # pero para persistencia limpia, el router recargará al navegar.
        # Sin embargo, si queremos reacción inmediata sin navegar, Sidebar debe manejarlo internamente
        # y solo avisar a App para persistencia.
        # En este diseño simple, App solo guarda el estado para la PROXIMA navegación.
        # PERO para que el toggle funcione IN-PLACE, pasaremos este callback a Sidebar.
        pass

    def _inicializar_router(self):
        from src.aplicacion.servicios.servicio_incidentes import ServicioIncidentes
        from src.infraestructura.persistencia.database import DatabaseManager
        from src.presentacion.components.sidebar import Sidebar
        from src.presentacion.router import Router
        from src.presentacion.views.dashboard_view import crear_dashboard_view
        from src.presentacion.views.incidente_detail_view import IncidenteDetailView
        from src.presentacion.views.incidente_form_view import IncidenteFormView
        from src.presentacion.views.incidentes_list_view import IncidentesListView

        self.router = Router(self.page, self.usuario_actual)
        self.db_manager = DatabaseManager()
        self.servicio_incidentes = ServicioIncidentes(self.db_manager)

        # Helper para layout persistente (Sidebar)
        def layout_con_sidebar(content):
            # Wrapper para actualizar el estado en App
            def on_sidebar_toggle(collapsed):
                self.sidebar_collapsed = collapsed

            sidebar = Sidebar(
                self.usuario_actual,
                on_navigate=self.router.navegar_a,
                on_logout=self._mostrar_login,
                collapsed=self.sidebar_collapsed,
                on_toggle=on_sidebar_toggle,
            )
            # Marcar activo según vista actual (simple logic)
            # En una impl más avanzada sidebar sabría cual es la active route
            return ft.Row([sidebar, ft.Container(content, expand=True)], spacing=0, expand=True)

        # -- Registrar Vistas --

        # Dashboard (Ya retorna layout completo)
        self.router.registrar_vista(
            "dashboard",
            lambda: crear_dashboard_view(
                self.page,
                self.usuario_actual,
                self._mostrar_login,
                on_navigate=self.router.navegar_a,
            ),
        )

        # Incidentes Lista
        self.router.registrar_vista(
            "incidentes",
            lambda: layout_con_sidebar(IncidentesListView(self.page, self.servicio_incidentes)),
        )

        # Reportar Incidente
        self.router.registrar_vista(
            "incidente_reportar",
            lambda: layout_con_sidebar(
                IncidenteFormView(self.page, self.servicio_incidentes, self.db_manager)
            ),
        )

        # Detalle Incidente (Ruta dinámica simulada: incidente_detalle/<id>)
        # El Router simple de router.py no soporta rutas dinámicas tipo Flask.
        # Necesitamos un wrapper o el router debe soportar kwargs.
        # Router.navegar_a("incidente_detalle", id_incidente=123) funciona si registramos:
        self.router.registrar_vista(
            "incidente_detalle",
            lambda id_incidente: layout_con_sidebar(
                IncidenteDetailView(self.page, self.servicio_incidentes, id_incidente)
            ),
        )


def main(page: ft.Page):
    """Funcion principal de la app."""
    InmobiliariaVelarApp(page)
