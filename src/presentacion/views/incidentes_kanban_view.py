from typing import Callable, Optional, List
import flet as ft
from src.aplicacion.servicios.servicio_incidentes import ServicioIncidentes
from src.aplicacion.servicios.servicio_propiedades import ServicioPropiedades

class IncidentesKanbanView(ft.Column):
    """Vista Kanban para gestión de incidentes con 5 columnas de estado."""
    
    def __init__(self, page: ft.Page, servicio_incidentes: ServicioIncidentes, servicio_propiedades: ServicioPropiedades, on_navigate: Callable):
        super().__init__(expand=True, spacing=0)
        self.page = page
        self.servicio = servicio_incidentes
        self.servicio_propiedades = servicio_propiedades
        self.on_navigate = on_navigate
        
        # Filtros actuales
        self.filtro_busqueda = None
        self.filtro_propiedad = None
        self.filtro_prioridad = None
        self.filtros_avanzados_visible = False
        
        # Cargar datos
        self.incidentes = []
        self.propiedades = []
        self.cargar_datos()
        
        # Construir UI
        self.construir_ui()
    
    def cargar_datos(self):
        """Carga incidentes y propiedades."""
        self.incidentes = self.servicio.listar_con_filtros(
            busqueda=self.filtro_busqueda,
            id_propiedad=self.filtro_propiedad,
            prioridad=self.filtro_prioridad
        )
        self.propiedades = self.servicio_propiedades.listar_propiedades()
    
    def construir_ui(self):
        """Construye la interfaz completa."""
        # Header con título y botón
        header = ft.Row([
            ft.Text("Gestión de Incidentes", size=24, weight=ft.FontWeight.BOLD),
            ft.ElevatedButton(
                "Reportar Incidente",
                icon=ft.Icons.ADD,
                on_click=lambda _: self.on_navigate("incidente_reportar")
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        # Panel de filtros
        filtros_panel = self._crear_panel_filtros()
        
        # Tablero Kanban
        kanban_board = self._crear_tablero_kanban()
        
        self.controls = [
            ft.Container(content=header, padding=20),
            filtros_panel,
            ft.Divider(height=1),
            kanban_board
        ]
    
    def _crear_panel_filtros(self) -> ft.Container:
        """Crea el panel de filtros avanzados."""
        # Campo de búsqueda
        self.txt_busqueda = ft.TextField(
            hint_text="Buscar por ID o descripción...",
            prefix_icon=ft.Icons.SEARCH,
            value=self.filtro_busqueda if self.filtro_busqueda else "",
            on_change=self.aplicar_filtros,
            expand=True
        )
        
        # Dropdown de propiedades
        opciones_propiedades = [ft.dropdown.Option(key="0", text="Todas las propiedades")]
        opciones_propiedades.extend([
            ft.dropdown.Option(key=str(p.id_propiedad), text=f"{p.direccion_propiedad}")
            for p in self.propiedades
        ])
        
        self.dd_propiedad = ft.Dropdown(
            label="Propiedad",
            options=opciones_propiedades,
            value=str(self.filtro_propiedad) if self.filtro_propiedad else "0",
            on_change=self.aplicar_filtros,
            width=250
        )
        
        # Dropdown de prioridad
        self.dd_prioridad = ft.Dropdown(
            label="Prioridad",
            options=[
                ft.dropdown.Option("Todas", text="Todas"),
                ft.dropdown.Option("Urgente", text="🔴 Urgente"),
                ft.dropdown.Option("Alta", text="🟠 Alta"),
                ft.dropdown.Option("Media", text="🟡 Media"),
                ft.dropdown.Option("Baja", text="🟢 Baja"),
            ],
            value=self.filtro_prioridad if self.filtro_prioridad else "Todas",
            on_change=self.aplicar_filtros,
            width=200
        )
        
        filtros_row = ft.Row([
            self.txt_busqueda,
            self.dd_propiedad,
            self.dd_prioridad
        ], spacing=10)
        
        return ft.Container(
            content=filtros_row,
            padding=ft.padding.symmetric(horizontal=20, vertical=10),
            bgcolor=ft.Colors.GREY_50
        )
    
    def _crear_tablero_kanban(self) -> ft.Container:
        """Crea el tablero Kanban con 5 columnas."""
        # Agrupar incidentes por estado
        reportados = [i for i in self.incidentes if i.estado in ["Reportado", "En Revision"]]
        cotizados = [i for i in self.incidentes if i.estado == "Cotizado"]
        aprobados = [i for i in self.incidentes if i.estado == "Aprobado"]
        en_reparacion = [i for i in self.incidentes if i.estado == "En Reparacion"]
        finalizados = [i for i in self.incidentes if i.estado == "Finalizado"]
        
        # Crear columnas
        col_reportado = self._crear_columna("Reportado", reportados, ft.Colors.RED_400)
        col_cotizado = self._crear_columna("Cotizado", cotizados, ft.Colors.AMBER_600)
        col_aprobado = self._crear_columna("Aprobado", aprobados, ft.Colors.GREEN_600)
        col_reparacion = self._crear_columna("En Reparación", en_reparacion, ft.Colors.BLUE_600)
        col_finalizado = self._crear_columna("Finalizado", finalizados, ft.Colors.GREY_600)
        
        board = ft.Row([
            col_reportado,
            col_cotizado,
            col_aprobado,
            col_reparacion,
            col_finalizado
        ], spacing=15, expand=True, scroll=ft.ScrollMode.AUTO)
        
        return ft.Container(
            content=board,
            padding=20,
            expand=True
        )
    
    def _crear_columna(self, titulo: str, incidentes: List, color: str) -> ft.Container:
        """Crea una columna del tablero Kanban."""
        # Header de columna con contador
        header = ft.Container(
            content=ft.Row([
                ft.Text(titulo, weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.WHITE),
                ft.Container(
                    content=ft.Text(str(len(incidentes)), color=ft.Colors.WHITE, size=12, weight=ft.FontWeight.BOLD),
                    bgcolor=ft.Colors.with_opacity(0.3, ft.Colors.WHITE),
                    padding=ft.padding.symmetric(horizontal=8, vertical=2),
                    border_radius=10
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=12,
            bgcolor=color,
            border_radius=ft.border_radius.only(top_left=8, top_right=8)
        )
        
        # Tarjetas de incidentes
        tarjetas = [self._crear_tarjeta_incidente(inc, color) for inc in incidentes]
        
        if not tarjetas:
            tarjetas = [ft.Container(
                content=ft.Text("No hay incidentes", size=12, color=ft.Colors.GREY_400, italic=True),
                padding=20,
                alignment=ft.alignment.center
            )]
        
        contenido_columna = ft.Column(
            controls=tarjetas,
            scroll=ft.ScrollMode.AUTO,
            spacing=10,
            expand=True
        )
        
        return ft.Container(
            content=ft.Column([header, ft.Container(content=contenido_columna, padding=10, expand=True)], spacing=0),
            width=280,
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=8,
            bgcolor=ft.Colors.WHITE,
            expand=True
        )
    
    def _crear_tarjeta_incidente(self, incidente, color_columna) -> ft.Container:
        """Crea una tarjeta de incidente."""
        # Iconos y colores por prioridad
        prioridad_config = {
            "Urgente": ("🔴", ft.Colors.RED_400),
            "Alta": ("🟠", ft.Colors.ORANGE_400),
            "Media": ("🟡", ft.Colors.AMBER_600),
            "Baja": ("🟢", ft.Colors.GREEN_400)
        }
        
        icono_prioridad, color_prioridad = prioridad_config.get(incidente.prioridad, ("⚪", ft.Colors.GREY_400))
        
        # Dirección truncada
        direccion = incidente.direccion_propiedad if hasattr(incidente, 'direccion_propiedad') and incidente.direccion_propiedad else f"Propiedad #{incidente.id_propiedad}"
        direccion_corta = direccion[:28] + "..." if len(direccion) > 28 else direccion
        
        # Indicador de días sin resolver con color
        dias = incidente.dias_sin_resolver
        if dias > 15:
            dias_color = ft.Colors.RED_700
        elif dias > 7:
            dias_color = ft.Colors.ORANGE_700
        else:
            dias_color = ft.Colors.GREY_700
        
        tarjeta = ft.Container(
            content=ft.Column([
                # Header con ID y botón
                ft.Row([
                    ft.Row([
                        ft.Text(icono_prioridad, size=14),
                        ft.Text(f"Inc #{incidente.id_incidente}", weight=ft.FontWeight.BOLD, size=13)
                    ], spacing=5),
                    ft.IconButton(
                        icon=ft.Icons.ARROW_FORWARD_IOS,
                        icon_size=14,
                        tooltip="Ver detalles",
                        on_click=lambda _, id=incidente.id_incidente: self.on_navigate("incidente_detalle", id_incidente=id)
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                # Prioridad
                ft.Container(
                    content=ft.Text(f"⚡ {incidente.prioridad}", size=11, color=ft.Colors.WHITE),
                    bgcolor=color_prioridad,
                    padding=ft.padding.symmetric(horizontal=6, vertical=2),
                    border_radius=4
                ),
                
                # Dirección
                ft.Row([
                    ft.Icon(ft.Icons.HOME, size=14, color=ft.Colors.GREY_600),
                    ft.Text(direccion_corta, size=11, color=ft.Colors.GREY_800)
                ], spacing=5),
                
                # Días sin resolver
                ft.Row([
                    ft.Icon(ft.Icons.SCHEDULE, size=14, color=dias_color),
                    ft.Text(f"{dias} días", size=11, color=dias_color, weight=ft.FontWeight.BOLD)
                ], spacing=5),
            ], spacing=6),
            padding=12,
            border=ft.border.all(1, color_columna),
            border_radius=8,
            bgcolor=ft.Colors.WHITE,
            on_click=lambda _, id=incidente.id_incidente: self.on_navigate("incidente_detalle", id_incidente=id),
            ink=True
        )
        
        return tarjeta
    
    def aplicar_filtros(self, e):
        """Aplica los filtros y recarga la vista."""
        # Actualizar filtros
        self.filtro_busqueda = self.txt_busqueda.value if self.txt_busqueda.value else None
        self.filtro_propiedad = int(self.dd_propiedad.value) if self.dd_propiedad.value != "0" else None
        self.filtro_prioridad = self.dd_prioridad.value if self.dd_prioridad.value != "Todas" else None
        
        # Recargar datos
        self.cargar_datos()
        
        # Reconstruir UI
        self.controls.clear()
        self.construir_ui()
        self.update()
