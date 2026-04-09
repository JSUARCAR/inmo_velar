from datetime import datetime
from typing import Any, Dict, List, Optional, TypedDict

import reflex as rx


class IncidenteDict(TypedDict):
    """Estructura tipada para serializacion de Incidente en Reflex."""

    id: int
    descripcion: str
    estado: str
    prioridad: str
    fecha: str
    id_propiedad: int
    direccion_propiedad: str
    id_proveedor: Optional[int]
    origen: str


class IncidentesStateBase(rx.State):
    """Estado base para gestion de Incidentes - Variables de estado."""

    incidentes: List[IncidenteDict] = []
    incidentes_kanban: Dict[str, List[IncidenteDict]] = {
        "Reportado": [],
        "Cotizado": [],
        "Aprobado": [],
        "En Reparacion": [],
        "Finalizado": [],
    }

    is_loading: bool = False
    error_message: str = ""
    view_mode: str = "kanban"

    filter_estado: str = "Todos"
    filter_prioridad: str = "Todas"
    search_text: str = ""

    page: int = 1
    total_pages: int = 1
    items_per_page: int = 12

    estado_options: List[str] = [
        "Todos",
        "Reportado",
        "En Revision",
        "Cotizado",
        "Aprobado",
        "En Reparacion",
        "Finalizado",
        "Cancelado",
    ]
    prioridad_options: List[str] = ["Todas", "Alta", "Media", "Baja"]
    propiedades_options: List[Dict[str, Any]] = []

    propiedad_search: str = ""
    propiedad_menu_open: bool = False
    propiedad_selected_label: str = ""

    @rx.var
    def filtered_propiedades_options(self) -> List[tuple[str, str]]:
        search_lower = self.propiedad_search.lower()
        if not search_lower:
            return [(p["texto"], str(p["id"])) for p in self.propiedades_options]
        return [
            (p["texto"], str(p["id"]))
            for p in self.propiedades_options
            if search_lower in p["texto"].lower()
        ]

    @rx.var
    def incidentes_reportado(self) -> List[IncidenteDict]:
        return self.incidentes_kanban.get("Reportado", [])

    @rx.var
    def incidentes_cotizado(self) -> List[IncidenteDict]:
        return self.incidentes_kanban.get("Cotizado", [])

    @rx.var
    def incidentes_aprobado(self) -> List[IncidenteDict]:
        return self.incidentes_kanban.get("Aprobado", [])

    @rx.var
    def incidentes_en_reparacion(self) -> List[IncidenteDict]:
        return self.incidentes_kanban.get("En Reparacion", [])

    @rx.var
    def incidentes_finalizado(self) -> List[IncidenteDict]:
        return self.incidentes_kanban.get("Finalizado", [])

    kanban_columns: Dict[str, List[str]] = {
        "Reportado": ["Reportado", "En Revision"],
        "Cotizado": ["Cotizado"],
        "Aprobado": ["Aprobado"],
        "En Reparacion": ["En Reparacion"],
        "Finalizado": ["Finalizado", "Cancelado"],
    }

    modal_open: bool = False
    form_data: Dict[str, Any] = {
        "id_propiedad": "",
        "descripcion": "",
        "prioridad": "Media",
        "origen_reporte": "Inquilino",
        "fecha_incidente": "",
        "responsable_pago": "Inquilino",
    }

    origen_reporte_options: List[str] = ["Inquilino", "Propietario", "Inmobiliaria"]
    responsable_pago_options: List[str] = [
        "Inquilino",
        "Propietario",
        "Inmobiliaria",
        "Aseguradora",
    ]

    details_modal_open: bool = False
    selected_incidente: Dict[str, Any] = {}
    cotizaciones: List[Dict[str, Any]] = []

    show_quote_form: bool = False
    show_finalize_form: bool = False
    finalize_date: str = ""

    cotizacion_form: Dict[str, Any] = {
        "id_proveedor": "",
        "materiales": 0,
        "mano_obra": 0,
        "descripcion": "",
        "dias": 1,
    }

    proveedores_options: List[Dict[str, Any]] = []

    detalles_editar_open: bool = False

    current_entidad_tipo: str = ""
    current_entidad_id: str = ""

    def set_propiedad_search(self, value: str):
        self.propiedad_search = value

    def toggle_propiedad_menu(self, open: bool):
        self.propiedad_menu_open = open

    def select_propiedad(self, value: str, label: str):
        self.propiedad_selected_label = label
        self.form_data["id_propiedad"] = value
        self.propiedad_menu_open = False

    def set_form_field(self, key: str, value: Any):
        self.form_data[key] = value

    def open_modal(self):
        self.modal_open = True
        self.form_data = {
            "id_propiedad": "",
            "descripcion": "",
            "prioridad": "Media",
            "origen_reporte": "Inquilino",
            "fecha_incidente": "",
            "responsable_pago": "Inquilino",
        }
        self.propiedad_selected_label = ""

    def close_modal(self):
        self.modal_open = False

    def toggle_view_mode(self, mode: str):
        self.view_mode = mode

    def set_filter_estado(self, estado: str):
        self.filter_estado = estado

    def set_filter_prioridad(self, prioridad: str):
        self.filter_prioridad = prioridad

    def set_search_text(self, text: str):
        self.search_text = text

    def set_page(self, page: int):
        self.page = page
