import pydantic
from datetime import datetime
from typing import Any, Dict, List, Optional

import reflex as rx

from src.dominio.servicios.calculadora_contratos import CalculadoraContratos
from src.aplicacion.servicios.servicio_contratos import ServicioContratos
from src.infraestructura.persistencia.database import db_manager
from src.presentacion_reflex.state.documentos_mixin import DocumentosStateMixin


class ContratoDict(pydantic.BaseModel):
    """Estructura tipada para serialización de Contrato en Reflex."""

    id_contrato: int
    tipo_contrato: str
    estado_contrato: str
    propiedad_direccion: str
    propiedad_matricula: str
    propiedad_tipo: str
    propietario_nombre: str
    propietario_documento: str
    arrendatario_nombre: str
    arrendatario_documento: str
    habitante_nombre: str
    asesor_nombre: str
    fecha_inicio: str
    fecha_fin: str
    valor_canon: float
    valor_administracion: float
    fecha_pago: str = ""
    grupo_operativo: int = 0
    estado_cumplimiento: str = "PENDIENTE"  # AL_DIA, PENDIENTE, VENCIDO


class ContratosState(DocumentosStateMixin):
    """Estado para gestión de contratos (Mandatos y Arrendamientos).
    Maneja paginación, filtros y CRUD operations.
    """

    # Paginación
    current_page: int = 1
    page_size: int = 25
    total_items: int = 0

    # Datos
    contratos: List[ContratoDict] = []
    is_loading: bool = False
    error_message: str = ""
    is_grid_view: bool = False

    # KPIs
    kpi_mandatos_total: int = 0
    kpi_mandatos_activos: int = 0
    kpi_mandatos_inactivos: int = 0

    kpi_arriendos_total: int = 0
    kpi_arriendos_activos: int = 0
    kpi_arriendos_inactivos: int = 0

    # Búsqueda y Filtros
    search_text: str = ""
    filter_tipo: str = "Todos"
    filter_estado: str = "ACTIVO"
    filter_propiedad_id: str = ""
    filter_persona_id: str = ""
    filter_asesor_id: str = "todos"
    filter_sin_arrendamiento: bool = False

    # Ordenamiento
    sort_by: str = "direccion"
    sort_order: str = "desc"

    # Opciones de filtros
    tipo_options: List[str] = ["Todos", "Mandato", "Arrendamiento"]
    estado_options: List[str] = ["TODOS", "ACTIVO", "FINALIZADO", "CANCELADO", "LEGAL"]
    propiedades_options: List[Dict[str, Any]] = []
    personas_options: List[Dict[str, Any]] = []

    # Opciones para selects
    propiedades_select_options: List[List[str]] = []
    propietarios_select_options: List[List[str]] = []
    asesores_select_options: List[List[str]] = []
    personas_select_options: List[List[str]] = []
    propiedades_arriendo_select_options: List[List[str]] = []
    propiedades_mandato_libre_select_options: List[List[str]] = []
    arrendatarios_select_options: List[List[str]] = []
    codeudores_select_options: List[List[str]] = []

    # --- Searchable Selects State ---
    propiedad_search: str = ""
    propiedad_menu_open: bool = False
    propiedad_selected_label: str = ""

    propietario_search: str = ""
    propietario_menu_open: bool = False
    propietario_selected_label: str = ""

    asesor_search: str = ""
    asesor_menu_open: bool = False
    asesor_selected_label: str = ""

    arrendatario_search: str = ""
    arrendatario_menu_open: bool = False
    arrendatario_selected_label: str = ""

    codeudor_search: str = ""
    codeudor_menu_open: bool = False
    codeudor_selected_label: str = ""

    # Mapas de datos adicionales
    propiedades_canon_map: Dict[str, float] = {}

    # Modal CRUD
    modal_open: bool = False
    modal_mode: str = "crear_mandato"
    editing_id: Optional[int] = None
    form_data: Dict[str, Any] = {}

    # Modal Detalle
    show_detail_modal: bool = False
    contrato_detalle: Dict[str, Any] = {}

    # Renovacion
    show_renewal_confirm: bool = False
    renewal_loading_proyeccion: bool = False
    renewal_proyeccion: Dict[str, Any] = {}
    renewal_nueva_fecha_fin: str = ""
    renewal_target_id: int = 0
    renewal_target_tipo: str = ""

    # Modal IPC Increment
    show_ipc_modal: bool = False
    ipc_target_contrato_id: int = 0

    # --- Computed Filtered Options ---
    @rx.var
    def filtered_propiedades_options(self) -> List[List[str]]:
        """Opciones de propiedades filtradas por búsqueda y modo de modal (creación vs edición)."""
        s = self.propiedad_search.lower()
        options = []

        # Selección de base de opciones según el modo del modal
        if self.modal_mode == "crear_arrendamiento":
            options = self.propiedades_arriendo_select_options
        elif self.modal_mode == "editar_arrendamiento":
            # Incluir disponibles + la propiedad actual del contrato que se edita
            options = list(self.propiedades_arriendo_select_options)
            current_id = self.form_data.get("id_propiedad")
            if current_id and not any(opt[1] == str(current_id) for opt in options):
                for opt in self.propiedades_select_options:
                    if opt[1] == str(current_id):
                        options.append(opt)
                        break
        elif self.modal_mode == "crear_mandato":
            options = self.propiedades_mandato_libre_select_options
        elif self.modal_mode == "editar_mandato":
            # Incluir propiedades sin mandato + la propiedad actual del contrato
            options = list(self.propiedades_mandato_libre_select_options)
            current_id = self.form_data.get("id_propiedad")
            if current_id and not any(opt[1] == str(current_id) for opt in options):
                for opt in self.propiedades_select_options:
                    if opt[1] == str(current_id):
                        options.append(opt)
                        break
        else:
            options = self.propiedades_select_options

        if not s:
            return options
        return [opt for opt in options if s in opt[0].lower()]

    @rx.var
    def filtered_propietarios_options(self) -> List[List[str]]:
        s = self.propietario_search.lower()
        if not s:
            return self.propietarios_select_options
        return [opt for opt in self.propietarios_select_options if s in opt[0].lower()]

    @rx.var
    def filtered_asesores_options(self) -> List[List[str]]:
        s = self.asesor_search.lower()
        if not s:
            return self.asesores_select_options
        return [opt for opt in self.asesores_select_options if s in opt[0].lower()]

    @rx.var
    def filtered_arrendatarios_options(self) -> List[List[str]]:
        s = self.arrendatario_search.lower()
        if not s:
            return self.arrendatarios_select_options
        return [opt for opt in self.arrendatarios_select_options if s in opt[0].lower()]

    @rx.var
    def filtered_codeudores_options(self) -> List[List[str]]:
        s = self.codeudor_search.lower()
        if not s:
            return self.codeudores_select_options
        return [opt for opt in self.codeudores_select_options if s in opt[0].lower()]

    # --- Searchable Select Handlers ---
    def set_propiedad_search(self, value: str):
        self.propiedad_search = value

    def toggle_propiedad_menu(self, open: bool):
        self.propiedad_menu_open = open

    def select_propiedad(self, value: str, label: str):
        self.propiedad_selected_label = label
        self.form_data["id_propiedad"] = value
        self.propiedad_menu_open = False
        if self.modal_mode in ["crear_mandato", "editar_mandato"]:
            self.on_change_propiedad(value)
        else:
            self.on_change_propiedad_arriendo(value)

    def set_propietario_search(self, value: str):
        self.propietario_search = value

    def toggle_propietario_menu(self, open: bool):
        self.propietario_menu_open = open

    def select_propietario(self, value: str, label: str):
        self.propietario_selected_label = label
        self.form_data["id_propietario"] = value
        self.propietario_menu_open = False

    def set_asesor_search(self, value: str):
        self.asesor_search = value

    def toggle_asesor_menu(self, open: bool):
        self.asesor_menu_open = open

    def select_asesor(self, value: str, label: str):
        self.asesor_selected_label = label
        self.form_data["id_asesor"] = value
        self.asesor_menu_open = False

    def set_arrendatario_search(self, value: str):
        self.arrendatario_search = value

    def toggle_arrendatario_menu(self, open: bool):
        self.arrendatario_menu_open = open

    def select_arrendatario(self, value: str, label: str):
        self.arrendatario_selected_label = label
        self.form_data["id_arrendatario"] = value
        self.arrendatario_menu_open = False

    def set_codeudor_search(self, value: str):
        self.codeudor_search = value

    def toggle_codeudor_menu(self, open: bool):
        self.codeudor_menu_open = open

    def select_codeudor(self, value: str, label: str):
        self.codeudor_selected_label = label
        self.form_data["id_codeudor"] = value
        self.codeudor_menu_open = False

    def set_form_field(self, name: str, value: Any):
        self.form_data[name] = value

    @rx.var
    def asesores_filter_options(self) -> List[List[str]]:
        return [["Todos los Asesores", "todos"]] + self.asesores_select_options

    def set_search(self, value: str):
        self.search_text = value
        self.current_page = 1

    def toggle_sort(self, column: str):
        """Alterna el ordenamiento por columna."""
        if self.sort_by == column:
            self.sort_order = "asc" if self.sort_order == "desc" else "desc"
        else:
            self.sort_by = column
            self.sort_order = "desc"
        self.current_page = 1
        return ContratosState.load_contratos

    def _traducir_sort_by(self, sort_by: str, tipo_repo: str) -> str:
        """Traduce clave neutra UI a clave de BD según tipo de repositorio."""
        mapeo = {
            "id_contrato": {
                "mandato": "ID_CONTRATO_M",
                "arrendamiento": "ID_CONTRATO_A",
            },
            "direccion": {
                "mandato": "DIRECCION",
                "arrendamiento": "DIRECCION",
            },
            "propietario_nombre": {
                "mandato": "PROPIETARIO",
                "arrendamiento": "PROPIETARIO",
            },
            "fecha_inicio": {
                "mandato": "FECHA_INICIO_CONTRATO_M",
                "arrendamiento": "FECHA_INICIO_CONTRATO_A",
            },
            "valor_canon": {
                "mandato": "CANON_MANDATO",
                "arrendamiento": "CANON_ARRENDAMIENTO",
            },
            "estado_contrato": {
                "mandato": "ESTADO_CONTRATO_M",
                "arrendamiento": "ESTADO_CONTRATO_A",
            },
            "tipo_contrato": {
                "mandato": "ESTADO_CONTRATO_M",
                "arrendamiento": "ESTADO_CONTRATO_A",
            },
        }
        return mapeo.get(sort_by, {}).get(tipo_repo, sort_by.upper())

    def set_filter_tipo(self, value: str):
        self.filter_tipo = value
        self.current_page = 1
        # Reset filtro sin_arrendamiento si tipo != Mandato
        if value != "Mandato":
            self.filter_sin_arrendamiento = False
        return ContratosState.load_contratos

    def set_filter_estado(self, value: str):
        self.filter_estado = value
        self.current_page = 1
        return ContratosState.load_contratos

    def set_filter_asesor_id(self, val: str):
        self.filter_asesor_id = val
        self.current_page = 1
        return [ContratosState.load_contratos, ContratosState.load_kpis]

    def set_filter_sin_arrendamiento(self, value: bool):
        """Activa/desactiva filtro de mandatos sin arrendamiento activo.
        Fuerza filter_tipo a 'Mandato' cuando se activa."""
        self.filter_sin_arrendamiento = value
        if value:
            self.filter_tipo = "Mandato"
        self.current_page = 1
        return ContratosState.load_contratos

    def toggle_view(self):
        self.is_grid_view = not self.is_grid_view

    def on_change_propiedad(self, id_propiedad: str):
        self.form_data["id_propiedad"] = id_propiedad
        if id_propiedad and id_propiedad in self.propiedades_canon_map:
            canon = self.propiedades_canon_map[id_propiedad]
            self.form_data["canon"] = str(int(canon))
        else:
            self.form_data["canon"] = ""

    def on_change_propiedad_arriendo(self, id_propiedad: str):
        self.form_data["id_propiedad"] = id_propiedad
        if id_propiedad and id_propiedad in self.propiedades_canon_map:
            canon = self.propiedades_canon_map[id_propiedad]
            self.form_data["canon"] = str(int(canon))
            self.form_data["deposito"] = str(int(canon * 0.5))
        else:
            self.form_data["canon"] = ""
            self.form_data["deposito"] = "0"

    def on_change_canon_arriendo(self, canon: str):
        self.form_data["canon"] = canon
        try:
            val_canon = float(canon) if canon else 0
            self.form_data["deposito"] = str(int(val_canon * 0.5))
        except ValueError:
            pass

    def _calcular_duracion(self):
        f_inicio = self.form_data.get("fecha_inicio")
        f_fin = self.form_data.get("fecha_fin")
        if f_inicio and f_fin:
            try:
                total_meses = CalculadoraContratos.calcular_duracion_meses(f_inicio, f_fin)
                self.form_data["duracion_meses"] = str(total_meses)
            except ValueError:
                pass

    def on_change_fecha_inicio(self, fecha: str):
        self.form_data["fecha_inicio"] = fecha
        self._calcular_duracion()

    def on_change_fecha_fin(self, fecha: str):
        self.form_data["fecha_fin"] = fecha
        self._calcular_duracion()

    @rx.event(background=True)
    async def on_load(self):
        async with self:
            self.is_loading = True
        try:
            yield ContratosState.load_filter_options()
            yield ContratosState.load_contratos()
            yield ContratosState.load_kpis()
        finally:
            async with self:
                self.is_loading = False

    @rx.event(background=True)
    async def load_kpis(self):
        from src.aplicacion.servicios.servicio_contratos import ServicioContratos
        from src.infraestructura.persistencia.repositorio_contrato_mandato_postgres import (
            RepositorioContratoMandatoPostgres,
        )
        from src.infraestructura.persistencia.repositorio_contrato_arrendamiento_postgres import (
            RepositorioContratoArrendamientoPostgres,
        )

        servicio = ServicioContratos(db_manager)
        kpis = servicio.obtener_kpis(self.filter_asesor_id)
        async with self:
            m = kpis.get("mandatos", {})
            self.kpi_mandatos_total = m.get("total", 0) or 0
            self.kpi_mandatos_activos = m.get("activos", 0) or 0
            self.kpi_mandatos_inactivos = m.get("inactivos", 0) or 0
            a = kpis.get("arriendos", {})
            self.kpi_arriendos_total = a.get("total", 0) or 0
            self.kpi_arriendos_activos = a.get("activos", 0) or 0
            self.kpi_arriendos_inactivos = a.get("inactivos", 0) or 0

    @rx.event(background=True)
    async def load_filter_options(self):
        from src.aplicacion.servicios.servicio_contratos import ServicioContratos
        from src.infraestructura.persistencia.repositorio_contrato_mandato_postgres import (
            RepositorioContratoMandatoPostgres,
        )
        from src.infraestructura.persistencia.repositorio_contrato_arrendamiento_postgres import (
            RepositorioContratoArrendamientoPostgres,
        )

        servicio = ServicioContratos(db_manager)
        ops = servicio.obtener_opciones_filtro()
        async with self:
            self.propiedades_select_options = ops["propiedades"]
            self.propiedades_canon_map = ops["canon_map"]
            self.propietarios_select_options = ops["propietarios"]
            self.asesores_select_options = ops["asesores"]
            self.personas_select_options = ops["personas"]
            self.propiedades_mandato_libre_select_options = ops["prop_sin_mandato"]
            self.propiedades_arriendo_select_options = ops["prop_sin_arriendo"]
            self.arrendatarios_select_options = ops.get("arrendatarios", [])
            self.codeudores_select_options = ops.get("codeudores", [])

    @rx.event(background=True)
    async def load_contratos(self):
        async with self:
            self.is_loading = True
            self.error_message = ""
        try:
            from src.infraestructura.persistencia.repositorio_contrato_mandato_postgres import (
                RepositorioContratoMandatoPostgres,
            )
            from src.infraestructura.persistencia.repositorio_contrato_arrendamiento_postgres import (
                RepositorioContratoArrendamientoPostgres,
            )
            from src.infraestructura.persistencia.repositorio_propiedad_postgres import (
                RepositorioPropiedadPostgres,
            )
            from src.infraestructura.persistencia.repositorio_renovacion_postgres import (
                RepositorioRenovacionPostgres,
            )
            from src.infraestructura.persistencia.repositorio_ipc_postgres import (
                RepositorioIPCPostgres,
            )
            from src.infraestructura.persistencia.repositorio_arrendatario_postgres import (
                RepositorioArrendatarioPostgres,
            )
            from src.infraestructura.persistencia.repositorio_codeudor_postgres import (
                RepositorioCodeudorPostgres,
            )

            servicio = ServicioContratos(db_manager)
            asesor_filter = (
                self.filter_asesor_id
                if self.filter_asesor_id and self.filter_asesor_id != "todos"
                else None
            )
            estado_filtro = (
                self.filter_estado if self.filter_estado != "TODOS" else None
            )

            # Traducir sort_by según el tipo de repositorio
            sort_by_mandato = self._traducir_sort_by(self.sort_by, "mandato")
            sort_by_arrendamiento = self._traducir_sort_by(
                self.sort_by, "arrendamiento"
            )

            kwargs_paginacion = {
                "page": self.current_page,
                "page_size": self.page_size,
                "estado": estado_filtro,
                "busqueda": self.search_text or None,
                "id_asesor": asesor_filter,
                "sort_by": sort_by_arrendamiento,
                "sort_order": self.sort_order,
            }

            # Parámetro exclusivo para mandatos
            kwargs_mandatos = {**kwargs_paginacion}
            kwargs_mandatos["sort_by"] = sort_by_mandato
            if self.filter_sin_arrendamiento:
                kwargs_mandatos["sin_arrendamiento"] = True

            if self.filter_tipo == "Mandato":
                res = servicio.listar_mandatos_paginado(**kwargs_mandatos)
                items = [
                    ContratoDict(tipo_contrato="Mandato", **item) for item in res.items
                ]
                total = res.total
            elif self.filter_tipo == "Arrendamiento":
                res = servicio.listar_arrendamientos_paginado(**kwargs_paginacion)
                items = [
                    ContratoDict(tipo_contrato="Arrendamiento", **item)
                    for item in res.items
                ]
                total = res.total
            else:
                res_m = servicio.listar_mandatos_paginado(**kwargs_mandatos)
                res_a = servicio.listar_arrendamientos_paginado(**kwargs_paginacion)
                items = [
                    ContratoDict(tipo_contrato="Mandato", **item)
                    for item in res_m.items
                ] + [
                    ContratoDict(tipo_contrato="Arrendamiento", **item)
                    for item in res_a.items
                ]
                total = res_m.total + res_a.total

            # Cargar cumplimiento (Excepción temporal SQLite hasta migrar liquidaciones/recaudos)
            from src.infraestructura.persistencia.repositorio_liquidacion_postgres import (
                RepositorioLiquidacionPostgres,
            )
            from src.infraestructura.persistencia.repositorio_recaudo import (
                RepositorioRecaudo,
            )
            from src.dominio.value_objects.estado_cumplimiento import (
                obtener_periodo_actual,
            )

            repo_liq = RepositorioLiquidacionPostgres(db_manager)
            repo_recaudo = RepositorioRecaudo(db_manager)
            periodo = obtener_periodo_actual()

            for it in items:
                try:
                    if it.tipo_contrato == "Mandato":
                        it.estado_cumplimiento = repo_liq.obtener_estado_pago_actual(
                            it.id_contrato, periodo
                        )
                    else:
                        it.estado_cumplimiento = (
                            repo_recaudo.obtener_estado_pago_actual(
                                it.id_contrato, periodo
                            )
                        )
                except:
                    it.estado_cumplimiento = "PENDIENTE"

            async with self:
                self.contratos = items
                self.total_items = total
                self.is_loading = False
        except Exception as e:
            async with self:
                self.error_message = f"Error: {e}"
                self.is_loading = False

    def next_page(self):
        if self.current_page * self.page_size < self.total_items:
            self.current_page += 1
            return ContratosState.load_contratos

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            return ContratosState.load_contratos

    def search_contratos(self):
        self.current_page = 1
        return ContratosState.load_contratos

    def handle_search_key_down(self, key: str):
        if key == "Enter":
            return self.search_contratos()

    def _get_label_by_id(self, options: List[List[str]], target_id: Any) -> str:
        """Helper para encontrar la etiqueta descriptiva dado un ID en las opciones."""
        if not target_id:
            return ""
        tid = str(target_id)
        for label, val in options:
            if str(val) == tid:
                return label
        return ""

    def open_create_mandato_modal(self):
        self.modal_mode = "crear_mandato"
        self.editing_id = None
        self.form_data = {
            "id_propiedad": "",
            "id_propietario": "",
            "id_asesor": "",
            "comision_porcentaje": 10,
            "iva_porcentaje": 19,
            "banco_propietario": "",
            "numero_cuenta_propietario": "",
            "tipo_cuenta": "Ahorros",
            "consignatario": "",
            "documento_consignatario": "",
        }
        self.propiedad_selected_label = ""
        self.propietario_selected_label = ""
        self.asesor_selected_label = ""
        self.propiedad_search = ""
        self.propietario_search = ""
        self.asesor_search = ""
        self.modal_open = True

    def open_create_arrendamiento_modal(self):
        self.modal_mode = "crear_arrendamiento"
        self.editing_id = None
        self.form_data = {"id_propiedad": "", "id_arrendatario": "", "id_codeudor": ""}
        self.propiedad_selected_label = ""
        self.arrendatario_selected_label = ""
        self.codeudor_selected_label = ""
        self.propiedad_search = ""
        self.arrendatario_search = ""
        self.codeudor_search = ""
        self.modal_open = True

    @rx.event(background=True)
    async def open_edit_modal(self, id_contrato: int, tipo: str):
        async with self:
            self.is_loading = True
        try:
            from src.infraestructura.persistencia.repositorio_contrato_mandato_postgres import (
                RepositorioContratoMandatoPostgres,
            )
            from src.infraestructura.persistencia.repositorio_contrato_arrendamiento_postgres import (
                RepositorioContratoArrendamientoPostgres,
            )
            from src.infraestructura.persistencia.repositorio_propiedad_postgres import (
                RepositorioPropiedadPostgres,
            )
            from src.infraestructura.persistencia.repositorio_arrendatario_postgres import (
                RepositorioArrendatarioPostgres,
            )
            from src.infraestructura.persistencia.repositorio_codeudor_postgres import (
                RepositorioCodeudorPostgres,
            )

            servicio = ServicioContratos(db_manager)

            if tipo == "Mandato":
                c = servicio.obtener_mandato_por_id(id_contrato)
                if c:
                    async with self:
                        self.modal_mode = "editar_mandato"
                        self.editing_id = id_contrato
                        # Normalización de porcentajes (Base 10000 -> Base 100)
                        comision = float(c.comision_porcentaje_contrato_m or 0) / 100.0
                        iva = float(c.iva_contrato_m or 0) / 100.0

                        self.form_data = {
                            "id_propiedad": str(c.id_propiedad),
                            "id_propietario": str(c.id_propietario),
                            "id_asesor": str(c.id_asesor),
                            "fecha_inicio": c.fecha_inicio_contrato_m,
                            "fecha_fin": c.fecha_fin_contrato_m,
                            "duracion_meses": str(c.duracion_contrato_m),
                            "canon": str(c.canon_mandato),
                            "fecha_pago": c.fecha_pago or "",
                            "comision_porcentaje": comision,
                            "iva_porcentaje": iva,
                            "banco_propietario": c.banco_propietario or "",
                            "numero_cuenta_propietario": c.numero_cuenta_propietario or "",
                            "tipo_cuenta": c.tipo_cuenta or "Ahorros",
                            "consignatario": c.consignatario or "",
                            "documento_consignatario": c.documento_consignatario or "",
                        }
                        # Rehidratación de etiquetas
                        self.propiedad_selected_label = self._get_label_by_id(
                            self.propiedades_select_options, c.id_propiedad
                        )
                        self.propietario_selected_label = self._get_label_by_id(
                            self.propietarios_select_options, c.id_propietario
                        )
                        self.asesor_selected_label = self._get_label_by_id(
                            self.asesores_select_options, c.id_asesor
                        )

                        self.propiedad_search = ""
                        self.propietario_search = ""
                        self.asesor_search = ""
                        self.modal_open = True
            else:
                c = servicio.obtener_arrendamiento_por_id(id_contrato)
                if c:
                    async with self:
                        self.modal_mode = "editar_arrendamiento"
                        self.editing_id = id_contrato
                        self.form_data = {
                            "id_propiedad": str(c.id_propiedad),
                            "id_arrendatario": str(c.id_arrendatario),
                            "id_codeudor": str(c.id_codeudor or ""),
                            "fecha_inicio": c.fecha_inicio_contrato_a,
                            "fecha_fin": c.fecha_fin_contrato_a,
                            "duracion_meses": str(c.duracion_contrato_a),
                            "canon": str(c.canon_arrendamiento),
                            "deposito": str(c.deposito),
                            "fecha_pago": c.fecha_pago or "",
                        }
                        # Rehidratación de etiquetas
                        self.propiedad_selected_label = self._get_label_by_id(
                            self.propiedades_select_options, c.id_propiedad
                        )
                        self.arrendatario_selected_label = self._get_label_by_id(
                            self.arrendatarios_select_options, c.id_arrendatario
                        )
                        self.codeudor_selected_label = self._get_label_by_id(
                            self.codeudores_select_options, c.id_codeudor
                        )

                        self.propiedad_search = ""
                        self.arrendatario_search = ""
                        self.codeudor_search = ""
                        self.modal_open = True
        except Exception as e:
            async with self:
                self.error_message = f"Error: {e}"
        finally:
            async with self:
                self.is_loading = False

    def close_modal(self):
        self.modal_open = False
        self.editing_id = None
        self.form_data = {}

    @rx.event(background=True)
    async def save_contrato(self, form_data: Dict):
        async with self:
            self.is_loading = True
            # Capturar snapshot del state ANTES de soltar el lock
            # para evitar race conditions con on_change / reset_on_submit
            state_snapshot = dict(self.form_data)
        try:
            from src.infraestructura.persistencia.repositorio_contrato_mandato_postgres import (
                RepositorioContratoMandatoPostgres,
            )
            from src.infraestructura.persistencia.repositorio_contrato_arrendamiento_postgres import (
                RepositorioContratoArrendamientoPostgres,
            )

            servicio = ServicioContratos(db_manager)

            # El state_snapshot es la fuente de verdad porque TODOS los inputs
            # controlados actualizan el state vía on_change handlers.
            # form_data HTML aporta campos con 'name=' como fallback, pero
            # puede contener valores stale en inputs type="number" controlados.
            full_data = {**form_data, **state_snapshot}
            usuario = "admin"

            # ═══════════ DIAGNÓSTICO TEMPORAL ═══════════
            import logging
            _dbg = logging.getLogger("SAVE_CONTRATO_DEBUG")
            _dbg.setLevel(logging.DEBUG)
            if not _dbg.handlers:
                _dbg.addHandler(logging.StreamHandler())
            _dbg.info(f">>> form_data HTML: {form_data}")
            _dbg.info(f">>> state_snapshot: {state_snapshot}")
            _dbg.info(f">>> full_data (merged): canon={full_data.get('canon')}, tipo={type(full_data.get('canon'))}")
            _dbg.info(f">>> modal_mode={self.modal_mode}, editing_id={self.editing_id}")
            # ═══════════ FIN DIAGNÓSTICO ═══════════

            if "mandato" in self.modal_mode:
                datos = {
                    "id_propiedad": int(full_data["id_propiedad"]),
                    "id_propietario": int(full_data["id_propietario"]),
                    "id_asesor": int(full_data["id_asesor"]),
                    "fecha_inicio": full_data["fecha_inicio"],
                    "fecha_fin": full_data["fecha_fin"],
                    "canon": int(full_data.get("canon") or 0),
                    "comision_porcentaje": int(
                        float(full_data.get("comision_porcentaje") or 10) * 100
                    ),
                    "iva_porcentaje": int(
                        float(full_data.get("iva_porcentaje") or 19) * 100
                    ),
                    "duracion_meses": int(full_data.get("duracion_meses") or 12),
                    "fecha_pago": full_data.get("fecha_pago", ""),
                    "banco_propietario": full_data.get("banco_propietario", ""),
                    "numero_cuenta_propietario": full_data.get("numero_cuenta_propietario", ""),
                    "tipo_cuenta": full_data.get("tipo_cuenta", "Ahorros"),
                    "consignatario": full_data.get("consignatario", ""),
                    "documento_consignatario": full_data.get("documento_consignatario", ""),
                }
                if self.modal_mode == "crear_mandato":
                    servicio.crear_mandato(datos, usuario)
                else:
                    servicio.actualizar_mandato(self.editing_id, datos, usuario)
            else:
                datos = {
                    "id_propiedad": int(full_data["id_propiedad"]),
                    "id_arrendatario": int(full_data["id_arrendatario"]),
                    "id_codeudor": int(full_data["id_codeudor"])
                    if full_data.get("id_codeudor")
                    else None,
                    "fecha_inicio": full_data["fecha_inicio"],
                    "fecha_fin": full_data["fecha_fin"],
                    "canon": int(full_data.get("canon") or 0),
                    "deposito": int(full_data.get("deposito") or 0),
                    "duracion_meses": int(full_data.get("duracion_meses") or 12),
                    "fecha_pago": full_data.get("fecha_pago", ""),
                }
                if self.modal_mode == "crear_arrendamiento":
                    servicio.crear_arrendamiento(datos, usuario)
                else:
                    servicio.actualizar_arrendamiento(self.editing_id, datos, usuario)

            async with self:
                self.modal_open = False
                self.form_data = {}
            yield ContratosState.load_contratos()
            yield ContratosState.load_kpis()
            yield ContratosState.load_filter_options()
            yield rx.toast.success("Guardado exitoso", position="bottom-right")
        except Exception as e:
            async with self:
                self.error_message = str(e)
            yield rx.toast.error(f"Error: {e}")
        finally:
            async with self:
                self.is_loading = False

    @rx.event(background=True)
    async def open_detail_modal(self, id_contrato: int, tipo: str):
        async with self:
            self.is_loading = True
        try:
            from src.infraestructura.persistencia.repositorio_contrato_mandato_postgres import (
                RepositorioContratoMandatoPostgres,
            )
            from src.infraestructura.persistencia.repositorio_contrato_arrendamiento_postgres import (
                RepositorioContratoArrendamientoPostgres,
            )

            servicio = ServicioContratos(db_manager)

            detalle = servicio.obtener_detalle_contrato_ui(id_contrato, tipo)
            if detalle:
                async with self:
                    self.contrato_detalle = detalle
                    self.show_detail_modal = True
            else:
                async with self:
                    self.error_message = "Detalles no encontrados"
        except Exception as e:
            async with self:
                self.error_message = f"Error: {e}"
        finally:
            async with self:
                self.is_loading = False

    @rx.event(background=True)
    async def exportar_csv(self):
        async with self:
            self.is_loading = True
        try:
            from src.infraestructura.persistencia.repositorio_contrato_mandato_postgres import (
                RepositorioContratoMandatoPostgres,
            )
            from src.infraestructura.persistencia.repositorio_contrato_arrendamiento_postgres import (
                RepositorioContratoArrendamientoPostgres,
            )

            servicio = ServicioContratos(db_manager)

            estado_filtro = (
                self.filter_estado if self.filter_estado != "Todos" else None
            )

            csv_data = servicio.exportar_contratos_csv(
                filtro_tipo=self.filter_tipo if self.filter_tipo != "Todos" else None,
                estado=estado_filtro,
                busqueda=self.search_text if self.search_text else None,
            )
            import time

            timestamp = int(time.time())
            filename = f"reporte_contratos_{timestamp}.csv"
            yield rx.download(
                data=csv_data.encode("utf-8-sig")
                if isinstance(csv_data, str)
                else csv_data,
                filename=filename,
            )
        except Exception as e:
            async with self:
                self.error_message = f"Error exportando: {e}"
            yield rx.toast.error(f"Error: {e}")
        finally:
            async with self:
                self.is_loading = False

    @rx.event(background=True)
    async def toggle_estado(self, id_contrato: int, tipo: str, estado_actual: str):
        async with self:
            self.is_loading = True
        try:
            from src.infraestructura.persistencia.repositorio_contrato_mandato_postgres import (
                RepositorioContratoMandatoPostgres,
            )
            from src.infraestructura.persistencia.repositorio_contrato_arrendamiento_postgres import (
                RepositorioContratoArrendamientoPostgres,
            )
            from src.infraestructura.persistencia.repositorio_propiedad_postgres import (
                RepositorioPropiedadPostgres,
            )
            from src.infraestructura.persistencia.repositorio_renovacion_postgres import (
                RepositorioRenovacionPostgres,
            )
            from src.infraestructura.persistencia.repositorio_ipc_postgres import (
                RepositorioIPCPostgres,
            )
            from src.infraestructura.persistencia.repositorio_arrendatario_postgres import (
                RepositorioArrendatarioPostgres,
            )
            from src.infraestructura.persistencia.repositorio_codeudor_postgres import (
                RepositorioCodeudorPostgres,
            )
            from src.presentacion_reflex.state.pdf_state import PDFState

            servicio = ServicioContratos(db_manager)
            usuario_sistema = "admin"

            if estado_actual == "Activo":
                detalle = servicio.obtener_detalle_contrato_ui(id_contrato, tipo)
                beneficiario = (
                    detalle.get("propietario", "Propietario")
                    if tipo == "Mandato"
                    else detalle.get("arrendatario", "Arrendatario")
                    if detalle
                    else "Interesado"
                )
                motivo = "Cancelación manual desde interfaz"

                if tipo == "Mandato":
                    servicio.terminar_mandato(id_contrato, motivo, usuario_sistema)
                else:
                    servicio.terminar_arrendamiento(
                        id_contrato, motivo, usuario_sistema
                    )

                yield PDFState.generar_certificado_paz_y_salvo(
                    id_contrato, beneficiario
                )
                yield ContratosState.load_contratos()
                yield ContratosState.load_kpis()
                yield ContratosState.load_filter_options()
                yield rx.toast.info("Contrato cancelado")
            else:
                async with self:
                    self.error_message = "No se puede reactivar un contrato cancelado"
        except Exception as e:
            async with self:
                self.error_message = f"Error: {e}"
        finally:
            async with self:
                self.is_loading = False

    def set_renewal_fecha_fin(self, val: str):
        self.renewal_nueva_fecha_fin = val

    def cancel_renewal(self):
        self.show_renewal_confirm = False
        self.renewal_proyeccion = {}
        self.error_message = ""

    @rx.event(background=True)
    async def confirm_renewal(self, id_contrato: int, tipo: str):
        async with self:
            self.renewal_target_id = id_contrato
            self.renewal_target_tipo = tipo
            self.renewal_loading_proyeccion = True
            self.show_renewal_confirm = True
            self.error_message = ""
        try:
            from src.infraestructura.persistencia.repositorio_contrato_mandato_postgres import (
                RepositorioContratoMandatoPostgres,
            )
            from src.infraestructura.persistencia.repositorio_contrato_arrendamiento_postgres import (
                RepositorioContratoArrendamientoPostgres,
            )
            from src.infraestructura.persistencia.repositorio_propiedad_postgres import (
                RepositorioPropiedadPostgres,
            )
            from src.infraestructura.persistencia.repositorio_ipc_postgres import (
                RepositorioIPCPostgres,
            )

            servicio = ServicioContratos(db_manager)

            proyeccion = servicio.calcular_proyeccion_renovacion(id_contrato, tipo)
            async with self:
                self.renewal_proyeccion = proyeccion
                if not proyeccion.get("error"):
                    self.renewal_nueva_fecha_fin = proyeccion.get("fecha_fin", "")
        except Exception as e:
            async with self:
                self.renewal_proyeccion = {"error": f"Error: {e}"}
        finally:
            async with self:
                self.renewal_loading_proyeccion = False

    @rx.event(background=True)
    async def execute_renewal(self):
        async with self:
            self.is_loading = True
        try:
            from src.infraestructura.persistencia.repositorio_renovacion_postgres import (
                RepositorioRenovacionPostgres,
            )
            from src.infraestructura.persistencia.repositorio_contrato_mandato_postgres import (
                RepositorioContratoMandatoPostgres,
            )
            from src.infraestructura.persistencia.repositorio_contrato_arrendamiento_postgres import (
                RepositorioContratoArrendamientoPostgres,
            )
            from src.infraestructura.persistencia.repositorio_propiedad_postgres import (
                RepositorioPropiedadPostgres,
            )
            from src.infraestructura.persistencia.repositorio_ipc_postgres import (
                RepositorioIPCPostgres,
            )

            servicio = ServicioContratos(db_manager)

            res = {"success": False, "message": "Error desconocido"}
            try:
                if self.renewal_target_tipo == "Mandato":
                    contrato = servicio.renovar_mandato(
                        id_contrato=self.renewal_target_id,
                        usuario_sistema="admin",
                        nueva_fecha_fin=self.renewal_nueva_fecha_fin or None,
                    )
                    res = {
                        "success": True,
                        "message": f"Mandato renovado: {contrato.fecha_fin_contrato_m if contrato else ''}",
                    }
                else:
                    contrato = servicio.renovar_arrendamiento(
                        id_contrato=self.renewal_target_id,
                        usuario_sistema="admin",
                        nueva_fecha_fin=self.renewal_nueva_fecha_fin or None,
                    )
                    res = {
                        "success": True,
                        "message": f"Arrendamiento renovado: {contrato.fecha_fin_contrato_a if contrato else ''}",
                    }
            except ValueError as e:
                res = {"success": False, "message": str(e)}
            except Exception as e:
                res = {"success": False, "message": f"Error: {e}"}

            if res["success"]:
                async with self:
                    self.show_renewal_confirm = False
                    self.renewal_proyeccion = {}
                yield ContratosState.load_contratos()
                yield ContratosState.load_kpis()
                yield ContratosState.load_filter_options()
                yield rx.toast.success(res["message"])
            else:
                async with self:
                    self.error_message = res["message"]
        except Exception as e:
            async with self:
                self.error_message = f"Error: {e}"
        finally:
            async with self:
                self.is_loading = False

    def close_detail_modal(self):
        self.show_detail_modal = False
        self.contrato_detalle = {}

    def close_ipc_modal(self):
        self.show_ipc_modal = False
        self.error_message = ""

    def open_ipc_modal(self, id_contrato: int):
        from datetime import datetime

        self.ipc_target_contrato_id = id_contrato
        self.form_data = {
            "porcentaje_ipc": "5.62",
            "fecha_aplicacion": datetime.now().strftime("%Y-%m-%d"),
            "observaciones": "",
        }
        self.show_ipc_modal = True

    @rx.event(background=True)
    async def apply_ipc_increment(self, form_data: Dict):
        async with self:
            self.is_loading = True
            self.error_message = ""

        try:
            porcentaje = float(form_data.get("porcentaje_ipc", 0))
            fecha = form_data.get("fecha_aplicacion", "")
            observaciones = form_data.get("observaciones", "")

            from src.infraestructura.persistencia.repositorio_contrato_mandato_postgres import (
                RepositorioContratoMandatoPostgres,
            )
            from src.infraestructura.persistencia.repositorio_contrato_arrendamiento_postgres import (
                RepositorioContratoArrendamientoPostgres,
            )
            from src.infraestructura.persistencia.repositorio_ipc_postgres import (
                RepositorioIPCPostgres,
            )

            servicio = ServicioContratos(db_manager)

            resultado = servicio.aplicar_incremento_ipc(
                id_contrato=self.ipc_target_contrato_id,
                porcentaje_ipc=porcentaje,
                fecha_aplicacion=fecha,
                observaciones=observaciones,
                usuario="admin",
            )

            if resultado["success"]:
                async with self:
                    self.show_ipc_modal = False
                    self.ipc_target_contrato_id = 0
                    self.form_data = {}
                yield ContratosState.load_contratos()
                yield ContratosState.load_kpis()
                yield ContratosState.load_filter_options()
                yield rx.toast.success(resultado["message"], position="bottom-right")
            else:
                async with self:
                    self.error_message = resultado["message"]
                yield rx.toast.error(resultado["message"], position="bottom-right")

        except Exception as e:
            async with self:
                self.error_message = f"Error al aplicar IPC: {str(e)}"
            yield rx.toast.error(f"Error: {str(e)}", position="bottom-right")
        finally:
            async with self:
                self.is_loading = False
