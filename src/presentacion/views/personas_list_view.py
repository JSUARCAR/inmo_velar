"""
Vista: Listado de Personas
Permite visualizar, buscar y filtrar personas.
Refactorizado para carga asíncrona (Optimización 17.3)
Adaptado a Flet moderno (sin UserControl).
"""

import flet as ft
import time
import threading
from typing import Optional, Callable, List
from src.presentacion.theme import colors, styles
from src.presentacion.components.widgets import PersonaDataTable
from src.aplicacion.servicios import ServicioPersonas, PersonaConRoles
from src.infraestructura.persistencia.database import DatabaseManager

# Integración Fase 3: Debouncer para búsquedas
from src.presentacion.utils.debouncer import Debouncer

# Integración Fase 4: Paginación
from src.presentacion.components.pagination_manager import PaginationManager

class PersonasListView(ft.Container):
    def __init__(
        self,
        page: ft.Page,
        on_nueva_persona: Callable,
        on_editar_persona: Callable[[int], None]
    ):
        super().__init__(expand=True, padding=30, bgcolor=colors.BACKGROUND)
        self.page_ref = page  # Referencia explicita por si self.page no está listo
        self.on_nueva_persona = on_nueva_persona
        self.on_editar_persona = on_editar_persona
        
        # Servicios
        self.db_manager = DatabaseManager()
        self.servicio = ServicioPersonas(self.db_manager)
        
        # Estado
        self.personas: List[PersonaConRoles] = []
        self.cargando = True
        self.filtro_rol = "Todos"
        self.busqueda = ""
        self.solo_activos = True
        
        # Paginación
        self.current_page = 1
        self.page_size = 25
        self.total_items = 0
        
        # Componentes UI (referencias para update)
        self.txt_contador = ft.Text("Esperando...", size=14, color=colors.TEXT_SECONDARY)
        self.tabla_container = ft.Container(expand=True)
        self.txt_busqueda = ft.Ref[ft.TextField]()
        
        # Debouncer para búsqueda (500ms delay)
        self.search_debouncer = Debouncer(
            delay_ms=500,
            callback=self._on_search_debounced,
            name="personas_search"
        )
        
        # Componente de paginación
        self.pagination = PaginationManager(
            total_items=0,
            items_per_page=25,
            on_page_change=self._on_page_change,
            on_page_size_change=self._on_page_size_change
        )

        # --- Construcción UI (adaptado de build) ---
        
        # Barra de búsqueda (con debouncing para búsqueda en tiempo real)
        search_bar = ft.TextField(
            ref=self.txt_busqueda,
            hint_text="Buscar por nombre o documento...",
            prefix_icon=ft.Icons.SEARCH,
            border_color=colors.BORDER_DEFAULT,
            focused_border_color=colors.PRIMARY,
            expand=True,
            on_change=self._on_search_change,  # Búsqueda en tiempo real con debounce
            on_submit=lambda e: self.cargar_datos()  # Enter fuerza búsqueda inmediata
        )
        
        # Filtros
        filtro_rol_dropdown = ft.Dropdown(
            label="Filtrar por Rol",
            options=[
                ft.dropdown.Option("Todos"),
                ft.dropdown.Option("Propietario"),
                ft.dropdown.Option("Arrendatario"),
                ft.dropdown.Option("Codeudor"),
                ft.dropdown.Option("Asesor"),
            ],
            value="Todos",
            width=200,
            on_change=self._on_filtro_change
        )
        
        switch_activos = ft.Switch(
            label="Solo activos",
            value=True,
            active_color=colors.SUCCESS,
            on_change=self._on_activos_change
        )
        
        # Botón Nueva
        btn_nueva = ft.ElevatedButton(
            "Nueva Persona",
            icon=ft.Icons.ADD,
            on_click=lambda e: self.on_nueva_persona(),
            style=ft.ButtonStyle(bgcolor=colors.PRIMARY, color=colors.TEXT_ON_PRIMARY)
        )
        
        # Layout Principal
        self.content = ft.Column(
            [
                # Breadcrumb y Título
                ft.Container(
                    content=ft.Column([
                        ft.Text("Inicio > Personas", style=styles.breadcrumb_text()),
                        ft.Text("Gestión de Personas", size=24, weight=ft.FontWeight.BOLD, color=colors.TEXT_PRIMARY),
                    ]),
                    padding=ft.padding.only(bottom=20)
                ),
                
                # Barra de herramientas
                ft.Container(
                    content=ft.Row(
                        [
                            search_bar,
                            ft.IconButton(
                                icon=ft.Icons.SEARCH, 
                                icon_color=colors.PRIMARY, 
                                on_click=lambda e: self.cargar_datos()
                            ),
                            filtro_rol_dropdown,
                            switch_activos,
                            btn_nueva,
                        ],
                        spacing=15
                    ),
                    padding=ft.padding.only(bottom=15)
                ),
                
                # Contador
                ft.Container(content=self.txt_contador, padding=ft.padding.only(bottom=10)),
                
                # Tabla (Contenedor dinámico)
                self.tabla_container,
                
                # Paginación
                ft.Container(
                    content=self.pagination,
                    padding=ft.padding.only(top=20)
                ),
            ],
            expand=True,
            spacing=0
        )

    def did_mount(self):
        """Se ejecuta cuando el control es agregado a la página."""
        self.cargar_datos()

    def _on_filtro_change(self, e):
        self.filtro_rol = e.control.value
        self.current_page = 1  # Reset a página 1 al cambiar filtros
        self.cargar_datos()

    def _on_activos_change(self, e):
        self.solo_activos = e.control.value
        self.current_page = 1  # Reset a página 1
        self.cargar_datos()
    
    def _on_search_change(self, e):
        """Handler para cambios en el campo de búsqueda (con debounce)."""
        # Disparar debouncer en cada tecla
        self.search_debouncer()
    
    def _on_search_debounced(self):
        """Callback ejecutado por el debouncer después del delay."""
        # Obtener valor actual del TextField
        if self.txt_busqueda.current:
            self.busqueda = self.txt_busqueda.current.value or ""
            self.current_page = 1  # Reset a página 1 en búsqueda
            self.cargar_datos()
    
    def _on_page_change(self, page: int):
        """Handler cuando cambia la página."""
        self.current_page = page
        self.cargar_datos()
    
    def _on_page_size_change(self, page_size: int):
        """Handler cuando cambia el tamaño de página."""
        self.page_size = page_size
        self.current_page = 1  # Reset a página 1
        self.cargar_datos()

    def cargar_datos(self):
        """Inicia el proceso de carga en un hilo separado."""
        self.cargando = True
        
        # Obtener valor actual de búsqueda de la referencia
        if self.txt_busqueda.current:
            self.busqueda = self.txt_busqueda.current.value.strip()
        
        # Mostrar loading inmediatamente
        self._mostrar_loading()
        
        # Ejecutar consulta en hilo secundario
        threading.Thread(target=self._fetch_data_thread, daemon=True).start()

    def _mostrar_loading(self):
        """Actualiza la UI para mostrar estado de carga."""
        self.tabla_container.content = ft.Container(
            content=ft.Column([
                ft.ProgressBar(width=400, color=colors.PRIMARY),
                ft.Text("Cargando personas...", color=colors.TEXT_SECONDARY)
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.alignment.center,
            expand=True
        )
        self.txt_contador.value = "Consultando base de datos..."
        self.update()

    def _fetch_data_thread(self):
        """Lógica de obtención de datos paginados (ejecutada en background)."""
        try:
            start_time = time.time()
            
            # Llamar a método paginado
            result = self.servicio.listar_personas_paginado(
                page=self.current_page,
                page_size=self.page_size,
                filtro_rol=None if self.filtro_rol == "Todos" else self.filtro_rol,
                solo_activos=self.solo_activos,
                busqueda=self.busqueda if self.busqueda else None
            )
            
            elapsed = time.time() - start_time
            
            # Actualizar estado
            self.personas = result.items
            self.total_items = result.total
            
            # Volver a UI thread
            self._schedule_ui_update(elapsed, error=None)
            
        except Exception as e:
            pass  # print(f"Error cargando personas: {e}") [OpSec Removed]
            import traceback
            traceback.print_exc()
            self._schedule_ui_update(0, error=str(e))

    def _schedule_ui_update(self, elapsed, error):
        """Helper para volver al hilo principal si es necesario (Flet maneja esto, pero es buena práctica mental)."""
        # Verificar si el control ya está montado en una página
        if self.page:
            self._actualizar_tabla(elapsed, error)
        else:
            pass  # print("⚠️ Advertencia: Intento de actualizar PersonasListView sin estar montado en página") [OpSec Removed]

    def _actualizar_tabla(self, elapsed, error):
        """Renderiza los datos obtenidos."""
        if error:
            self.tabla_container.content = ft.Text(f"Error: {error}", color=colors.ERROR)
            self.txt_contador.value = "Error al cargar"
        elif not self.personas:
            self.tabla_container.content = ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.PERSON_OUTLINE, size=80, color=colors.TEXT_DISABLED),
                    ft.Text("No se encontraron personas", size=16, color=colors.TEXT_SECONDARY),
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.alignment.center,
                expand=True
            )
            self.txt_contador.value = "0 personas encontradas"
        else:
            tabla = PersonaDataTable(
                personas=self.personas,
                on_edit=self.handle_editar,
                on_toggle_estado=self.handle_toggle_estado
            )
            self.tabla_container.content = tabla
            
            # Actualizar info
            start_idx = (self.current_page - 1) * self.page_size + 1
            end_idx = min(start_idx + len(self.personas) - 1, self.total_items)
            self.txt_contador.value = f"Mostrando {start_idx}-{end_idx} de {self.total_items} personas ({elapsed:.3f}s)"
        
        # Actualizar componente de paginación
        self.pagination.set_total_items(self.total_items)
        self.pagination.set_current_page(self.current_page)
        
        self.cargando = False
        self.update()

    def handle_editar(self, id_persona: int):
        self.on_editar_persona(id_persona)

    def handle_toggle_estado(self, id_persona: int, nuevo_estado: bool):
        """Cambio de estado optimista."""
        try:
            if nuevo_estado:
                self.servicio.activar_persona(id_persona, usuario_sistema="admin")
                msg = "Persona activada"
            else:
                self.servicio.desactivar_persona(id_persona, motivo="UI Switch", usuario_sistema="admin")
                msg = "Persona inactivada"
            
            if self.page_ref:
                self.page_ref.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor=colors.SUCCESS)
                self.page_ref.snack_bar.open = True
                self.page_ref.update()
            
            # Recargar sin loading completo bloqueante visualmente si se desea, 
            # pero por consistencia usamos cargar_datos()
            self.cargar_datos()
            
        except Exception as e:
            if self.page_ref:
                self.page_ref.snack_bar = ft.SnackBar(ft.Text(f"Error: {e}"), bgcolor=colors.ERROR)
                self.page_ref.snack_bar.open = True
                self.page_ref.update()

# Función wrapper para compatibilidad con main.py (si fuera necesaria)
def crear_personas_list_view(page, on_nueva, on_editar):
    return PersonasListView(page, on_nueva, on_editar)
