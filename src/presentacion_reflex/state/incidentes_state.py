import pydantic
from datetime import datetime
from typing import Any, Dict, List, Optional

import reflex as rx
from rxconfig import config

from src.aplicacion.servicios.servicio_incidentes import ServicioIncidentes
from src.infraestructura.persistencia.database import db_manager
from src.presentacion_reflex.state.documentos_mixin import DocumentosStateMixin
from src.infraestructura.servicios.pdf_elite.templates.incidente_template_elite import (
    IncidenteTemplateElite,
)
from src.aplicacion.servicios.servicio_configuracion import ServicioConfiguracion
from src.core.auth import obtener_usuario_actual, obtener_usuario_actual_async
from pathlib import Path


class IncidenteDict(pydantic.BaseModel):
    """Estructura tipada para serialización de Incidente en Reflex."""

    id: int
    descripcion: str
    estado: str
    prioridad: str
    fecha: str
    id_propiedad: int
    direccion_propiedad: str
    id_proveedor: Optional[int]
    origen: str
    nombre_propietario: str
    nombre_inquilino: str
    nombre_habitante: str
    telefono_propietario: str
    telefono_inquilino: str
    telefono_habitante: str
    costo_incidente: Optional[int] = None
    fecha_arreglo: Optional[str] = None
    nombre_proveedor: Optional[str] = None
    cotizaciones_resumen: List[Dict[str, Any]] = []
    estado_pago: str = "Pendiente"
    plan_pago: Optional[Dict[str, Any]] = None


class IncidentesState(DocumentosStateMixin):
    """Estado para gestión de Incidentes."""

    # Datos
    incidentes: List[IncidenteDict] = []
    incidentes_kanban: Dict[str, List[IncidenteDict]] = {
        "Reportado": [],
        "Cotizado": [],
        "Aprobado": [],
        "En Reparacion": [],
        "Finalizado": [],
    }

    # UI State
    is_loading: bool = False
    error_message: str = ""
    view_mode: str = "kanban"  # "list" or "kanban"

    # Filtros
    filter_estado: str = "Todos"
    filter_prioridad: str = "Todas"
    filter_estado_pago: str = ""
    search_text: str = ""

    # Ordenamiento
    sort_by: str = "fecha"
    sort_order: str = "desc"

    # Pagination
    page: int = 1
    total_pages: int = 1
    items_per_page: int = 50

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
    estados_pago_options: List[str] = ["Todos"]
    propiedades_options: List[Dict[str, Any]] = []

    # Combobox State - Propiedad Afectada
    propiedad_search: str = ""
    propiedad_menu_open: bool = False
    propiedad_selected_label: str = ""

    @rx.var
    def filtered_propiedades_options(self) -> List[tuple[str, str]]:
        """Opciones filtradas de propiedades para el combobox (texto, id_propiedad)."""
        search_lower = self.propiedad_search.lower()
        if not search_lower:
            return [(p["texto"], str(p["id"])) for p in self.propiedades_options]
        return [
            (p["texto"], str(p["id"]))
            for p in self.propiedades_options
            if search_lower in p["texto"].lower()
        ]

    def set_propiedad_search(self, value: str):
        """Actualiza el texto de búsqueda de propiedad."""
        self.propiedad_search = value

    def toggle_propiedad_menu(self, open: bool):
        """Abre o cierra el menú del combobox de propiedad."""
        self.propiedad_menu_open = open

    def select_propiedad(self, value: str, label: str):
        """Selecciona una propiedad del combobox."""
        self.propiedad_selected_label = label
        self.form_data["id_propiedad"] = value
        self.propiedad_menu_open = False

    # Mapeo de estados backend a columnas Kanban
    # Backend states: Reportado, En Revision, Cotizado, Aprobado, En Reparacion, Finalizado, Cancelado
    kanban_columns: Dict[str, List[str]] = {
        "Reportado": [
            "Reportado",
            "En Revision",
        ],  # Agrupamos En Revision aquí o podría tener su propia col
        "Cotizado": ["Cotizado"],
        "Aprobado": ["Aprobado"],
        "En Reparacion": ["En Reparacion"],
        "Finalizado": [
            "Finalizado",
            "Cancelado",
        ],  # Agrupamos Cancelado aquí por ahora o lo ocultamos
    }

    # Modal Create/Edit
    modal_open: bool = False
    form_data: Dict[str, Any] = {
        "id_propiedad": "",
        "descripcion": "",
        "prioridad": "Media",
        "origen_reporte": "Inquilino",
        "fecha_incidente": "",  # Default to today in UI if empty
        "responsable_pago": "Inquilino",  # Pre-assign or leave empty
    }

    origen_reporte_options: List[str] = ["Inquilino", "Propietario", "Inmobiliaria"]
    responsable_pago_options: List[str] = [
        "Inquilino",
        "Propietario",
        "Inmobiliaria",
        "Aseguradora",
    ]

    # --- DETAILS MODAL & QUOTING ---
    details_modal_open: bool = False
    selected_incidente: Dict[str, Any] = {}
    cotizaciones: List[Dict[str, Any]] = (
        []
    )  # Lista de cotizaciones del incidente seleccionado

    show_quote_form: bool = False

    # Estado formulario finalización
    show_finalize_form: bool = False
    finalize_date: str = ""
    finalize_obs: str = ""

    # Lista de proveedores para el select
    proveedores_options: List[Dict[str, Any]] = []

    cotizacion_form: Dict[str, Any] = {
        "id_proveedor": "",
        "materiales": 0,
        "mano_obra": 0,
        "descripcion": "",
        "dias": 1,
    }

    # --- EDIT MODAL ---
    edit_modal_open: bool = False
    editing_incidente: Dict[str, Any] = {}
    edit_form_data: Dict[str, Any] = {
        "descripcion": "",
        "prioridad": "Media",
        "origen_reporte": "Inquilino",
        "responsable_pago": "Inquilino",
        "costo_incidente": 0,
        "id_proveedor_asignado": None,
    }
    edit_error: str = ""

    # --- CANCEL MODAL ---
    cancel_modal_open: bool = False
    cancel_incidente: Dict[str, Any] = {}
    cancel_motivo: str = ""
    cancel_error: str = ""

    # --- DIRECT FINISH FORM ---
    show_direct_finish_form: bool = False
    direct_finish_date: str = ""
    direct_finish_obs: str = ""
    direct_finish_costo: int = 0
    direct_finish_proveedor: Optional[str] = None
    direct_finish_error: str = ""

    # --- PAYMENT PLAN MODAL (US1) ---
    show_plan_pago_modal: bool = False
    plan_pago_incidente_id: Optional[int] = None
    plan_pago_data: Dict[str, Any] = {}
    plan_pago_cuotas: List[Dict[str, Any]] = []
    plan_pago_num_cuotas: int = 1
    plan_pago_valor_cuota: int = 0
    plan_pago_error: str = ""
    plan_pago_loading: bool = False

    # Setters explícitos para modales requeridos por Reflex en build
    def set_modal_open(self, value: bool):
        self.modal_open = value

    def set_details_modal_open(self, value: bool):
        self.details_modal_open = value

    def set_edit_modal_open(self, value: bool):
        self.edit_modal_open = value

    def set_cancel_modal_open(self, value: bool):
        self.cancel_modal_open = value

    def close_cancel_modal(self, value: bool = False):
        self.cancel_modal_open = value

    # --- PAYMENT PLAN METHODS (US1) ---
    def set_show_plan_pago_modal(self, value: bool):
        self.show_plan_pago_modal = value

    def set_plan_pago_num_cuotas(self, value: str):
        try:
            self.plan_pago_num_cuotas = int(value) if value else 0
        except (ValueError, TypeError):
            self.plan_pago_num_cuotas = 0
        self._recalcular_valor_cuota()

    def _recalcular_valor_cuota(self):
        """Recalcular valor por cuota basado en el costo del incidente y número de cuotas."""
        if self.plan_pago_incidente_id and self.plan_pago_num_cuotas > 0:
            incidente = next(
                (i for i in self.incidentes if i.id == self.plan_pago_incidente_id),
                None,
            )
            if incidente and incidente.costo_incidente:
                self.plan_pago_valor_cuota = (
                    incidente.costo_incidente // self.plan_pago_num_cuotas
                )

    @rx.event(background=True)
    async def open_plan_pago_modal(self, id_incidente: int):
        """Abre el modal de plan de pago para un incidente."""
        async with self:
            self.plan_pago_incidente_id = id_incidente
            self.plan_pago_error = ""
            self.plan_pago_loading = True
            self.show_plan_pago_modal = True

        try:
            from src.aplicacion.servicios.servicio_plan_pago import (
                ServicioPlanPagoIncidente,
            )
            from src.infraestructura.persistencia.repositorio_plan_pago_postgres import (
                RepositorioPlanPagoPostgres,
            )
            from src.infraestructura.persistencia.repositorio_cuota_postgres import (
                RepositorioCuotaPostgres,
            )
            from src.infraestructura.persistencia.repositorio_incidentes_postgres import (
                RepositorioIncidentesPostgres,
            )
            from src.infraestructura.persistencia.repositorio_bloqueos import (
                RepositorioBloqueos,
            )

            repo_plan = RepositorioPlanPagoPostgres(db_manager)
            repo_cuota = RepositorioCuotaPostgres(db_manager)
            repo_incidentes = RepositorioIncidentesPostgres(db_manager)
            repo_bloqueos = RepositorioBloqueos(db_manager)

            servicio = ServicioPlanPagoIncidente(
                repo_plan, repo_cuota, repo_incidentes, repo_bloqueos
            )

            # Verificar si ya existe un plan
            resultado = servicio.obtener_plan_por_incidente(id_incidente)

            async with self:
                if resultado.get("success"):
                    self.plan_pago_data = resultado["data"]["plan"]
                    self.plan_pago_cuotas = resultado["data"]["cuotas"]
                    self.plan_pago_num_cuotas = self.plan_pago_data.get("num_cuotas", 1)
                    self.plan_pago_valor_cuota = self.plan_pago_data.get(
                        "valor_cuota", 0
                    )
                else:
                    # Nuevo plan - calcular valor basado en costo del incidente
                    incidente = next(
                        (i for i in self.incidentes if i.id == id_incidente),
                        None,
                    )
                    if incidente and incidente.costo_incidente:
                        self.plan_pago_valor_cuota = (
                            incidente.costo_incidente // self.plan_pago_num_cuotas
                        )
                self.plan_pago_loading = False

        except Exception as e:
            async with self:
                self.plan_pago_error = f"Error al cargar plan: {str(e)}"
                self.plan_pago_loading = False

    @rx.event(background=True)
    async def crear_plan_pago(self, form_data: dict):
        """Crea un nuevo plan de pago."""
        async with self:
            self.plan_pago_loading = True
            self.plan_pago_error = ""

        try:
            from src.aplicacion.servicios.servicio_plan_pago import (
                ServicioPlanPagoIncidente,
            )
            from src.infraestructura.persistencia.repositorio_plan_pago_postgres import (
                RepositorioPlanPagoPostgres,
            )
            from src.infraestructura.persistencia.repositorio_cuota_postgres import (
                RepositorioCuotaPostgres,
            )
            from src.infraestructura.persistencia.repositorio_incidentes_postgres import (
                RepositorioIncidentesPostgres,
            )
            from src.infraestructura.persistencia.repositorio_bloqueos import (
                RepositorioBloqueos,
            )

            repo_plan = RepositorioPlanPagoPostgres(db_manager)
            repo_cuota = RepositorioCuotaPostgres(db_manager)
            repo_incidentes = RepositorioIncidentesPostgres(db_manager)
            repo_bloqueos = RepositorioBloqueos(db_manager)

            servicio = ServicioPlanPagoIncidente(
                repo_plan, repo_cuota, repo_incidentes, repo_bloqueos
            )

            usuario = await obtener_usuario_actual_async()
            num_cuotas = form_data.get("num_cuotas", self.plan_pago_num_cuotas)
            valor_cuota = form_data.get("valor_cuota", self.plan_pago_valor_cuota)

            resultado = servicio.crear_plan(
                id_incidente=self.plan_pago_incidente_id,
                num_cuotas=int(num_cuotas),
                valor_cuota=int(valor_cuota),
                creado_por=usuario,
            )

            async with self:
                if resultado.get("success"):
                    self.plan_pago_data = resultado["data"]["plan"]
                    self.plan_pago_cuotas = resultado["data"]["cuotas"]
                    self.show_plan_pago_modal = False
                    yield IncidentesState.load_incidentes()
                else:
                    self.plan_pago_error = resultado.get(
                        "message", "Error al crear plan de pago"
                    )
                self.plan_pago_loading = False

        except Exception as e:
            async with self:
                self.plan_pago_error = f"Error al crear plan: {str(e)}"
                self.plan_pago_loading = False

    def close_plan_pago_modal(self):
        """Cierra el modal de plan de pago."""
        self.show_plan_pago_modal = False
        self.plan_pago_incidente_id = None
        self.plan_pago_data = {}
        self.plan_pago_cuotas = []
        self.plan_pago_error = ""

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

    @rx.event(background=True)
    async def on_load(self):
        """Carga inicial."""
        async with self:
            self.is_loading = True

        try:
            yield IncidentesState.load_incidentes()
            yield IncidentesState.load_propiedades()
            yield IncidentesState.load_proveedores()
            yield IncidentesState.load_estados_pago()
        finally:
            async with self:
                self.is_loading = False

    @rx.event(background=True)
    async def load_estados_pago(self):
        """Carga lista de estados de pago disponibles."""
        try:
            servicio = ServicioIncidentes(db_manager)
            estados = servicio.obtener_estados_pago()
            options = ["Todos"] + estados
            async with self:
                self.estados_pago_options = options
        except Exception as e:
            print(f"Error cargando estados de pago: {e}")

    @rx.event(background=True)
    async def load_propiedades(self):
        """Carga lista de propiedades para el select."""
        try:
            from src.aplicacion.servicios.servicio_propiedades import (
                ServicioPropiedades,
            )
            from src.infraestructura.persistencia.repositorio_propiedad_postgres import (
                RepositorioPropiedadPostgres,
            )

            repo_prop = RepositorioPropiedadPostgres(db_manager)
            servicio = ServicioPropiedades(repo_prop)
            props = servicio.listar_propiedades()

            options = [
                {"id": str(p.id_propiedad), "texto": p.direccion_propiedad}
                for p in props
            ]
            async with self:
                self.propiedades_options = options
        except Exception as e:
            print(f"Error cargando propiedades: {e}")

    @rx.event(background=True)
    async def load_incidentes(self):
        """Carga lista de incidentes y actualiza vistas optimizadamente."""
        import logging

        _log = logging.getLogger("IncidentesState")

        async with self:
            self.is_loading = True
            self.error_message = ""

        try:
            servicio = ServicioIncidentes(db_manager)

            # Filtros para el servicio
            prioridad = (
                self.filter_prioridad if self.filter_prioridad != "Todas" else None
            )
            estado = self.filter_estado if self.filter_estado != "Todos" else None
            estado_pago = self.filter_estado_pago if self.filter_estado_pago and self.filter_estado_pago != "Todos" else None

            # Pagination server-side enforced (US1) to prevent websocket crashes
            pagina = self.page
            tamano_pagina = self.items_per_page

            resultado = servicio.listar_con_filtros(
                busqueda=self.search_text if self.search_text else None,
                prioridad=prioridad,
                estado=estado,
                estado_pago=estado_pago,
                page=pagina,
                page_size=tamano_pagina,
            )

            resultado_objs = resultado["items"]
            total_items = resultado["total"]

            # Serializar (SIN N+1: La data de relaciones ya viene en el objeto Incidente)
            items = []
            kanban_grouped = {k: [] for k in self.kanban_columns.keys()}

            for inc in resultado_objs:
                # Formatear fechas
                fecha_arreglo_str = None
                if inc.fecha_arreglo:
                    if hasattr(inc.fecha_arreglo, "strftime"):
                        fecha_arreglo_str = inc.fecha_arreglo.strftime("%Y-%m-%d")
                    elif isinstance(inc.fecha_arreglo, str):
                        fecha_arreglo_str = inc.fecha_arreglo.split(" ")[0]

                item = {
                    "id": inc.id_incidente,
                    "descripcion": inc.descripcion_incidente,
                    "estado": inc.estado,
                    "prioridad": inc.prioridad,
                    "fecha": (
                        inc.fecha_incidente.strftime("%Y-%m-%d")
                        if hasattr(inc.fecha_incidente, "strftime")
                        else str(inc.fecha_incidente)[:10]
                    ),
                    "id_propiedad": inc.id_propiedad,
                    "direccion_propiedad": inc.direccion_propiedad
                    or f"#{inc.id_propiedad}",
                    "id_proveedor": inc.id_proveedor_asignado,
                    "origen": inc.origen_reporte or "Inquilino",
                    "nombre_propietario": inc.nombre_propietario or "N/D",
                    "nombre_inquilino": inc.nombre_inquilino or "N/D",
                    "nombre_habitante": inc.nombre_habitante or "N/D",
                    "telefono_propietario": inc.telefono_propietario or "",
                    "telefono_inquilino": inc.telefono_inquilino or "",
                    "telefono_habitante": inc.telefono_habitante or "",
                    "costo_incidente": inc.costo_incidente,
                    "fecha_arreglo": fecha_arreglo_str,
                    "nombre_proveedor": inc.nombre_proveedor,
                    "cotizaciones_resumen": inc.cotizaciones_resumen or [],
                    "estado_pago": getattr(inc, "estado_pago", "Pendiente"),
                    "plan_pago": getattr(inc, "plan_pago", None),
                }
                incidente_dict_obj = IncidenteDict(**item)
                items.append(incidente_dict_obj)

                # Agrupar para Kanban
                for col_name, status_list in self.kanban_columns.items():
                    if inc.estado in status_list:
                        kanban_grouped[col_name].append(incidente_dict_obj)
                        break

            async with self:
                self.incidentes = items
                self.incidentes_kanban = kanban_grouped

                import math

                self.total_pages = math.ceil(total_items / self.items_per_page)
                if self.total_pages < 1:
                    self.total_pages = 1

                _log.info(
                    "load_incidentes: cargados=%d, total=%d, kanban=%s",
                    len(items),
                    total_items,
                    {k: len(v) for k, v in kanban_grouped.items()},
                )

        except Exception as e:
            _log.exception("Error crítico en load_incidentes")
            async with self:
                self.error_message = f"Error al cargar incidentes: {str(e)}"
                self.incidentes = []
        finally:
            async with self:
                self.is_loading = False

    @rx.event(background=True)
    async def load_proveedores(self):
        """Carga lista de proveedores."""
        try:
            from src.aplicacion.servicios.servicio_proveedores import (
                ServicioProveedores,
            )

            servicio = ServicioProveedores(db_manager)
            proveedores = servicio.listar_proveedores()

            options = [
                {
                    "id": str(p.id_proveedor),
                    "texto": f"{p.nombre_completo or 'Proveedor'} ({p.especialidad})",
                }
                for p in proveedores
                if p.estado_registro
            ]

            async with self:
                self.proveedores_options = options

        except Exception:
            pass  # print(f"Error cargando proveedores: {e}") [OpSec Removed]

    def toggle_view_mode(self):
        """Alterna entre vista lista y kanban y recarga datos."""
        self.view_mode = "list" if self.view_mode == "kanban" else "kanban"
        self.page = 1
        return IncidentesState.load_incidentes

    def set_filter_estado(self, value: str):
        self.filter_estado = value
        return IncidentesState.load_incidentes

    def set_filter_estado_pago(self, value: str):
        self.filter_estado_pago = value
        self.page = 1
        return IncidentesState.load_incidentes

    def set_filter_prioridad(self, value: str):
        self.filter_prioridad = value
        return IncidentesState.load_incidentes

    def set_search(self, value: str):
        self.search_text = value
        self.page = 1
        return IncidentesState.load_incidentes

    def toggle_sort(self, column: str):
        """Alterna el ordenamiento por columna."""
        if self.sort_by == column:
            self.sort_order = "asc" if self.sort_order == "desc" else "desc"
        else:
            self.sort_by = column
            self.sort_order = "desc"
        self.page = 1
        return IncidentesState.load_incidentes

    # --- CRUD ---
    def open_create_modal(self):
        self.modal_open = True
        from datetime import datetime

        self.form_data = {
            "id_propiedad": "",
            "descripcion": "",
            "prioridad": "Media",
            "origen_reporte": "Inquilino",
            "fecha_incidente": datetime.now().strftime("%Y-%m-%d"),
            "responsable_pago": "Inquilino",
        }
        self.propiedad_search = ""
        self.propiedad_selected_label = ""
        self.propiedad_menu_open = False

    def close_modal(self):
        self.modal_open = False

    def set_form_data(self, key: str, value: Any):
        self.form_data[key] = value

    def set_id_propiedad(self, value: str):
        self.form_data["id_propiedad"] = value

    def set_descripcion(self, value: str):
        self.form_data["descripcion"] = value

    def set_prioridad(self, value: str):
        self.form_data["prioridad"] = value

    def set_origen_reporte(self, value: str):
        self.form_data["origen_reporte"] = value

    def set_fecha_incidente(self, value: str):
        self.form_data["fecha_incidente"] = value

    def set_responsable_pago(self, value: str):
        self.form_data["responsable_pago"] = value

    # --- DETAILS & QUOTING ACTIONS ---

    @rx.event(background=True)
    @rx.event(background=True)
    async def select_incidente(self, incidente: Dict[str, Any]):
        """Selecciona un incidente y carga sus detalles completos."""
        async with self:
            # Inicializar con ID mientras carga
            incidente["direccion_propiedad"] = (
                f"#{incidente.get('id_propiedad', '')}..."
            )
            self.selected_incidente = incidente
            self.details_modal_open = True
            self.show_quote_form = False
            self.error_message = ""
            self.is_loading = True

            # Configurar identidad de documentos
            self.iniciar_contexto_documental("INCIDENTE", str(incidente["id"]))

        try:
            servicio = ServicioIncidentes(db_manager)
            detalle = servicio.obtener_detalle(incidente["id"])

            cotizaciones_data = []
            if detail_cots := detalle.get("cotizaciones"):
                # Serializar cotizaciones
                for cot in detail_cots:
                    # Obtener nombre proveedor si es posible
                    nombre_prov = "Proveedor"
                    if cot.id_proveedor:
                        # Buscamos en opciones cargadas o servicio
                        prov_opt = next(
                            (
                                p
                                for p in self.proveedores_options
                                if p["id"] == str(cot.id_proveedor)
                            ),
                            None,
                        )
                        if prov_opt:
                            nombre_prov = prov_opt["texto"]

                    cotizaciones_data.append(
                        {
                            "id": cot.id_cotizacion,
                            "proveedor": nombre_prov,
                            "valor_total": cot.valor_total,
                            "materiales": cot.valor_materiales,
                            "mano_obra": cot.valor_mano_obra,
                            "dias": cot.dias_estimados,
                            "descripcion": cot.descripcion_trabajo,
                            "estado": cot.estado_cotizacion,
                        }
                    )

            # Obtener historial para buscar observaciones de finalización
            historial = servicio.obtener_historial(incidente["id"])
            observacion_final = ""
            for h in historial:
                if h.estado_nuevo == "Finalizado":
                    observacion_final = h.comentario
                    break

            async with self:
                current_inc = self.selected_incidente.copy()

                # Actualizar datos del incidente completo
                inc_obj = detalle["incidente"]
                current_inc["estado"] = inc_obj.estado
                current_inc["prioridad"] = inc_obj.prioridad
                current_inc["costo_incidente"] = inc_obj.costo_incidente
                current_inc["estado_pago"] = getattr(
                    inc_obj, "estado_pago", "Pendiente"
                )

                # Manejo robusto de fecha_arreglo (str o datetime)
                fecha_val = inc_obj.fecha_arreglo
                if hasattr(fecha_val, "strftime"):
                    current_inc["fecha_arreglo"] = fecha_val.strftime("%Y-%m-%d")
                elif isinstance(fecha_val, str):
                    # Si viene como string 'YYYY-MM-DD HH:MM:SS', tomar solo fecha
                    current_inc["fecha_arreglo"] = fecha_val.split(" ")[0]
                else:
                    current_inc["fecha_arreglo"] = "N/A"

                current_inc["observaciones_final"] = observacion_final

                # Actualizar dirección si existe propiedad
                if prop := detalle.get("propiedad"):
                    current_inc["direccion_propiedad"] = getattr(
                        prop, "direccion_propiedad", str(prop)
                    )

                # Nombre del propietario (ya viene del servicio)
                current_inc["nombre_propietario"] = detalle.get(
                    "nombre_propietario", "N/D"
                )

                # Actualizar nombre proveedor si existe
                current_inc["nombre_proveedor"] = "Proveedor No Asignado"
                if (
                    pid := inc_obj.id_proveedor_asignado
                ):  # Usar del objeto real, mas seguro
                    # Buscar en opciones (formato id, texto)
                    prov_opt = next(
                        (p for p in self.proveedores_options if p["id"] == str(pid)),
                        None,
                    )
                    if prov_opt:
                        current_inc["nombre_proveedor"] = prov_opt["texto"]

                self.selected_incidente = current_inc
                self.cotizaciones = cotizaciones_data

        except Exception:
            pass  # print(f"Error cargando detalle incidente: {e}") [OpSec Removed]
            # Fallback a datos básicos si falla
            async with self:
                self.cotizaciones = []
        finally:
            async with self:
                self.is_loading = False

    def close_details_modal(self):
        self.details_modal_open = False
        self.selected_incidente = {}

    def toggle_quote_form(self):
        self.show_quote_form = not self.show_quote_form

    def set_cotizacion_field(self, key: str, value: Any):
        self.cotizacion_form[key] = value

    @rx.event(background=True)
    async def save_cotizacion(self):
        async with self:
            self.is_loading = True

        try:
            servicio = ServicioIncidentes(db_manager)
            usuario = obtener_usuario_actual()

            # Prepare data
            datos = {
                "id_proveedor": int(self.cotizacion_form["id_proveedor"]),
                "materiales": float(self.cotizacion_form["materiales"]),
                "mano_obra": float(self.cotizacion_form["mano_obra"]),
                "descripcion": self.cotizacion_form["descripcion"],
                "dias": int(self.cotizacion_form["dias"]),
            }

            id_incidente = self.selected_incidente["id"]

            servicio.registrar_cotizacion(id_incidente, datos, usuario)

            yield rx.toast.success("Cotización registrada exitosamente.")

            # Ocultar formulario pero MANTENER modal abierto
            async with self:
                self.show_quote_form = False

            # Recargar lista general
            yield IncidentesState.load_incidentes()

            # Recargar detalles del incidente actual (cotizaciones)
            yield IncidentesState.select_incidente(self.selected_incidente)

        except Exception as e:
            yield rx.toast.error(f"Error al registrar cotización: {str(e)}")
        finally:
            async with self:
                self.is_loading = False

    @rx.event(background=True)
    async def save_incidente(self):
        async with self:
            self.is_loading = True
            self.error_message = ""

        try:
            servicio = ServicioIncidentes(db_manager)
            usuario = (
                "sistema"  # TODO: Implementar obtener_usuario_desde_state  # TODO Auth
            )

            # Validación básica
            if not self.form_data["id_propiedad"] or not self.form_data["descripcion"]:
                raise ValueError("Propiedad y Descripción son obligatorias")

            datos = {
                "id_propiedad": int(self.form_data["id_propiedad"]),
                "id_contrato_m": None,
                "descripcion": self.form_data["descripcion"],
                "prioridad": self.form_data["prioridad"],
                "origen_reporte": self.form_data["origen_reporte"],
                "fecha_incidente": self.form_data["fecha_incidente"],
                "responsable_pago": self.form_data["responsable_pago"],
            }

            servicio.reportar_incidente(datos, usuario)

            async with self:
                self.modal_open = False

            yield IncidentesState.load_incidentes()

        finally:
            async with self:
                self.is_loading = False

    @rx.event(background=True)
    async def aprobar_cotizacion_event(self, id_incidente: int, id_cotizacion: int):
        """Aprueba una cotización y genera Orden de Trabajo."""
        async with self:
            self.is_loading = True

        try:
            servicio = ServicioIncidentes(db_manager)
            usuario = (
                "sistema"  # TODO: Implementar obtener_usuario_desde_state  # TODO Auth
            )
            # Asumimos 'Propietario' por defecto o requerir input extra
            servicio.aprobar_cotizacion(
                id_incidente, id_cotizacion, usuario, responsable_pago="Propietario"
            )

            yield rx.toast.success("Cotización aprobada y Orden de Trabajo creada.")

            async with self:
                if (
                    self.selected_incidente
                    and self.selected_incidente.get("id") == id_incidente
                ):
                    self.selected_incidente["estado"] = "Aprobado"

            yield IncidentesState.load_incidentes()
            if (
                self.selected_incidente
                and self.selected_incidente.get("id") == id_incidente
            ):
                yield IncidentesState.select_incidente(self.selected_incidente)

        except Exception as e:
            yield rx.toast.error(f"Error al aprobar: {str(e)}")
        finally:
            async with self:
                self.is_loading = False

    @rx.event(background=True)
    async def iniciar_reparacion_event(self, id_incidente: int):
        """Inicia la reparación."""
        async with self:
            self.is_loading = True

        try:
            servicio = ServicioIncidentes(db_manager)
            usuario = obtener_usuario_actual()
            servicio.iniciar_reparacion(id_incidente, usuario)

            yield rx.toast.success("Reparación iniciada.")

            async with self:
                if (
                    self.selected_incidente
                    and self.selected_incidente.get("id") == id_incidente
                ):
                    self.selected_incidente["estado"] = "En Reparacion"

            yield IncidentesState.load_incidentes()
            if (
                self.selected_incidente
                and self.selected_incidente.get("id") == id_incidente
            ):
                yield IncidentesState.select_incidente(self.selected_incidente)

        except Exception as e:
            yield rx.toast.error(f"Error al iniciar reparación: {str(e)}")
        finally:
            async with self:
                self.is_loading = False

    @rx.event(background=True)
    async def finalizar_incidente_event(self, id_incidente: int):
        """Finaliza el incidente."""
        async with self:
            self.is_loading = True

        try:
            servicio = ServicioIncidentes(db_manager)
            usuario = obtener_usuario_actual()
            servicio.finalizar_incidente(id_incidente, usuario)

            yield rx.toast.success("Incidente finalizado exitosamente.")

            async with self:
                if (
                    self.selected_incidente
                    and self.selected_incidente.get("id") == id_incidente
                ):
                    self.selected_incidente["estado"] = "Finalizado"

            yield IncidentesState.load_incidentes()
            if (
                self.selected_incidente
                and self.selected_incidente.get("id") == id_incidente
            ):
                yield IncidentesState.select_incidente(self.selected_incidente)

        except Exception as e:
            yield rx.toast.error(f"Error al finalizar: {str(e)}")
        finally:
            async with self:
                self.is_loading = False

    @rx.event(background=True)
    async def finalizar_carga_cotizaciones(self, id_incidente: int):
        """Finaliza la carga de cotizaciones y pasa a estado Cotizado."""
        async with self:
            self.is_loading = True

        try:
            servicio = ServicioIncidentes(db_manager)
            usuario = obtener_usuario_actual()
            servicio.cambiar_estado(id_incidente, "Cotizado", usuario)

            yield rx.toast.success(
                "Cotizaciones finalizadas. Incidente pasa a estado Cotizado para aprobación."
            )
            yield IncidentesState.load_incidentes()

            # Actualizar estado seleccionado localmente para reflejar cambio inmediato en UI
            async with self:
                if (
                    self.selected_incidente
                    and self.selected_incidente["id"] == id_incidente
                ):
                    self.selected_incidente["estado"] = "Cotizado"
                    self.details_modal_open = True

            if (
                self.selected_incidente
                and self.selected_incidente["id"] == id_incidente
            ):
                yield IncidentesState.select_incidente(self.selected_incidente)

        except Exception as e:
            yield rx.toast.error(f"Error al cambiar estado: {str(e)}")
        finally:
            async with self:
                self.is_loading = False

    @rx.event
    def toggle_finalize_form(self):
        """Alterna la visibilidad del formulario de finalización."""
        self.show_finalize_form = not self.show_finalize_form
        if self.show_finalize_form:
            # Prellenar fecha con hoy
            self.finalize_date = datetime.now().strftime("%Y-%m-%d")
            self.finalize_obs = ""

    @rx.event
    def set_finalize_date(self, value: str):
        self.finalize_date = value

    @rx.event
    def set_finalize_obs(self, value: str):
        self.finalize_obs = value

    @rx.event(background=True)
    async def confirmar_finalizacion(self):
        """Confirma la finalización del incidente con fecha y observaciones."""
        async with self:
            self.is_loading = True
            if not self.finalize_date:
                yield rx.toast.error("Debe ingresar una fecha de finalización.")
                self.is_loading = False
                return

        try:
            servicio = ServicioIncidentes(db_manager)
            usuario = obtener_usuario_actual()

            # Parsear fecha string a datetime
            fecha_fin = datetime.strptime(self.finalize_date, "%Y-%m-%d")

            # Pasar fecha y observación (comentario)
            servicio.finalizar_incidente(
                self.selected_incidente["id"],
                usuario,
                comentario=self.finalize_obs,
                fecha_arreglo=fecha_fin,
            )

            yield rx.toast.success("Incidente finalizado exitosamente.")
            yield IncidentesState.load_incidentes()

            async with self:
                self.show_finalize_form = False
                self.details_modal_open = False  # Cerrar modal al finalizar

        except Exception as e:
            yield rx.toast.error(f"Error al finalizar: {str(e)}")
        finally:
            async with self:
                self.is_loading = False

    @rx.event
    def prev_page(self):
        if self.page > 1:
            self.page -= 1
            return IncidentesState.load_incidentes

    @rx.event
    def next_page(self):
        if self.page < self.total_pages:
            self.page += 1
            return IncidentesState.load_incidentes

    @rx.event(background=True)
    async def generar_pdf_incidente(self):
        """Genera el PDF del incidente seleccionado.

        Estrategia CQRS lite: consulta directa a la DB para obtener datos
        frescos y completos, independientes del estado de la UI. Esto evita
        que fallos de carga de incidentes contamenen la generación del PDF.
        """
        import logging

        _log = logging.getLogger("IncidentesState")

        async with self:
            if not self.selected_incidente:
                yield rx.toast.error("No hay incidente seleccionado.")
                return
            self.is_loading = True

        incidente_id = self.selected_incidente.get("id")
        if not incidente_id:
            yield rx.toast.error("El incidente seleccionado no tiene un ID válido.")
            async with self:
                self.is_loading = False
            return

        try:
            # 1. Consulta fresca a la DB (CQRS lite) - datos aislados del UI state
            servicio = ServicioIncidentes(db_manager)
            detalle = servicio.obtener_detalle(incidente_id)

            if not detalle or not detalle.get("incidente"):
                _log.error("PDF: No se encontró incidente %s en DB", incidente_id)
                yield rx.toast.error("No se encontró el incidente en la base de datos.")
                return

            inc_obj = detalle["incidente"]
            propiedad = detalle.get("propiedad")
            cotizaciones_db = detalle.get("cotizaciones", [])

            # 2. Construir datos del PDF con mapeo explícito desde la entidad
            datos = {
                "id": inc_obj.id_incidente,
                "descripcion": inc_obj.descripcion_incidente,
                "estado": inc_obj.estado,
                "prioridad": inc_obj.prioridad,
                "fecha": (
                    inc_obj.fecha_incidente.strftime("%Y-%m-%d")
                    if hasattr(inc_obj.fecha_incidente, "strftime")
                    else str(inc_obj.fecha_incidente)[:10]
                ),
                "id_propiedad": inc_obj.id_propiedad,
                "direccion": (
                    getattr(
                        propiedad, "direccion_propiedad", f"#{inc_obj.id_propiedad}"
                    )
                    if propiedad
                    else f"#{inc_obj.id_propiedad}"
                ),
                "origen_reporte": inc_obj.origen_reporte or "Inquilino",
                "responsable_pago": inc_obj.responsable_pago or "Por definir",
                "nombre_propietario": inc_obj.nombre_propietario or "N/D",
                "nombre_proveedor": inc_obj.nombre_proveedor or "No Asignado",
                "costo_incidente": inc_obj.costo_incidente,
                "fecha_arreglo": (
                    inc_obj.fecha_arreglo.strftime("%Y-%m-%d")
                    if inc_obj.fecha_arreglo
                    and hasattr(inc_obj.fecha_arreglo, "strftime")
                    else (
                        str(inc_obj.fecha_arreglo).split(" ")[0]
                        if inc_obj.fecha_arreglo
                        else None
                    )
                ),
                "cotizaciones": [],
                "fecha_reporte": (
                    inc_obj.fecha_incidente.strftime("%Y-%m-%d")
                    if hasattr(inc_obj.fecha_incidente, "strftime")
                    else str(inc_obj.fecha_incidente)[:10]
                ),
            }

            # 3. Mapear cotizaciones con nombre de proveedor
            for cot in cotizaciones_db:
                nombre_prov = "Proveedor"
                if cot.id_proveedor:
                    prov_opt = next(
                        (
                            p
                            for p in self.proveedores_options
                            if p["id"] == str(cot.id_proveedor)
                        ),
                        None,
                    )
                    if prov_opt:
                        nombre_prov = prov_opt["texto"]
                datos["cotizaciones"].append(
                    {
                        "proveedor": nombre_prov,
                        "descripcion": cot.descripcion_trabajo or "",
                        "dias": cot.dias_estimados,
                        "mano_obra": cot.valor_mano_obra,
                        "materiales": cot.valor_materiales,
                        "valor_total": cot.valor_total,
                        "estado": cot.estado_cotizacion,
                    }
                )

            # 4. Obtener observaciones de finalización desde historial
            historial = servicio.obtener_historial(incidente_id)
            for h in historial:
                if h.estado_nuevo == "Finalizado" and h.comentario:
                    datos["observaciones_final"] = h.comentario
                    break

            # 5. Configuración empresa
            servicio_config = ServicioConfiguracion(db_manager)
            config_empresa = servicio_config.obtener_configuracion_empresa()
            if config_empresa:
                datos["empresa"] = {
                    "logo_base64": config_empresa.logo_base64,
                    "nombre": config_empresa.nombre_empresa,
                }

            _log.info(
                "PDF generado para incidente %s (estado=%s, cotizaciones=%d)",
                incidente_id,
                inc_obj.estado,
                len(datos["cotizaciones"]),
            )

            # 6. Generar PDF
            template = IncidenteTemplateElite(output_dir=Path("documentos_generados"))
            pdf_path = template.generate(datos)

            yield rx.toast.success("PDF generado exitosamente.")

            # 7. Descargar
            pdf_filename = Path(pdf_path).name
            download_url = f"{config.api_url}/api/pdf/download/{pdf_filename}"

            js_download = f"""
            fetch('{download_url}', {{ credentials: 'include' }})
              .then(res => {{ 
                  if (!res.ok) throw new Error('Error en descarga: ' + res.statusText); 
                  const contentType = res.headers.get('content-type'); 
                  if (contentType && contentType.includes('text/html')) throw new Error('Sesión expirada.'); 
                  return res.blob(); 
              }})
              .then(blob => {{
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = '{pdf_filename}';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
              }})
              .catch(err => console.error('Download error:', err));
            """
            yield rx.call_script(js_download)

        except Exception as e:
            _log.exception("Error generando PDF para incidente %s", incidente_id)
            yield rx.toast.error(f"Error generando PDF: {str(e)}")
        finally:
            async with self:
                self.is_loading = False

    # === EDIT METHODS ===
    @rx.event
    def open_edit_modal(self, incidente: Dict[str, Any]):
        self.edit_modal_open = True
        self.editing_incidente = incidente
        self.edit_form_data = {
            "descripcion": incidente.get("descripcion", ""),
            "prioridad": incidente.get("prioridad", "Media"),
            "origen_reporte": incidente.get("origen", "Inquilino"),
            "responsable_pago": "Inquilino",
            "costo_incidente": float(incidente.get("costo_incidente", 0) or 0),
            "id_proveedor_asignado": incidente.get("id_proveedor"),
        }
        self.edit_error = ""

    @rx.event
    def set_edit_modal_open(self, value: bool):
        self.edit_modal_open = value

    @rx.event
    def close_edit_modal(self):
        self.edit_modal_open = False
        self.editing_incidente = {}
        self.edit_form_data = {
            "descripcion": "",
            "prioridad": "Media",
            "origen_reporte": "Inquilino",
            "responsable_pago": "Inquilino",
            "costo_incidente": 0,
            "id_proveedor_asignado": None,
        }
        self.edit_error = ""

    @rx.event
    def set_edit_field(self, key: str, value: Any):
        self.edit_form_data[key] = value

    @rx.event(background=True)
    async def save_edit_incidente(self):
        async with self:
            self.is_loading = True
            self.edit_error = ""

        try:
            if not self.editing_incidente:
                raise ValueError("No hay incidente seleccionado para editar")

            servicio = ServicioIncidentes(db_manager)
            usuario = obtener_usuario_actual()

            id_incidente = self.editing_incidente["id"]

            datos_actualizacion = {}
            if self.edit_form_data.get("descripcion"):
                datos_actualizacion["descripcion_incidente"] = self.edit_form_data[
                    "descripcion"
                ]
            if self.edit_form_data.get("prioridad"):
                datos_actualizacion["prioridad"] = self.edit_form_data["prioridad"]
            if self.edit_form_data.get("origen_reporte"):
                datos_actualizacion["origen_reporte"] = self.edit_form_data[
                    "origen_reporte"
                ]
            if self.edit_form_data.get("responsable_pago"):
                datos_actualizacion["responsable_pago"] = self.edit_form_data[
                    "responsable_pago"
                ]
            if self.edit_form_data.get("costo_incidente"):
                datos_actualizacion["costo_incidente"] = int(
                    self.edit_form_data["costo_incidente"]
                )
            if self.edit_form_data.get("id_proveedor_asignado"):
                datos_actualizacion["id_proveedor_asignado"] = self.edit_form_data[
                    "id_proveedor_asignado"
                ]

            servicio.editar_incidente(id_incidente, datos_actualizacion, usuario)

            yield rx.toast.success("Incidente actualizado exitosamente.")

            async with self:
                self.edit_modal_open = False

            yield IncidentesState.load_incidentes()
            if (
                self.selected_incidente
                and self.selected_incidente.get("id") == id_incidente
            ):
                yield IncidentesState.select_incidente(self.selected_incidente)

        except Exception as e:
            yield rx.toast.error(f"Error al editar incidente: {str(e)}")
            async with self:
                self.edit_error = str(e)
        finally:
            async with self:
                self.is_loading = False

    # === CANCEL METHODS ===
    @rx.event
    def open_cancel_modal(self, incidente: Dict[str, Any]):
        self.cancel_modal_open = True
        self.cancel_incidente = incidente
        self.cancel_motivo = ""
        self.cancel_error = ""

    @rx.event
    def close_cancel_modal(self):
        self.cancel_modal_open = False
        self.cancel_incidente = {}
        self.cancel_motivo = ""
        self.cancel_error = ""

    @rx.event
    def set_cancel_motivo(self, value: str):
        self.cancel_motivo = value
        self.cancel_error = ""

    @rx.event(background=True)
    async def confirmar_cancelacion(self):
        async with self:
            self.is_loading = True
            self.cancel_error = ""

        if not self.cancel_motivo or not self.cancel_motivo.strip():
            yield rx.toast.error("Debe ingresar un motivo para cancelar")
            async with self:
                self.cancel_error = "El motivo es obligatorio"
                self.is_loading = False
            return

        try:
            if not self.cancel_incidente:
                raise ValueError("No hay incidente seleccionado para cancelar")

            servicio = ServicioIncidentes(db_manager)
            usuario = obtener_usuario_actual()

            id_incidente = self.cancel_incidente["id"]
            estado_actual = self.cancel_incidente.get("estado", "")

            if estado_actual in ["Finalizado", "Cancelado"]:
                raise ValueError(
                    f"No se puede cancelar un incidente en estado {estado_actual}"
                )

            servicio.cancelar_incidente(
                id_incidente, usuario, self.cancel_motivo.strip()
            )

            yield rx.toast.success("Incidente cancelado exitosamente.")

            async with self:
                self.cancel_modal_open = False
                self.details_modal_open = False

            yield IncidentesState.load_incidentes()

        except Exception as e:
            yield rx.toast.error(f"Error al cancelar incidente: {str(e)}")
            async with self:
                self.cancel_error = str(e)
        finally:
            async with self:
                self.is_loading = False

    # === DIRECT FINISH METHODS ===
    @rx.event
    def toggle_direct_finish_form(self):
        self.show_direct_finish_form = not self.show_direct_finish_form
        if self.show_direct_finish_form:
            self.direct_finish_date = datetime.now().strftime("%Y-%m-%d")
            self.direct_finish_obs = ""
            self.direct_finish_costo = 0
            self.direct_finish_proveedor = None
            self.direct_finish_error = ""

    @rx.event
    def set_direct_finish_field(self, key: str, value: Any):
        if key == "fecha":
            self.direct_finish_date = value
        elif key == "observacion":
            self.direct_finish_obs = value
        elif key == "costo":
            self.direct_finish_costo = int(value) if value else 0
        elif key == "proveedor":
            self.direct_finish_proveedor = value

    @rx.event(background=True)
    async def confirmar_finalizacion_directa(self):
        async with self:
            self.is_loading = True
            self.direct_finish_error = ""

        try:
            if not self.selected_incidente:
                raise ValueError("No hay incidente seleccionado")

            servicio = ServicioIncidentes(db_manager)
            usuario = obtener_usuario_actual()

            id_incidente = self.selected_incidente["id"]
            estado_actual = self.selected_incidente.get("estado", "")

            if estado_actual in ["Finalizado", "Cancelado"]:
                raise ValueError(
                    f"No se puede finalizar un incidente en estado {estado_actual}"
                )

            # Preparar datos
            costo_final = self.direct_finish_costo if self.direct_finish_costo else None
            comentario = (
                self.direct_finish_obs if self.direct_finish_obs.strip() else None
            )
            fecha_fin = None

            if self.direct_finish_date:
                fecha_fin = datetime.strptime(self.direct_finish_date, "%Y-%m-%d")

            # Determinar si es finalización directa
            es_directo = estado_actual not in ["En Reparacion"]

            # Pasar proveedor directamente al método de finalización
            id_proveedor = (
                int(self.direct_finish_proveedor)
                if self.direct_finish_proveedor
                else None
            )

            servicio.finalizar_incidente(
                id_incidente=id_incidente,
                usuario_sistema=usuario,
                costo_final=costo_final,
                comentario=comentario,
                fecha_arreglo=fecha_fin,
                es_finalizacion_directa=es_directo,
                id_proveedor=id_proveedor,
            )

            yield rx.toast.success("Incidente finalizado exitosamente.")

            async with self:
                self.show_direct_finish_form = False

            yield IncidentesState.load_incidentes()
            if (
                self.selected_incidente
                and self.selected_incidente.get("id") == id_incidente
            ):
                yield IncidentesState.select_incidente(self.selected_incidente)

        except Exception as e:
            yield rx.toast.error(f"Error al finalizar incidente: {str(e)}")
            async with self:
                self.direct_finish_error = str(e)
        finally:
            async with self:
                self.is_loading = False
