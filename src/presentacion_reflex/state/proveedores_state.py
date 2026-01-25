from typing import Any, Dict, List

import reflex as rx

from src.aplicacion.servicios.servicio_proveedores import ServicioProveedores
from src.infraestructura.persistencia.database import db_manager
from src.infraestructura.persistencia.repositorio_persona_sqlite import RepositorioPersonaSQLite
from src.infraestructura.persistencia.repositorio_proveedores_sqlite import (
    RepositorioProveedoresSQLite,
)


class ProveedoresState(rx.State):
    """Estado para la gestión de proveedores."""

    # Datos
    proveedores: List[Dict[str, Any]] = []
    personas_disponibles: List[Dict[str, Any]] = []  # Para el select de crear

    # Filtros y Búsqueda
    search_text: str = ""
    filter_especialidad: str = "Todas"

    # Paginación
    current_page: int = 1
    page_size: int = 10
    total_items: int = 0

    # Modal y Formulario
    show_form_modal: bool = False
    is_editing: bool = False
    form_data: Dict[str, Any] = {
        "id_proveedor": None,
        "id_persona": "",
        "especialidad": "Otros",
        "calificacion": 5.0,
        "observaciones": "",
    }

    # UI State
    is_loading: bool = False
    error_message: str = ""

    def on_load(self):
        """Carga inicial de datos."""
        return [ProveedoresState.load_data, ProveedoresState.load_personas_options]

    @rx.event(background=True)
    async def load_data(self):
        """Carga la lista de proveedores."""
        async with self:
            self.is_loading = True
            self.error_message = ""

        try:
            repo = RepositorioProveedoresSQLite(db_manager)
            servicio = ServicioProveedores(db_manager)
            servicio.repo = repo

            # Obtener todos (el servicio filtra por estado_registro=1)
            # Nota: El servicio actual devuelve objetos Proveedor.
            # Necesitamos filtrar en memoria o mejorar el repositorio para paginación/filtros SQL.
            # Por simplicidad y tamaño esperado, filtramos en memoria por ahora.

            todos = servicio.listar_proveedores()

            # Convertir a dicts y filtrar
            filtered = []
            search_lower = self.search_text.lower()

            for p in todos:
                # Mapear objeto a dict para UI
                p_dict = {
                    "id_proveedor": p.id_proveedor,
                    "id_persona": p.id_persona,
                    "nombre": p.nombre_completo or "Sin Nombre",
                    "contacto": p.contacto or "Sin Contacto",
                    "especialidad": p.especialidad,
                    "calificacion": p.calificacion,
                    "observaciones": p.observaciones or "",
                }

                # Filtros
                match_text = (
                    search_lower in p_dict["nombre"].lower()
                    or search_lower in p_dict["especialidad"].lower()
                )
                match_spec = (
                    self.filter_especialidad == "Todas"
                    or self.filter_especialidad == p_dict["especialidad"]
                )

                if match_text and match_spec:
                    filtered.append(p_dict)

            async with self:
                self.total_items = len(filtered)
                # Paginación en memoria
                start = (self.current_page - 1) * self.page_size
                end = start + self.page_size
                self.proveedores = filtered[start:end]
                self.is_loading = False

        except Exception as e:
            async with self:
                self.error_message = f"Error carga: {str(e)}"
                self.is_loading = False

    @rx.event(background=True)
    async def load_personas_options(self):
        """Carga personas para el select del formulario."""
        try:
            repo_personas = RepositorioPersonaSQLite(db_manager)
            personas = repo_personas.listar_activos()

            # TODO: Idealmente solo cargar personas que NO son proveedores aún.
            # O mostrar todos y validar en backend.

            # Simple conversion for select
            options = [
                {"value": str(p.id_persona), "label": f"{p.nombre_completo} ({p.numero_documento})"}
                for p in personas
            ]
            async with self:
                self.personas_disponibles = options
        except Exception:
            pass  # print(f"Error loading personas: {e}") [OpSec Removed]

    # Setters y Helpers
    def set_search(self, value: str):
        self.search_text = value
        self.current_page = 1
        return ProveedoresState.load_data

    def set_filter_especialidad(self, value: str):
        self.filter_especialidad = value
        self.current_page = 1
        return ProveedoresState.load_data

    def next_page(self):
        if self.current_page * self.page_size < self.total_items:
            self.current_page += 1
            return ProveedoresState.load_data

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            return ProveedoresState.load_data

    # CRUD
    def open_create_modal(self):
        self.is_editing = False
        self.form_data = {
            "id_proveedor": None,
            "id_persona": "",
            "especialidad": "Otros",
            "calificacion": 5.0,
            "observaciones": "",
        }
        self.show_form_modal = True

    def open_edit_modal(self, proveedor: Dict):
        self.is_editing = True
        self.form_data = {
            "id_proveedor": proveedor["id_proveedor"],
            "id_persona": str(proveedor["id_persona"]),
            "especialidad": proveedor["especialidad"],
            "calificacion": float(proveedor["calificacion"]),
            "observaciones": proveedor["observaciones"],
        }
        self.show_form_modal = True

    def close_modal(self):
        self.show_form_modal = False
        self.error_message = ""

    def handle_open_change(self, is_open: bool):
        if not is_open:
            self.close_modal()

    def set_form_field(self, field: str, value: Any):
        self.form_data[field] = value

    @rx.event(background=True)
    async def save_proveedor(self):
        """Guarda o actualiza el proveedor."""
        async with self:
            self.is_loading = True
            self.error_message = ""

        try:
            repo = RepositorioProveedoresSQLite(db_manager)
            servicio = ServicioProveedores(db_manager)
            servicio.repo = repo

            datos = self.form_data.copy()

            # Validaciones simples
            if not datos["id_persona"]:
                raise ValueError("Debe seleccionar una persona")

            usuario = "admin"  # TODO: Auth

            if self.is_editing:
                servicio.actualizar_proveedor(datos["id_proveedor"], datos)
            else:
                datos["id_persona"] = int(datos["id_persona"])
                servicio.crear_proveedor(datos, usuario)

            async with self:
                self.show_form_modal = False
                self.is_loading = False

            yield ProveedoresState.load_data

        except Exception as e:
            async with self:
                self.error_message = str(e)
                self.is_loading = False

    @rx.event(background=True)
    async def eliminar_proveedor(self, id_proveedor: int):
        """Elimina (soft delete) un proveedor."""
        try:
            repo = RepositorioProveedoresSQLite(db_manager)
            servicio = ServicioProveedores(db_manager)
            servicio.repo = repo
            servicio.eliminar_proveedor(id_proveedor)
            yield ProveedoresState.load_data
        except Exception as e:
            async with self:
                self.error_message = f"Error al eliminar: {e}"
