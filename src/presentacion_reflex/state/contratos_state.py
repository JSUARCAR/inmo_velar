from datetime import datetime
from typing import Any, Dict, List, Optional

import reflex as rx

from src.aplicacion.servicios.servicio_contratos import ServicioContratos
from src.infraestructura.persistencia.database import db_manager
from src.presentacion_reflex.state.documentos_mixin import DocumentosStateMixin


class ContratosState(DocumentosStateMixin):
    """Estado para gestión de contratos (Mandatos y Arrendamientos).
    Maneja paginación, filtros y CRUD operations.
    """

    # Paginación
    current_page: int = 1
    page_size: int = 25
    total_items: int = 0

    # Datos
    contratos: List[Dict[str, Any]] = []
    is_loading: bool = False
    # Datos
    contratos: List[Dict[str, Any]] = []
    is_loading: bool = False
    error_message: str = ""
    is_grid_view: bool = False  # Default to Table, or True for Elite default

    # Búsqueda y Filtros
    search_text: str = ""
    filter_tipo: str = "Todos"  # Todos, Mandato, Arrendamiento
    filter_estado: str = "Activo"  # Todos, Activo, Cancelado
    filter_propiedad_id: str = ""
    filter_persona_id: str = ""
    filter_asesor_id: str = ""

    # Opciones de filtros (para dropdowns)
    tipo_options: List[str] = ["Todos", "Mandato", "Arrendamiento"]
    estado_options: List[str] = ["Todos", "Activo", "Cancelado"]
    propiedades_options: List[Dict[str, Any]] = []
    personas_options: List[Dict[str, Any]] = []

    # Opciones para selects (listas simples de strings)
    # Opciones para selects (listas de listas ["label", "value"])
    propiedades_select_options: List[List[str]] = []
    propietarios_select_options: List[List[str]] = []
    asesores_select_options: List[List[str]] = []
    propiedades_select_options: List[List[str]] = []
    propietarios_select_options: List[List[str]] = []
    asesores_select_options: List[List[str]] = []
    asesores_select_options: List[List[str]] = []
    personas_select_options: List[List[str]] = []
    # Nuevas opciones para Arrendamiento y Mandato
    propiedades_arriendo_select_options: List[List[str]] = []
    propiedades_mandato_libre_select_options: List[List[str]] = []
    arrendatarios_select_options: List[List[str]] = []
    codeudores_select_options: List[List[str]] = []

    # Mapas de datos adicionales
    propiedades_canon_map: Dict[str, float] = {}

    # Modal CRUD
    modal_open: bool = False
    modal_mode: str = "crear_mandato"  # crear_mandato, crear_arrendamiento, editar
    editing_id: Optional[int] = None
    form_data: Dict[str, Any] = {}

    # Modal Detalle
    show_detail_modal: bool = False
    contrato_detalle: Dict[str, Any] = {}

    # Modal IPC Increment
    show_ipc_modal: bool = False
    ipc_target_contrato_id: int = 0
    # Document Management Vars (Inherited from DocumentosStateMixin)
    # current_entidad_tipo and current_entidad_id are now in the mixin

    def set_form_field(self, name: str, value: Any):
        """Actualiza un campo del formulario."""
        self.form_data[name] = value

    def toggle_view(self):
        """Alterna entre vista de tabla y grid."""
        self.is_grid_view = not self.is_grid_view

    def on_change_propiedad(self, id_propiedad: str):
        """Maneja cambio propiedad Mandato."""
        self.form_data["id_propiedad"] = id_propiedad
        if id_propiedad and id_propiedad in self.propiedades_canon_map:
            canon = self.propiedades_canon_map[id_propiedad]
            self.form_data["canon"] = str(int(canon))
        else:
            self.form_data["canon"] = ""

    def on_change_propiedad_arriendo(self, id_propiedad: str):
        """
        Maneja cambio propiedad Arrendamiento.
        1. Carga canon.
        2. Calcula deposito (50% canon).
        """
        self.form_data["id_propiedad"] = id_propiedad
        if id_propiedad and id_propiedad in self.propiedades_canon_map:
            canon = self.propiedades_canon_map[id_propiedad]
            self.form_data["canon"] = str(int(canon))
            # Calcular deposito
            self.form_data["deposito"] = str(int(canon * 0.5))
        else:
            self.form_data["canon"] = ""
            self.form_data["deposito"] = "0"

    def on_change_canon_arriendo(self, canon: str):
        """Recalcula deposito si cambia el canon manual."""
        self.form_data["canon"] = canon
        try:
            val_canon = float(canon) if canon else 0
            self.form_data["deposito"] = str(int(val_canon * 0.5))
        except ValueError:
            pass

    def _calcular_duracion(self):
        """Calcula la duración en meses entre fecha inicio y fin."""
        f_inicio = self.form_data.get("fecha_inicio")
        f_fin = self.form_data.get("fecha_fin")

        if f_inicio and f_fin:
            try:
                d_inicio = datetime.strptime(f_inicio, "%Y-%m-%d")
                d_fin = datetime.strptime(f_fin, "%Y-%m-%d")

                # Calcular diferencia en meses
                # Formula: (Años * 12) + Meses
                diff_years = d_fin.year - d_inicio.year
                diff_months = d_fin.month - d_inicio.month

                total_meses = (diff_years * 12) + diff_months

                # Ajuste basico: si el dia de fin es menor al de inicio, no ha completado el mes?
                # Usualmente en contratos se cuenta la diferencia de meses calendario.
                # Si total_meses < 0, poner 0.
                if total_meses < 0:
                    total_meses = 0

                self.form_data["duracion_meses"] = str(total_meses)
            except ValueError:
                pass  # Formato de fecha invalido

    def on_change_fecha_inicio(self, fecha: str):
        """Actualiza fecha inicio y recalcula duración."""
        self.form_data["fecha_inicio"] = fecha
        self._calcular_duracion()

    def on_change_fecha_fin(self, fecha: str):
        """Actualiza fecha fin y recalcula duración."""
        self.form_data["fecha_fin"] = fecha
        self._calcular_duracion()

    @rx.event(background=True)
    async def on_load(self):
        """Carga inicial al montar la página."""
        async with self:
            self.is_loading = True

        try:
            # Cargar opciones de filtros
            yield ContratosState.load_filter_options()
            # Cargar contratos
            yield ContratosState.load_contratos()
        finally:
            async with self:
                self.is_loading = False

    @rx.event(background=True)
    async def load_filter_options(self):
        """Carga opciones para dropdowns de filtros."""
        # Instanciar repositorios y servicio
        from src.infraestructura.persistencia.repositorio_propiedad_sqlite import RepositorioPropiedadSQLite
        from src.infraestructura.persistencia.repositorio_contrato_mandato_sqlite import (
            RepositorioContratoMandatoSQLite,
        )
        from src.infraestructura.persistencia.repositorio_contrato_arrendamiento_sqlite import (
            RepositorioContratoArrendamientoSQLite,
        )
        from src.infraestructura.persistencia.repositorio_renovacion_sqlite import (
            RepositorioRenovacionSQLite,
        )
        from src.infraestructura.persistencia.repositorio_ipc_sqlite import RepositorioIPCSQLite
        from src.infraestructura.persistencia.repositorio_arrendatario_sqlite import (
            RepositorioArrendatarioSQLite,
        )
        from src.infraestructura.persistencia.repositorio_codeudor_sqlite import (
            RepositorioCodeudorSQLite,
        )

        repo_propiedad = RepositorioPropiedadSQLite(db_manager)
        repo_mandato = RepositorioContratoMandatoSQLite(db_manager)
        repo_arriendo = RepositorioContratoArrendamientoSQLite(db_manager)
        repo_renovacion = RepositorioRenovacionSQLite(db_manager)
        repo_ipc = RepositorioIPCSQLite(db_manager)
        repo_arrendatario = RepositorioArrendatarioSQLite(db_manager)
        repo_codeudor = RepositorioCodeudorSQLite(db_manager)

        # Como solo cargamos opciones SQL directas aqui, no necesitamos el servicio completo, 
        # pero mantenemos la estructura por si acaso se usa logica de negocio luego.
        # De hecho, el código original INSTANCIABA el servicio pero NO LO USABA en load_filter_options
        # porque hacía queries directos con db_manager.
        # Mantendremos la instanciación correcta si se quiere usar, pero el bloque de abajo usa db_manager directo.

        # 1. Cargar TODAS las Propiedades activas
        # NOTE: Load ALL properties (not just those without contracts) to support edit mode
        query_propiedades = """
        SELECT P.ID_PROPIEDAD, P.MATRICULA_INMOBILIARIA, P.DIRECCION_PROPIEDAD, P.CANON_ARRENDAMIENTO_ESTIMADO
        FROM PROPIEDADES P
        WHERE P.ESTADO_REGISTRO = TRUE
        ORDER BY P.DIRECCION_PROPIEDAD
        """

        # 2. Cargar Propietarios: Unir PERSONAS con PROPIETARIOS
        query_propietarios = """
        SELECT PR.ID_PROPIETARIO, P.NOMBRE_COMPLETO, P.NUMERO_DOCUMENTO
        FROM PERSONAS P
        INNER JOIN PROPIETARIOS PR ON P.ID_PERSONA = PR.ID_PERSONA
        WHERE P.ESTADO_REGISTRO = TRUE AND PR.ESTADO_PROPIETARIO = TRUE
        ORDER BY P.NOMBRE_COMPLETO
        """

        # 3. Cargar Asesores: Unir PERSONAS con ASESORES
        query_asesores = """
        SELECT A.ID_ASESOR, P.NOMBRE_COMPLETO, P.NUMERO_DOCUMENTO
        FROM PERSONAS P
        INNER JOIN ASESORES A ON P.ID_PERSONA = A.ID_PERSONA
        WHERE P.ESTADO_REGISTRO = TRUE AND A.ESTADO = TRUE
        ORDER BY P.NOMBRE_COMPLETO
        """

        # 4. Cargar Personas (Generico para Arrendatarios/Codeudores) - MANTENER ID_PERSONA?
        # Para arrendamiento usamos las especificas abajo. Esta es select generico tal vez para otros usos?
        # Si se usa para algo que requiera ID_PERSONA, dejarlo.
        query_personas = """
        SELECT ID_PERSONA, NOMBRE_COMPLETO, NUMERO_DOCUMENTO
        FROM PERSONAS
        WHERE ESTADO_REGISTRO = TRUE
        ORDER BY NOMBRE_COMPLETO
        """

        # Helper local para acceso seguro a diccionarios (Case Insensitive)
        def get_val(row: dict, field: str) -> str:
            """Intenta obtener valor con clave en mayúscula o minúscula."""
            val = row.get(field.upper())
            if val is None:
                val = row.get(field.lower())
            if val is None:
                # Fallback para claves mixtas si fuera necesario
                return ""
            return str(val)

        with db_manager.obtener_conexion() as conn:
            cursor = db_manager.get_dict_cursor(conn)

            # Propiedades
            cursor.execute(query_propiedades)
            rows_propiedades = cursor.fetchall()
            # Formato para Reflex Select: [Label, Value]
            propiedades_select = [
                [
                    f"{get_val(row, 'MATRICULA_INMOBILIARIA')} - {get_val(row, 'DIRECCION_PROPIEDAD')}",
                    get_val(row, "ID_PROPIEDAD"),
                ]
                for row in rows_propiedades
            ]

            # Crear mapa de canones: ID -> Canon (float/int)
            canon_map = {}
            for row in rows_propiedades:
                # Intentar obtener el canon con manejo de mayusculas/minusculas
                canon_str = get_val(row, "CANON_ARRENDAMIENTO_ESTIMADO")
                id_prop = get_val(row, "ID_PROPIEDAD")
                canon_map[id_prop] = float(canon_str) if canon_str else 0.0

            # Propietarios
            cursor.execute(query_propietarios)
            rows_propietarios = cursor.fetchall()
            propietarios_select = [
                [
                    f"{get_val(row, 'NOMBRE_COMPLETO')} - {get_val(row, 'NUMERO_DOCUMENTO')}",
                    get_val(row, "ID_PROPIETARIO"),
                ]
                for row in rows_propietarios
            ]

            # Asesores
            cursor.execute(query_asesores)
            rows_asesores = cursor.fetchall()
            asesores_select = [
                [
                    f"{get_val(row, 'NOMBRE_COMPLETO')} - {get_val(row, 'NUMERO_DOCUMENTO')}",
                    get_val(row, "ID_ASESOR"),
                ]
                for row in rows_asesores
            ]

            # Personas (Generico)
            cursor.execute(query_personas)
            rows_personas = cursor.fetchall()
            personas_select = [
                [
                    f"{get_val(row, 'NOMBRE_COMPLETO')} - {get_val(row, 'NUMERO_DOCUMENTO')}",
                    get_val(row, "ID_PERSONA"),
                ]
                for row in rows_personas
            ]

            # 4.1. Propiedades para NUEVO MANDATO (Sin mandato activo)
            # NOTE: Load properties without active Mandate
            query_propiedades_libre_mandato = """
            SELECT P.ID_PROPIEDAD, P.MATRICULA_INMOBILIARIA, P.DIRECCION_PROPIEDAD
            FROM PROPIEDADES P
            WHERE P.ESTADO_REGISTRO = TRUE
            AND NOT EXISTS (
                SELECT 1 FROM CONTRATOS_MANDATOS CM 
                WHERE CM.ID_PROPIEDAD = P.ID_PROPIEDAD
                AND CM.ESTADO_CONTRATO_M = 'Activo'
            )
            ORDER BY P.DIRECCION_PROPIEDAD
            """
            cursor.execute(query_propiedades_libre_mandato)
            rows_prop_libre = cursor.fetchall()
            propiedades_libre_select = [
                [
                    f"{get_val(row, 'MATRICULA_INMOBILIARIA')} - {get_val(row, 'DIRECCION_PROPIEDAD')}",
                    get_val(row, "ID_PROPIEDAD"),
                ]
                for row in rows_prop_libre
            ]

            # ---------------------------------------------------------
            # CARGADORES ESPECIFICOS PAR ARRENDAMIENTO
            # ---------------------------------------------------------

            # 5. Propiedades para Arrendamiento (Con Mandato Activo Y SIN Arrendamiento Activo)
            # NOTE: Load properties with active Mandate AND NO active Lease
            query_propiedades_arriendo = """
            SELECT P.ID_PROPIEDAD, P.MATRICULA_INMOBILIARIA, P.DIRECCION_PROPIEDAD, P.CANON_ARRENDAMIENTO_ESTIMADO
            FROM PROPIEDADES P
            JOIN CONTRATOS_MANDATOS CM ON P.ID_PROPIEDAD = CM.ID_PROPIEDAD
            WHERE P.ESTADO_REGISTRO = TRUE
            AND CM.ESTADO_CONTRATO_M = 'Activo'
            AND NOT EXISTS (
                SELECT 1 FROM CONTRATOS_ARRENDAMIENTOS CA 
                WHERE CA.ID_PROPIEDAD = P.ID_PROPIEDAD 
                AND CA.ESTADO_CONTRATO_A = 'Activo'
            )
            ORDER BY P.DIRECCION_PROPIEDAD
            """
            cursor.execute(query_propiedades_arriendo)
            rows_prop_arriendo = cursor.fetchall()
            propiedades_arriendo_select = [
                [
                    f"{get_val(row, 'MATRICULA_INMOBILIARIA')} - {get_val(row, 'DIRECCION_PROPIEDAD')}",
                    get_val(row, "ID_PROPIEDAD"),
                ]
                for row in rows_prop_arriendo
            ]

            # Actualizar mapa de canones con estas propiedades tambien
            for row in rows_prop_arriendo:
                canon_str = get_val(row, "CANON_ARRENDAMIENTO_ESTIMADO")
                id_prop = get_val(row, "ID_PROPIEDAD")
                if id_prop:
                    canon_map[id_prop] = float(canon_str) if canon_str else 0.0

            # 6. Arrendatarios (Personas con rol Arrendatario)
            query_arrendatarios = """
            SELECT A.ID_ARRENDATARIO, P.NOMBRE_COMPLETO, P.NUMERO_DOCUMENTO
            FROM PERSONAS P
            INNER JOIN ARRENDATARIOS A ON P.ID_PERSONA = A.ID_PERSONA
            WHERE P.ESTADO_REGISTRO = TRUE AND A.ESTADO_ARRENDATARIO = TRUE
            ORDER BY P.NOMBRE_COMPLETO
            """
            cursor.execute(query_arrendatarios)
            rows_arrendatarios = cursor.fetchall()
            arrendatarios_select = [
                [
                    f"{get_val(row, 'NOMBRE_COMPLETO')} - {get_val(row, 'NUMERO_DOCUMENTO')}",
                    get_val(row, "ID_ARRENDATARIO"),
                ]
                for row in rows_arrendatarios
            ]

            # 7. Codeudores (Personas con rol Codeudor)
            query_codeudores = """
            SELECT C.ID_CODEUDOR, P.NOMBRE_COMPLETO, P.NUMERO_DOCUMENTO
            FROM PERSONAS P
            INNER JOIN CODEUDORES C ON P.ID_PERSONA = C.ID_PERSONA
            WHERE P.ESTADO_REGISTRO = TRUE AND C.ESTADO_REGISTRO = TRUE
            ORDER BY P.NOMBRE_COMPLETO
            """
            cursor.execute(query_codeudores)
            rows_codeudores = cursor.fetchall()
            codeudores_select = [
                [
                    f"{get_val(row, 'NOMBRE_COMPLETO')} - {get_val(row, 'NUMERO_DOCUMENTO')}",
                    get_val(row, "ID_CODEUDOR"),
                ]
                for row in rows_codeudores
            ]

        async with self:
            # self.propiedades_options = ... # Ya no usamos listas de dicts viejas si no se necesitan
            self.propiedades_select_options = propiedades_select
            self.propiedades_mandato_libre_select_options = propiedades_libre_select
            self.propietarios_select_options = propietarios_select
            self.asesores_select_options = asesores_select
            self.personas_select_options = personas_select
            self.propiedades_arriendo_select_options = propiedades_arriendo_select
            self.arrendatarios_select_options = arrendatarios_select
            self.codeudores_select_options = codeudores_select
            self.propiedades_canon_map = canon_map
            self.propiedades_canon_map = canon_map

    @rx.event(background=True)
    async def load_contratos(self):
        """Carga contratos con filtros y paginación (unificados)."""
        async with self:
            self.is_loading = True
            self.error_message = ""

        try:
            from src.infraestructura.persistencia.repositorio_contrato_mandato_sqlite import (
                RepositorioContratoMandatoSQLite,
            )
            from src.infraestructura.persistencia.repositorio_contrato_arrendamiento_sqlite import (
                RepositorioContratoArrendamientoSQLite,
            )
            from src.infraestructura.persistencia.repositorio_propiedad_sqlite import (
                RepositorioPropiedadSQLite,
            )
            from src.infraestructura.persistencia.repositorio_renovacion_sqlite import (
                RepositorioRenovacionSQLite,
            )
            from src.infraestructura.persistencia.repositorio_ipc_sqlite import RepositorioIPCSQLite
            from src.infraestructura.persistencia.repositorio_arrendatario_sqlite import (
                RepositorioArrendatarioSQLite,
            )
            from src.infraestructura.persistencia.repositorio_codeudor_sqlite import (
                RepositorioCodeudorSQLite,
            )

            repo_mandato = RepositorioContratoMandatoSQLite(db_manager)
            repo_arriendo = RepositorioContratoArrendamientoSQLite(db_manager)
            repo_propiedad = RepositorioPropiedadSQLite(db_manager)
            repo_renovacion = RepositorioRenovacionSQLite(db_manager)
            repo_ipc = RepositorioIPCSQLite(db_manager)
            repo_arrendatario = RepositorioArrendatarioSQLite(db_manager)
            repo_codeudor = RepositorioCodeudorSQLite(db_manager)

            servicio = ServicioContratos(
                db_manager,
                repo_mandato=repo_mandato,
                repo_arriendo=repo_arriendo,
                repo_propiedad=repo_propiedad,
                repo_renovacion=repo_renovacion,
                repo_ipc=repo_ipc,
                repo_arrendatario=repo_arrendatario,
                repo_codeudor=repo_codeudor,
            )

            # Helper para el filtro de asesor (manejar "todos" o vacio)
            asesor_filter = (
                self.filter_asesor_id
                if self.filter_asesor_id and self.filter_asesor_id != "todos"
                else None
            )

            # Determinar qué tipo de contratos cargar
            if self.filter_tipo == "Mandato":
                # Solo mandatos
                resultado = servicio.listar_mandatos_paginado(
                    page=self.current_page,
                    page_size=self.page_size,
                    estado=self.filter_estado if self.filter_estado != "Todos" else None,
                    busqueda=self.search_text if self.search_text else None,
                    id_asesor=asesor_filter,
                )
                # Agregar campo 'tipo' para distinguir en la UI
                items = [{"tipo": "Mandato", **item} for item in resultado.items]

            elif self.filter_tipo == "Arrendamiento":
                # Solo arrendamientos
                resultado = servicio.listar_arrendamientos_paginado(
                    page=self.current_page,
                    page_size=self.page_size,
                    estado=self.filter_estado if self.filter_estado != "Todos" else None,
                    busqueda=self.search_text if self.search_text else None,
                    id_asesor=asesor_filter,
                )
                items = [{"tipo": "Arrendamiento", **item} for item in resultado.items]

            else:
                # Todos: combinar mandatos y arrendamientos
                resultado_mandatos = servicio.listar_mandatos_paginado(
                    page=self.current_page,
                    page_size=self.page_size,
                    estado=self.filter_estado if self.filter_estado != "Todos" else None,
                    busqueda=self.search_text if self.search_text else None,
                    id_asesor=asesor_filter,
                )

                resultado_arrendamientos = servicio.listar_arrendamientos_paginado(
                    page=self.current_page,
                    page_size=self.page_size,
                    estado=self.filter_estado if self.filter_estado != "Todos" else None,
                    busqueda=self.search_text if self.search_text else None,
                    id_asesor=asesor_filter,
                )

                mandatos = [{"tipo": "Mandato", **item} for item in resultado_mandatos.items]
                arrendamientos = [
                    {"tipo": "Arrendamiento", **item} for item in resultado_arrendamientos.items
                ]

                items = mandatos + arrendamientos
                # Total combinado
                resultado = resultado_mandatos  # Para paginación usamos uno como base
                resultado.items = items
                resultado.total = resultado_mandatos.total + resultado_arrendamientos.total

            async with self:
                self.contratos = items
                self.total_items = resultado.total
                self.is_loading = False

        except Exception as e:
            async with self:
                self.error_message = f"Error al cargar contratos: {str(e)}"
                self.contratos = []
                self.total_items = 0
                self.is_loading = False

    # Paginación
    def next_page(self):
        """Avanza a la siguiente página."""
        if self.current_page * self.page_size < self.total_items:
            self.current_page += 1
            return ContratosState.load_contratos

    def prev_page(self):
        """Retrocede a la página anterior."""
        if self.current_page > 1:
            self.current_page -= 1
            return ContratosState.load_contratos

    def set_page_size(self, size: str):
        """Cambia el tamaño de página."""
        self.page_size = int(size)
        self.current_page = 1
        return ContratosState.load_contratos

    # Búsqueda y Filtros
    def set_search(self, value: str):
        """Actualiza búsqueda."""
        self.search_text = value

    def search_contratos(self):
        """Ejecuta búsqueda."""
        self.current_page = 1
        return ContratosState.load_contratos

    def handle_search_key_down(self, key: str):
        """
        Maneja el evento de teclado en el campo de búsqueda.
        Si se presiona Enter, ejecuta la búsqueda.
        """
        if key == "Enter":
            return self.search_contratos()

    def set_filter_tipo(self, value: str):
        """Cambia filtro de tipo."""
        self.filter_tipo = value
        self.current_page = 1
        return ContratosState.load_contratos

    def set_filter_estado(self, value: str):
        """Cambia filtro de estado."""
        self.filter_estado = value
        self.current_page = 1
        return ContratosState.load_contratos

    def set_filter_propiedad(self, value: str):
        """Cambia filtro de propiedad."""
        self.filter_propiedad_id = value
        self.current_page = 1
        return ContratosState.load_contratos

    def set_filter_persona(self, value: str):
        """Cambia filtro de persona."""
        self.filter_persona_id = value
        self.current_page = 1
        return ContratosState.load_contratos

    def set_filter_asesor(self, value: str):
        """Cambia filtro de asesor."""
        self.filter_asesor_id = value
        self.current_page = 1
        return ContratosState.load_contratos

    # Modal CRUD
    def open_create_mandato_modal(self):
        """Abre modal para crear nuevo mandato."""
        self.modal_mode = "crear_mandato"
        self.editing_id = None
        self.form_data = {
            "id_propiedad": "",
            "id_propietario": "",
            "id_asesor": "",
            "fecha_inicio": "",
            "fecha_inicio": "",
            "fecha_fin": "",
            "fecha_pago": "",
            "duracion_meses": 12,
            "canon": 0,
            "comision_porcentaje": 10,  # 10% Predeterminado
            "iva_porcentaje": 19,  # 19% Predeterminado
        }
        self.modal_open = True
        self.error_message = ""

    def open_create_arrendamiento_modal(self):
        """Abre modal para crear nuevo arrendamiento."""
        self.modal_mode = "crear_arrendamiento"
        self.editing_id = None
        self.form_data = {
            "id_propiedad": "",
            "id_arrendatario": "",
            "id_codeudor": "",
            "fecha_inicio": "",
            "fecha_fin": "",
            "duracion_meses": 12,
            "canon": 0,
            "deposito": 0,
        }
        self.modal_open = True
        self.error_message = ""

    @rx.event(background=True)
    async def open_edit_modal(self, id_contrato: int, tipo: str):
        """Abre modal para editar contrato existente."""
        async with self:
            self.is_loading = True
            self.error_message = ""

        try:
            # Instanciar repositorios y servicio
            from src.infraestructura.persistencia.repositorio_contrato_mandato_sqlite import (
                RepositorioContratoMandatoSQLite,
            )
            from src.infraestructura.persistencia.repositorio_contrato_arrendamiento_sqlite import (
                RepositorioContratoArrendamientoSQLite,
            )
            from src.infraestructura.persistencia.repositorio_propiedad_sqlite import (
                RepositorioPropiedadSQLite,
            )
            from src.infraestructura.persistencia.repositorio_renovacion_sqlite import (
                RepositorioRenovacionSQLite,
            )
            from src.infraestructura.persistencia.repositorio_ipc_sqlite import RepositorioIPCSQLite
            from src.infraestructura.persistencia.repositorio_arrendatario_sqlite import (
                RepositorioArrendatarioSQLite,
            )
            from src.infraestructura.persistencia.repositorio_codeudor_sqlite import (
                RepositorioCodeudorSQLite,
            )

            repo_mandato = RepositorioContratoMandatoSQLite(db_manager)
            repo_arriendo = RepositorioContratoArrendamientoSQLite(db_manager)
            repo_propiedad = RepositorioPropiedadSQLite(db_manager)
            repo_renovacion = RepositorioRenovacionSQLite(db_manager)
            repo_ipc = RepositorioIPCSQLite(db_manager)
            repo_arrendatario = RepositorioArrendatarioSQLite(db_manager)
            repo_codeudor = RepositorioCodeudorSQLite(db_manager)

            servicio = ServicioContratos(
                db_manager,
                repo_mandato=repo_mandato,
                repo_arriendo=repo_arriendo,
                repo_propiedad=repo_propiedad,
                repo_renovacion=repo_renovacion,
                repo_ipc=repo_ipc,
                repo_arrendatario=repo_arrendatario,
                repo_codeudor=repo_codeudor,
            )

            if tipo == "Mandato":
                contrato = servicio.obtener_mandato_por_id(id_contrato)
                if contrato:
                    async with self:
                        self.modal_mode = "editar_mandato"
                        self.editing_id = id_contrato
                        self.form_data = {
                            "id_propiedad": str(contrato.id_propiedad),
                            "id_propietario": str(contrato.id_propietario),
                            "id_asesor": str(contrato.id_asesor),
                            "fecha_inicio": contrato.fecha_inicio_contrato_m,
                            "fecha_inicio": contrato.fecha_inicio_contrato_m,
                            "fecha_fin": contrato.fecha_fin_contrato_m,
                            "fecha_pago": contrato.fecha_pago or "",
                            "duracion_meses": contrato.duracion_contrato_m,
                            "canon": contrato.canon_mandato,
                            "comision_porcentaje": contrato.comision_porcentaje_contrato_m,
                        }

                        # Set Document Context for Mandato
                        self.current_entidad_tipo = "CONTRATO_MANDATO"
                        self.current_entidad_id = str(id_contrato)
                        pass  # print(f"DEBUG: open_edit_modal Mandato. Set ID: {self.current_entidad_id}") [OpSec Removed]
                        self.cargar_documentos()

                        self.modal_open = True
            else:
                contrato = servicio.obtener_arrendamiento_por_id(id_contrato)
                if contrato:
                    async with self:
                        self.modal_mode = "editar_arrendamiento"
                        self.editing_id = id_contrato
                        self.form_data = {
                            "id_propiedad": str(contrato.id_propiedad),
                            "id_arrendatario": str(contrato.id_arrendatario),
                            "id_codeudor": (
                                str(contrato.id_codeudor) if contrato.id_codeudor else ""
                            ),
                            "fecha_inicio": contrato.fecha_inicio_contrato_a,
                            "fecha_fin": contrato.fecha_fin_contrato_a,
                            "canon": contrato.canon_arrendamiento,
                            "deposito": contrato.deposito,
                        }

                        # Set Document Context for Arrendamiento
                        self.current_entidad_tipo = "CONTRATO_ARRENDAMIENTO"
                        self.current_entidad_id = str(id_contrato)
                        pass  # print(f"DEBUG: open_edit_modal Arrendamiento. Set ID: {self.current_entidad_id}") [OpSec Removed]
                        self.cargar_documentos()

                        self.modal_open = True

        except Exception as e:
            async with self:
                self.error_message = f"Error al cargar contrato: {str(e)}"
        finally:
            async with self:
                self.is_loading = False

    def close_modal(self):
        """Cierra el modal."""
        self.modal_open = False
        self.editing_id = None
        self.form_data = {}
        self.error_message = ""

    @rx.event(background=True)
    async def open_detail_modal(self, id_contrato: int, tipo: str):
        """Abre modal con detalle completo del contrato."""
        async with self:
            self.is_loading = True
            self.error_message = ""

        try:
            # Instanciar repositorios y servicio
            from src.infraestructura.persistencia.repositorio_contrato_mandato_sqlite import (
                RepositorioContratoMandatoSQLite,
            )
            from src.infraestructura.persistencia.repositorio_contrato_arrendamiento_sqlite import (
                RepositorioContratoArrendamientoSQLite,
            )
            from src.infraestructura.persistencia.repositorio_propiedad_sqlite import (
                RepositorioPropiedadSQLite,
            )
            from src.infraestructura.persistencia.repositorio_renovacion_sqlite import (
                RepositorioRenovacionSQLite,
            )
            from src.infraestructura.persistencia.repositorio_ipc_sqlite import RepositorioIPCSQLite
            from src.infraestructura.persistencia.repositorio_arrendatario_sqlite import (
                RepositorioArrendatarioSQLite,
            )
            from src.infraestructura.persistencia.repositorio_codeudor_sqlite import (
                RepositorioCodeudorSQLite,
            )

            repo_mandato = RepositorioContratoMandatoSQLite(db_manager)
            repo_arriendo = RepositorioContratoArrendamientoSQLite(db_manager)
            repo_propiedad = RepositorioPropiedadSQLite(db_manager)
            repo_renovacion = RepositorioRenovacionSQLite(db_manager)
            repo_ipc = RepositorioIPCSQLite(db_manager)
            repo_arrendatario = RepositorioArrendatarioSQLite(db_manager)
            repo_codeudor = RepositorioCodeudorSQLite(db_manager)

            servicio = ServicioContratos(
                db_manager,
                repo_mandato=repo_mandato,
                repo_arriendo=repo_arriendo,
                repo_propiedad=repo_propiedad,
                repo_renovacion=repo_renovacion,
                repo_ipc=repo_ipc,
                repo_arrendatario=repo_arrendatario,
                repo_codeudor=repo_codeudor,
            )
            detalle = servicio.obtener_detalle_contrato_ui(id_contrato, tipo)

            if detalle:
                async with self:
                    self.contrato_detalle = detalle
                    self.show_detail_modal = True
                    self.is_loading = False
            else:
                async with self:
                    self.error_message = "Contrato no encontrado"
                    self.is_loading = False
        except Exception as e:
            async with self:
                self.error_message = f"Error al cargar detalle: {str(e)}"
                self.is_loading = False

    def close_detail_modal(self):
        """Cierra modal de detalle."""
        self.show_detail_modal = False
        self.contrato_detalle = {}

    @rx.event(background=True)
    async def save_contrato(self, form_data: Dict):
        """Guarda contrato (crear o editar)."""
        async with self:
            self.is_loading = True
            self.error_message = ""

        try:
            # Instanciar repositorios y servicio
            from src.infraestructura.persistencia.repositorio_contrato_mandato_sqlite import (
                RepositorioContratoMandatoSQLite,
            )
            from src.infraestructura.persistencia.repositorio_contrato_arrendamiento_sqlite import (
                RepositorioContratoArrendamientoSQLite,
            )
            from src.infraestructura.persistencia.repositorio_propiedad_sqlite import (
                RepositorioPropiedadSQLite,
            )
            from src.infraestructura.persistencia.repositorio_renovacion_sqlite import (
                RepositorioRenovacionSQLite,
            )
            from src.infraestructura.persistencia.repositorio_ipc_sqlite import RepositorioIPCSQLite
            from src.infraestructura.persistencia.repositorio_arrendatario_sqlite import (
                RepositorioArrendatarioSQLite,
            )
            from src.infraestructura.persistencia.repositorio_codeudor_sqlite import (
                RepositorioCodeudorSQLite,
            )

            repo_mandato = RepositorioContratoMandatoSQLite(db_manager)
            repo_arriendo = RepositorioContratoArrendamientoSQLite(db_manager)
            repo_propiedad = RepositorioPropiedadSQLite(db_manager)
            repo_renovacion = RepositorioRenovacionSQLite(db_manager)
            repo_ipc = RepositorioIPCSQLite(db_manager)
            repo_arrendatario = RepositorioArrendatarioSQLite(db_manager)
            repo_codeudor = RepositorioCodeudorSQLite(db_manager)

            servicio = ServicioContratos(
                db_manager,
                repo_mandato=repo_mandato,
                repo_arriendo=repo_arriendo,
                repo_propiedad=repo_propiedad,
                repo_renovacion=repo_renovacion,
                repo_ipc=repo_ipc,
                repo_arrendatario=repo_arrendatario,
                repo_codeudor=repo_codeudor,
            )
            usuario_sistema = "admin"  # TODO: Obtener de AuthState

            # Procesar datos del formulario según el tipo
            if self.modal_mode == "crear_mandato" or self.modal_mode == "editar_mandato":
                # Convertir tipos para mandato
                datos_procesados = {
                    "id_propiedad": int(form_data["id_propiedad"]),
                    "id_propietario": int(form_data["id_propietario"]),
                    "id_asesor": int(form_data["id_asesor"]),
                    "fecha_inicio": form_data["fecha_inicio"],
                    "fecha_fin": form_data["fecha_fin"],
                    "fecha_pago": form_data.get("fecha_pago"),
                    "duracion_meses": int(form_data["duracion_meses"]),
                    "canon": int(form_data["canon"]),
                    "comision_porcentaje": int(
                        float(form_data["comision_porcentaje"]) * 100
                    ),  # Convertir % a base 10000
                    "iva_porcentaje": int(
                        float(form_data.get("iva_porcentaje", 19)) * 100
                    ),  # Convertir % a base 10000
                }

                if self.modal_mode == "crear_mandato":
                    servicio.crear_mandato(datos_procesados, usuario_sistema)
                else:
                    servicio.actualizar_mandato(self.editing_id, datos_procesados, usuario_sistema)

            elif (
                self.modal_mode == "crear_arrendamiento"
                or self.modal_mode == "editar_arrendamiento"
            ):
                # Convertir tipos para arrendamiento
                datos_procesados = {
                    "id_propiedad": int(form_data["id_propiedad"]),
                    "id_arrendatario": int(form_data["id_arrendatario"]),
                    "id_codeudor": (
                        int(form_data["id_codeudor"]) if form_data.get("id_codeudor") else None
                    ),
                    "fecha_inicio": form_data["fecha_inicio"],
                    "fecha_fin": form_data["fecha_fin"],
                    "duracion_meses": int(form_data["duracion_meses"]),
                    "canon": int(form_data["canon"]),
                    "deposito": int(form_data.get("deposito", 0)),
                }

                if self.modal_mode == "crear_arrendamiento":
                    servicio.crear_arrendamiento(datos_procesados, usuario_sistema)
                else:
                    servicio.actualizar_arrendamiento(
                        self.editing_id, datos_procesados, usuario_sistema
                    )

            async with self:
                self.modal_open = False
                self.editing_id = None
                self.form_data = {}

            # Recargar lista
            yield ContratosState.load_contratos()

            # Notificación de éxito
            yield rx.toast.success(
                "El contrato ha sido guardado exitosamente.", position="bottom-right"
            )

        except ValueError as e:
            async with self:
                self.error_message = str(e)
            yield rx.toast.error(f"Error de validación: {str(e)}", position="bottom-right")
        except Exception as e:
            async with self:
                self.error_message = f"Error al guardar: {str(e)}"
            yield rx.toast.error(f"Error inesperado: {str(e)}", position="bottom-right")
        finally:
            async with self:
                self.is_loading = False

    # Renovación
    show_renewal_confirm: bool = False
    selected_contract_id_renew: Optional[int] = None
    selected_contract_type_renew: str = ""

    def confirm_renewal(self, id_contrato: int, tipo: str):
        """Abre dialogo de confirmación de renovación."""
        self.selected_contract_id_renew = id_contrato
        self.selected_contract_type_renew = tipo
        self.show_renewal_confirm = True

    def cancel_renewal(self):
        """Cierra dialogo de confirmación."""
        self.show_renewal_confirm = False
        self.selected_contract_id_renew = None
        self.selected_contract_type_renew = ""

    @rx.event(background=True)
    async def execute_renewal(self):
        """Ejecuta la renovación del contrato seleccionado."""
        async with self:
            self.show_renewal_confirm = False  # Cerrar dialogo inmediatamente
            self.is_loading = True

        try:
            from src.infraestructura.persistencia.repositorio_propiedad_sqlite import RepositorioPropiedadSQLite
            from src.infraestructura.persistencia.repositorio_contrato_mandato_sqlite import RepositorioContratoMandatoSQLite
            from src.infraestructura.persistencia.repositorio_contrato_arrendamiento_sqlite import RepositorioContratoArrendamientoSQLite
            from src.infraestructura.persistencia.repositorio_renovacion_sqlite import RepositorioRenovacionSQLite
            from src.infraestructura.persistencia.repositorio_ipc_sqlite import RepositorioIPCSQLite
            from src.infraestructura.persistencia.repositorio_arrendatario_sqlite import RepositorioArrendatarioSQLite
            from src.infraestructura.persistencia.repositorio_codeudor_sqlite import RepositorioCodeudorSQLite

            repo_propiedad = RepositorioPropiedadSQLite(db_manager)
            repo_mandato = RepositorioContratoMandatoSQLite(db_manager)
            repo_arriendo = RepositorioContratoArrendamientoSQLite(db_manager)
            repo_renovacion = RepositorioRenovacionSQLite(db_manager)
            repo_ipc = RepositorioIPCSQLite(db_manager)
            repo_arrendatario = RepositorioArrendatarioSQLite(db_manager)
            repo_codeudor = RepositorioCodeudorSQLite(db_manager)

            servicio = ServicioContratos(
                db_manager,
                repo_mandato=repo_mandato,
                repo_arriendo=repo_arriendo,
                repo_propiedad=repo_propiedad,
                repo_renovacion=repo_renovacion,
                repo_ipc=repo_ipc,
                repo_arrendatario=repo_arrendatario,
                repo_codeudor=repo_codeudor
            )
            usuario_sistema = "admin"  # TODO: Auth

            tipo = self.selected_contract_type_renew
            id_contrato = self.selected_contract_id_renew

            resultado_msg = ""

            if tipo == "Arrendamiento":
                contrato_renovado = servicio.renovar_arrendamiento(id_contrato, usuario_sistema)
                resultado_msg = f"Arrendamiento renovado. Nuevo Canon: ${contrato_renovado.canon_arrendamiento}, Fin: {contrato_renovado.fecha_fin_contrato_a}"
            elif tipo == "Mandato":
                contrato_renovado = servicio.renovar_mandato(id_contrato, usuario_sistema)
                resultado_msg = f"Mandato renovado. Fin: {contrato_renovado.fecha_fin_contrato_m}"

            # Recargar lista
            yield ContratosState.load_contratos()
            yield rx.toast.success(resultado_msg, position="bottom-right")

        except Exception as e:
            yield rx.toast.error(f"Error al renovar: {str(e)}", position="bottom-right")

        finally:
            async with self:
                self.is_loading = False
                self.selected_contract_id_renew = None
                self.selected_contract_type_renew = ""

    def exportar_csv(self):
        """Genera y descarga el CSV de contratos."""
        try:
            # Instanciar repositorios y servicio
            from src.infraestructura.persistencia.repositorio_contrato_mandato_sqlite import (
                RepositorioContratoMandatoSQLite,
            )
            from src.infraestructura.persistencia.repositorio_contrato_arrendamiento_sqlite import (
                RepositorioContratoArrendamientoSQLite,
            )
            from src.infraestructura.persistencia.repositorio_propiedad_sqlite import (
                RepositorioPropiedadSQLite,
            )
            from src.infraestructura.persistencia.repositorio_renovacion_sqlite import (
                RepositorioRenovacionSQLite,
            )
            from src.infraestructura.persistencia.repositorio_ipc_sqlite import RepositorioIPCSQLite
            from src.infraestructura.persistencia.repositorio_arrendatario_sqlite import (
                RepositorioArrendatarioSQLite,
            )
            from src.infraestructura.persistencia.repositorio_codeudor_sqlite import (
                RepositorioCodeudorSQLite,
            )

            repo_mandato = RepositorioContratoMandatoSQLite(db_manager)
            repo_arriendo = RepositorioContratoArrendamientoSQLite(db_manager)
            repo_propiedad = RepositorioPropiedadSQLite(db_manager)
            repo_renovacion = RepositorioRenovacionSQLite(db_manager)
            repo_ipc = RepositorioIPCSQLite(db_manager)
            repo_arrendatario = RepositorioArrendatarioSQLite(db_manager)
            repo_codeudor = RepositorioCodeudorSQLite(db_manager)

            servicio = ServicioContratos(
                repo_mandato=repo_mandato,
                repo_arriendo=repo_arriendo,
                repo_propiedad=repo_propiedad,
                repo_renovacion=repo_renovacion,
                repo_ipc=repo_ipc,
                repo_arrendatario=repo_arrendatario,
                repo_codeudor=repo_codeudor,
            )

            # Obtener datos CSV usando los filtros actuales
            csv_data = servicio.exportar_contratos_csv(
                filtro_tipo=self.filter_tipo,
                estado=self.filter_estado if self.filter_estado != "Todos" else None,
                busqueda=self.search_text if self.search_text else None,
            )

            # Preparar descarga
            import time

            timestamp = int(time.time())
            filename = f"reporte_contratos_{timestamp}.csv"

            # Convertir a bytes para descarga
            if isinstance(csv_data, str):
                data_bytes = csv_data.encode("utf-8-sig")
            else:
                data_bytes = csv_data

            yield rx.download(data=data_bytes, filename=filename)
            yield rx.toast.success("Descarga iniciada", position="bottom-right")

        except Exception as e:
            pass  # print(f"Error exportando CSV: {e}") [OpSec Removed]
            yield rx.toast.error(f"Error al exportar: {str(e)}", position="bottom-right")

    @rx.event(background=True)
    async def toggle_estado(self, id_contrato: int, tipo: str, estado_actual: str):
        """Cambia estado de un contrato (Activo <-> Cancelado)."""
        async with self:
            self.is_loading = True
            self.error_message = ""

        try:
            # Instanciar repositorios y servicio
            from src.infraestructura.persistencia.repositorio_contrato_mandato_sqlite import (
                RepositorioContratoMandatoSQLite,
            )
            from src.infraestructura.persistencia.repositorio_contrato_arrendamiento_sqlite import (
                RepositorioContratoArrendamientoSQLite,
            )
            from src.infraestructura.persistencia.repositorio_propiedad_sqlite import (
                RepositorioPropiedadSQLite,
            )
            from src.infraestructura.persistencia.repositorio_renovacion_sqlite import (
                RepositorioRenovacionSQLite,
            )
            from src.infraestructura.persistencia.repositorio_ipc_sqlite import RepositorioIPCSQLite
            from src.infraestructura.persistencia.repositorio_arrendatario_sqlite import (
                RepositorioArrendatarioSQLite,
            )
            from src.infraestructura.persistencia.repositorio_codeudor_sqlite import (
                RepositorioCodeudorSQLite,
            )

            repo_mandato = RepositorioContratoMandatoSQLite(db_manager)
            repo_arriendo = RepositorioContratoArrendamientoSQLite(db_manager)
            repo_propiedad = RepositorioPropiedadSQLite(db_manager)
            repo_renovacion = RepositorioRenovacionSQLite(db_manager)
            repo_ipc = RepositorioIPCSQLite(db_manager)
            repo_arrendatario = RepositorioArrendatarioSQLite(db_manager)
            repo_codeudor = RepositorioCodeudorSQLite(db_manager)

            servicio = ServicioContratos(
                repo_mandato=repo_mandato,
                repo_arriendo=repo_arriendo,
                repo_propiedad=repo_propiedad,
                repo_renovacion=repo_renovacion,
                repo_ipc=repo_ipc,
                repo_arrendatario=repo_arrendatario,
                repo_codeudor=repo_codeudor,
            )
            usuario_sistema = "admin"  # TODO: Obtener de AuthState

            if estado_actual == "Activo":
                # Cancelar contrato
                motivo = "Cancelación manual desde interfaz"
                if tipo == "Mandato":
                    servicio.terminar_mandato(id_contrato, motivo, usuario_sistema)
                else:
                    servicio.terminar_arrendamiento(id_contrato, motivo, usuario_sistema)
            else:
                # No implementado: reactivar contrato cancelado
                # Por ahora solo permitimos desactivar
                async with self:
                    self.error_message = "No se puede reactivar un contrato cancelado"
                    self.is_loading = False
                return

            # Recargar lista
            yield ContratosState.load_contratos()
            yield rx.toast.info(
                f"Contrato {estado_actual.lower()} desactivado/cancelado.", position="bottom-right"
            )

        except Exception as e:
            async with self:
                self.error_message = f"Error al cambiar estado: {str(e)}"
            yield rx.toast.error(f"Error al cambiar estado: {str(e)}", position="bottom-right")
        finally:
            async with self:
                self.is_loading = False

    # =========================================================================
    # IPC INCREMENT HANDLERS
    # =========================================================================

    def open_ipc_modal(self, id_contrato: int):
        """Abre modal para aplicar incremento IPC."""
        from datetime import datetime

        self.ipc_target_contrato_id = id_contrato
        self.form_data = {
            "porcentaje_ipc": "5.62",
            "fecha_aplicacion": datetime.now().strftime("%Y-%m-%d"),
            "observaciones": "",
        }
        self.show_ipc_modal = True

    def close_ipc_modal(self):
        """Cierra modal de IPC."""
        self.show_ipc_modal = False
        self.ipc_target_contrato_id = 0
        self.form_data = {}
        self.error_message = ""

    @rx.event(background=True)
    async def apply_ipc_increment(self, form_data: Dict):
        """Aplica incremento IPC al contrato seleccionado."""
        async with self:
            self.is_loading = True
            self.error_message = ""

        try:
            porcentaje = float(form_data.get("porcentaje_ipc", 0))
            fecha = form_data.get("fecha_aplicacion", "")
            observaciones = form_data.get("observaciones", "")

            from src.aplicacion.servicios.servicio_contratos import ServicioContratos
            from src.infraestructura.persistencia.database import db_manager

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

                # Recargar contratos
                yield ContratosState.load_contratos()
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
