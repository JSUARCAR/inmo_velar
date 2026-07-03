import pydantic
from typing import Any, Dict, List, Optional

import reflex as rx

from src.aplicacion.servicios.servicio_financiero import ServicioFinanciero
from src.infraestructura.persistencia.database import db_manager
from src.presentacion_reflex.state.documentos_mixin import DocumentosStateMixin
from src.presentacion_reflex.utils.formatters import format_currency


class LiquidacionDict(pydantic.BaseModel):
    """Estructura tipada para serialización de Liquidación en Reflex."""

    id: int
    periodo: str
    contrato: Optional[str] = "N/D"
    propiedad: Optional[str] = "N/D"
    propietario: Optional[str] = "N/D"
    documento: Optional[str] = "N/D"
    id_propietario: Optional[int] = 0
    estado: Optional[str] = "Desconocido"
    canon: Optional[float] = 0.0
    neto: Optional[float] = 0.0
    canon_view: Optional[str] = "$0"
    neto_view: Optional[str] = "$0"
    cantidad_propiedades: Optional[int] = 1
    grupo_operativo: int = 0
    estado_recaudo: str = "Sin Recaudo"


class LiquidacionesState(DocumentosStateMixin):
    """Estado para gestión de liquidaciones de propietarios.
    Maneja paginación, filtros, CRUD y transiciones de estado.
    """

    # Paginación
    current_page: int = 1
    page_size: int = 25
    total_items: int = 0

    # Datos
    liquidaciones: List[LiquidacionDict] = []
    liquidacion_actual: Optional[Dict[str, Any]] = None  # Para vista de detalle
    is_loading: bool = False
    error_message: str = ""

    # Búsqueda y Filtros
    search_text: str = ""
    filter_periodo: str = ""  # YYYY-MM format
    filter_estado: str = "Todos"
    filter_asesor_id: str = "Todos"
    filter_propiedad_id: str = ""
    filter_propietario_id: str = ""

    # Opciones de filtros (para dropdowns)
    estado_options: List[str] = [
        "Todos",
        "En Proceso",
        "Aprobada",
        "Pagada",
        "Cancelada",
    ]
    periodos_options: List[str] = []  # Se llenarán dinámicamente
    propiedades_options: List[Dict[str, Any]] = []
    propietarios_options: List[Dict[str, Any]] = []

    # Select options (listas simples para rx.select - evitar VarTypeError)
    periodos_select_options: List[str] = []
    propiedades_select_options: List[str] = []
    propietarios_select_options: List[str] = []  # Strings "Nombre - Documento"
    asesores_select_options: List[str] = ["Todos"]

    # Combobox Propiedad (formulario de creación de liquidación)
    propiedad_liq_search: str = ""
    propiedad_liq_menu_open: bool = False
    propiedad_liq_selected_label: str = ""

    # Vista agrupada/consolidada
    vista_agrupada: bool = False  # False = Individual, True = Por propietario

    # Ordenamiento
    sort_by: str = "periodo"
    sort_order: str = "desc"

    # Modales
    show_detail_modal: bool = False
    show_create_modal: bool = False
    show_edit_modal: bool = False
    show_payment_modal: bool = False
    show_bulk_create_modal: bool = False  # Modal para generar masivas
    show_cancel_modal: bool = False  # Modal para cancelar individual
    show_reverse_confirm: bool = False  # Confirmación para reversar
    show_reverse_pago_confirm: bool = False  # Confirmación para reversar pago
    reverse_pago_liquidacion_id: int = 0  # ID de liquidación para reversar pago
    reverse_pago_motivo: str = ""  # Motivo de reversión de pago
    show_export_modal: bool = False  # Modal para seleccionar periodo de exportación
    show_delete_modal: bool = False  # Modal para eliminar liquidación
    liquidacion_id_for_delete: int = 0  # ID de liquidación a eliminar
    delete_confirmed: bool = False  # Checkbox de confirmación de eliminación
    
    # Eliminación agrupada
    show_group_delete_modal: bool = False  # Modal para eliminar grupo de liquidaciones
    group_delete_id_propietario: int = 0  # ID del propietario del grupo
    group_delete_periodo: str = ""  # Período del grupo a eliminar
    group_delete_confirmed: bool = False  # Checkbox de confirmación de eliminación agrupada

    # --- INCIDENT ASSOCIATION MODAL (US2) ---
    show_seleccion_incidentes_modal: bool = False
    seleccion_incidentes_liquidacion_id: Optional[int] = None
    seleccion_incidentes_disponibles: List[Dict[str, Any]] = []
    seleccion_incidentes_seleccionados: List[Dict[str, Any]] = []
    seleccion_incidentes_total_descuentos: int = 0
    seleccion_incidentes_error: str = ""
    seleccion_incidentes_loading: bool = False

    # Exportación
    exportando_periodo: bool = False

    # Propiedades en vista consolidada
    propiedades_consolidadas: List[Dict[str, Any]] = []

    # Form data
    form_data: Dict[str, Any] = {}

    # Cancel/Reverse data
    cancel_motivo: str = ""
    liquidacion_id_for_action: int = 0  # ID de liquidación para acción pendiente
    selected_liquidaciones_ids: List[
        int
    ] = []  # IDs seleccionados para acciones masivas

    @staticmethod
    def parse_int_safe(value: Any, default: int = 0) -> int:
        """Convierte de forma segura valores numéricos provenientes de JS."""
        if value in (None, "undefined", "null", ""):
            return default
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return default

    @rx.var
    def detalles_ingresos(self) -> List[Dict[str, Any]]:
        """Devuelve la lista de ingresos tipeada para rx.foreach."""
        if self.liquidacion_actual and "ingresos" in self.liquidacion_actual:
            return self.liquidacion_actual["ingresos"]
        return []

    @rx.event(background=True)
    async def on_load(self):
        """Carga inicial al montar la página."""
        async with self:
            self.is_loading = True

        try:
            # Cargar opciones de filtros
            await self.load_filter_options()
            # Cargar liquidaciones
            await self.load_liquidaciones()
        finally:
            async with self:
                self.is_loading = False

    async def load_filter_options(self):
        """Carga opciones para dropdowns de filtros."""
        from datetime import datetime

        from dateutil.relativedelta import relativedelta

        # Generar últimos 24 periodos (meses)
        today = datetime.now()
        periodos = []
        for i in range(24):
            periodo = (today - relativedelta(months=i)).strftime("%Y-%m")
            periodos.append(periodo)

        # Cargar propiedades (solo con contratos de mandato activos)
        query_propiedades = """
        SELECT DISTINCT p.ID_PROPIEDAD, p.MATRICULA_INMOBILIARIA, p.DIRECCION_PROPIEDAD
        FROM PROPIEDADES p
        INNER JOIN CONTRATOS_MANDATOS cm ON p.ID_PROPIEDAD = cm.ID_PROPIEDAD
        WHERE cm.ESTADO_CONTRATO_M = 'ACTIVO'
        ORDER BY p.DIRECCION_PROPIEDAD
        """

        # Cargar propietarios (con contratos activos)
        query_propietarios = """
        SELECT DISTINCT prop.ID_PROPIETARIO, per.ID_PERSONA, per.NOMBRE_COMPLETO, per.NUMERO_DOCUMENTO
        FROM PERSONAS per
        INNER JOIN PROPIETARIOS prop ON per.ID_PERSONA = prop.ID_PERSONA
        INNER JOIN CONTRATOS_MANDATOS cm ON prop.ID_PROPIETARIO = cm.ID_PROPIETARIO
        WHERE cm.ESTADO_CONTRATO_M = 'ACTIVO'
        ORDER BY per.NOMBRE_COMPLETO
        """

        with db_manager.obtener_conexion() as conn:
            cursor = db_manager.get_dict_cursor(conn)

            # Propiedades
            cursor.execute(query_propiedades)
            rows_propiedades = cursor.fetchall()
            propiedades = [
                {
                    "id": str(row["ID_PROPIEDAD"]),
                    "texto": f"{row['DIRECCION_PROPIEDAD']}",
                }
                for row in rows_propiedades
            ]
            propiedades_select = [
                f"{row['DIRECCION_PROPIEDAD']}" for row in rows_propiedades
            ]

            # Propietarios
            cursor.execute(query_propietarios)
            rows_propietarios = cursor.fetchall()
            propietarios = [
                {
                    "id": str(row["ID_PROPIETARIO"]),
                    "texto": f"{row['NOMBRE_COMPLETO']}",
                }
                for row in rows_propietarios
            ]
            # Para rx.select: solo strings formateados (se parseará en backend)
            propietarios_select = [
                f"{row['NOMBRE_COMPLETO']}" for row in rows_propietarios
            ]

        async with self:
            self.periodos_options = ["Todos"] + periodos
            self.periodos_select_options = ["Todos"] + periodos
            self.propiedades_options = propiedades
            self.propiedades_select_options = propiedades_select
            self.propietarios_options = propietarios
            self.propietarios_select_options = propietarios_select

        # Cargar asesores
        await self.load_asesores_options()

    async def load_asesores_options(self):
        """Carga los asesores para el select de filtros de forma segura en fondo."""
        query = """
            SELECT a.ID_ASESOR, p.NOMBRE_COMPLETO 
            FROM ASESORES a 
            JOIN PERSONAS p ON a.ID_PERSONA = p.ID_PERSONA 
            WHERE p.ESTADO_REGISTRO IS TRUE AND a.ESTADO IS TRUE
            ORDER BY p.NOMBRE_COMPLETO
        """
        try:
            # Obtener datos de BD (sin bloquear el hilo principal)
            with db_manager.obtener_conexion() as conn:
                cursor = db_manager.get_dict_cursor(conn)
                cursor.execute(query)
                rows = cursor.fetchall()

            # Formatear fuera del lock para eficiencia
            opciones = ["Todos"] + [
                f"{r['NOMBRE_COMPLETO']} ({r['ID_ASESOR']})" for r in rows
            ]

            # Actualizar estado de forma segura
            async with self:
                self.asesores_select_options = opciones

        except Exception as e:
            print(f"Error cargando asesores: {e}")

    async def load_liquidaciones(self):
        """Carga liquidaciones con filtros y paginación (modo individual o agrupado)."""
        async with self:
            self.is_loading = True
            self.error_message = ""

        try:
            servicio = ServicioFinanciero(db_manager)

            # Preparar filtros
            periodo = (
                self.filter_periodo
                if self.filter_periodo and self.filter_periodo != "Todos"
                else None
            )
            estado = self.filter_estado if self.filter_estado != "Todos" else None
            busqueda = self.search_text.strip() if self.search_text else None

            # Resolver ID de asesor si no es "Todos"
            id_asesor_filt = None
            if self.filter_asesor_id != "Todos":
                try:
                    id_asesor_filt = int(
                        self.filter_asesor_id.split("(")[-1].replace(")", "")
                    )
                except Exception:
                    pass

            # Llamar al servicio según el modo de vista
            if self.vista_agrupada:
                # Vista consolidada por propietario
                resultado = servicio.listar_liquidaciones_propietarios_paginado(
                    page=self.current_page,
                    page_size=self.page_size,
                    periodo=periodo,
                    estado=estado,
                    busqueda=busqueda,
                    id_asesor=id_asesor_filt,
                    sort_by=self.sort_by,
                    sort_order=self.sort_order,
                )
            else:
                # Vista individual por propiedad
                resultado = servicio.listar_liquidaciones_paginado(
                    page=self.current_page,
                    page_size=self.page_size,
                    periodo=periodo,
                    estado=estado,
                    busqueda=busqueda,
                    id_asesor=id_asesor_filt,
                    sort_by=self.sort_by,
                    sort_order=self.sort_order,
                )

            async with self:
                # Aplicar formateo a los items de la lista
                formatted_items = []
                for item in resultado.items:
                    new_item = item.copy()
                    # Guardamos versiones formateadas para la UI
                    new_item["canon_view"] = format_currency(item.get("canon", 0))
                    new_item["neto_view"] = format_currency(item.get("neto", 0))
                    new_item["grupo_operativo"] = item.get("grupo_operativo", 0)
                    formatted_items.append(new_item)

                self.liquidaciones = formatted_items
                self.total_items = resultado.total
                self.is_loading = False

        except Exception as e:
            async with self:
                self.error_message = f"Error al cargar liquidaciones: {str(e)}"
                self.liquidaciones = []
                self.total_items = 0
                self.is_loading = False

    def toggle_sort(self, column: str):
        """Cambia el criterio de ordenamiento."""
        if self.sort_by == column:
            self.sort_order = "desc" if self.sort_order == "asc" else "asc"
        else:
            self.sort_by = column
            self.sort_order = "desc"

        self.current_page = 1
        return LiquidacionesState.load_liquidaciones

    # Paginación
    def next_page(self):
        """Avanza a la siguiente página."""
        if self.current_page * self.page_size < self.total_items:
            self.current_page += 1
            return LiquidacionesState.load_liquidaciones

    def prev_page(self):
        """Retrocede a la página anterior."""
        if self.current_page > 1:
            self.current_page -= 1
            return LiquidacionesState.load_liquidaciones

    def set_page_size(self, size: str):
        """Cambia el tamaño de página."""
        self.page_size = int(size)
        self.current_page = 1
        return LiquidacionesState.load_liquidaciones

    # Búsqueda y Filtros
    def set_search(self, value: str):
        """Actualiza búsqueda."""
        self.search_text = value

    def search_liquidaciones(self):
        """Ejecuta búsqueda."""
        self.current_page = 1
        return LiquidacionesState.load_liquidaciones

    def handle_search_key_down(self, key: str):
        """Maneja el evento de teclado en el campo de búsqueda."""
        if key == "Enter":
            return self.search_liquidaciones()

    def set_filter_periodo(self, value: str):
        """Cambia filtro de período."""
        self.filter_periodo = value
        self.current_page = 1
        return LiquidacionesState.load_liquidaciones

    def set_filter_estado(self, value: str):
        """Cambia filtro de estado."""
        self.filter_estado = value
        self.current_page = 1
        return LiquidacionesState.load_liquidaciones

    def set_filter_asesor(self, value: str):
        """Cambia filtro de asesor comercial."""
        self.filter_asesor_id = value
        self.current_page = 1
        return LiquidacionesState.load_liquidaciones

    def set_filter_propiedad(self, value: str):
        """Cambia filtro de propiedad."""
        self.filter_propiedad_id = value
        self.current_page = 1
        return LiquidacionesState.load_liquidaciones

    def set_filter_propietario(self, value: str):
        """Cambia filtro de propietario."""
        self.filter_propietario_id = value
        self.current_page = 1
        return LiquidacionesState.load_liquidaciones

    # Modal CRUD
    def open_create_modal(self):
        """Abre modal para crear nueva liquidación."""
        self.show_create_modal = True
        self.show_detail_modal = False
        self.show_edit_modal = False
        self.show_payment_modal = False
        self.form_data = {
            "id_contrato_m": "",
            "canon_mandato": "",
            "nombre_propietario": "",
            "direccion_propiedad": "",
            "periodo": "",
            "otros_ingresos": "0",
            "gastos_administracion": "0",
            "gastos_servicios": "0",
            "gastos_reparaciones": "0",
            "pago_predial": "0",
            "otros_egresos": "0",
            "observaciones": "",
            "estado": "",
        }
        self.error_message = ""
        # Reset combobox propiedad
        self.propiedad_liq_selected_label = ""
        self.propiedad_liq_search = ""
        self.propiedad_liq_menu_open = False

    def set_form_field(self, field: str, value: str):
        """Actualiza un campo del formulario."""
        self.form_data[field] = value

    # -------------------------------------------------------------------------
    # Combobox Propiedad (formulario de creación de liquidación)
    # -------------------------------------------------------------------------
    def set_propiedad_liq_search(self, value: str):
        """Actualiza el texto de búsqueda en el combobox de propiedad."""
        self.propiedad_liq_search = value

    def toggle_propiedad_liq_menu(self, open: bool):
        """Abre/cierra el popover del combobox de propiedad."""
        self.propiedad_liq_menu_open = open

    def select_propiedad_liq(self, id_propiedad: str, label: str):
        """Selecciona una propiedad en el combobox y dispara la carga de datos."""
        self.propiedad_liq_selected_label = label
        self.propiedad_liq_menu_open = False
        self.propiedad_liq_search = ""
        return LiquidacionesState.handle_propiedad_change(label)

    @rx.var
    def filtered_propiedades_liq_options(self) -> List[List[str]]:
        """Filtra las opciones de propiedad según el texto de búsqueda."""
        opts = self.propiedades_options
        search = self.propiedad_liq_search.lower()
        result = []
        for opt in opts:
            texto = opt.get("texto", "")
            id_ = opt.get("id", "")
            if not search or search in texto.lower():
                result.append([texto, id_])
        return result

    @rx.event(background=True)
    async def handle_propiedad_change(self, valor_seleccionado: str):
        """
        Maneja el cambio de propiedad en el formulario de creación.
        Busca el contrato de mandato activo y el valor de administración.

        Args:
            valor_seleccionado: El TEXTO de la opción seleccionada (debido a cómo funciona rx.select con listas simples)
        """
        if not valor_seleccionado:
            return

        # Buscar el ID real de la propiedad basado en el texto seleccionado
        id_propiedad = None
        for prop in self.propiedades_options:
            if prop["texto"] == valor_seleccionado:
                id_propiedad = prop["id"]
                break

        if not id_propiedad:
            # Si no se encuentra (no debería pasar), abortar o loguear
            return

        async with self:
            self.form_data["id_propiedad"] = (
                valor_seleccionado  # Guardamos el texto para que el select lo muestre
            )
            # Reset values
            self.form_data["id_contrato_m"] = ""
            self.form_data["gastos_administracion"] = "0"

        try:
            with db_manager.obtener_conexion() as conn:
                cursor = db_manager.get_dict_cursor(conn)
                placeholder = db_manager.get_placeholder()

                # 1. Buscar Contrato Mandato Activo con info extra
                query_mandato = f"""
                SELECT 
                    cm.ID_CONTRATO_M, 
                    cm.CANON_MANDATO,
                    p.DIRECCION_PROPIEDAD,
                    per.NOMBRE_COMPLETO as NOMBRE_PROPIETARIO
                FROM CONTRATOS_MANDATOS cm
                JOIN PROPIEDADES p ON cm.ID_PROPIEDAD = p.ID_PROPIEDAD
                JOIN PROPIETARIOS prop ON cm.ID_PROPIETARIO = prop.ID_PROPIETARIO
                JOIN PERSONAS per ON prop.ID_PERSONA = per.ID_PERSONA
                WHERE cm.ID_PROPIEDAD = {placeholder} AND cm.ESTADO_CONTRATO_M = 'ACTIVO'
                LIMIT 1
                """
                cursor.execute(query_mandato, (id_propiedad,))
                mandato = cursor.fetchone()

                # 2. Buscar Valor Administración de la Propiedad (Backup si no estuviera en join)
                query_prop = f"""
                SELECT VALOR_ADMINISTRACION
                FROM PROPIEDADES
                WHERE ID_PROPIEDAD = {placeholder}
                """
                cursor.execute(query_prop, (id_propiedad,))
                propiedad = cursor.fetchone()

            async with self:
                if mandato:
                    self.form_data["id_contrato_m"] = str(mandato["ID_CONTRATO_M"])
                    self.form_data["canon_mandato"] = (
                        f"${mandato['CANON_MANDATO']:,}".replace(",", ".")
                    )
                    self.form_data["direccion_propiedad"] = mandato[
                        "DIRECCION_PROPIEDAD"
                    ]
                    self.form_data["nombre_propietario"] = mandato["NOMBRE_PROPIETARIO"]

                # Cargar Gastos Administración si tiene valor
                if propiedad and propiedad["VALOR_ADMINISTRACION"] is not None:
                    valor_admin = propiedad["VALOR_ADMINISTRACION"]
                    # Convertir a string para el formulario
                    try:
                        self.form_data["gastos_administracion"] = str(
                            int(float(valor_admin))
                        )
                    except (ValueError, TypeError):
                        self.form_data["gastos_administracion"] = str(valor_admin)
                else:
                    self.form_data["gastos_administracion"] = "0"

                # Forzar actualización de la UI reutilizando el diccionario
                self.form_data = self.form_data.copy()

        except Exception as e:
            print(f"Error fetching contract details: {e}")

    @rx.event(background=True)
    async def open_edit_modal(self, id_liquidacion: int):
        """Abre modal para editar liquidación existente."""
        async with self:
            self.is_loading = True
            self.error_message = ""

        try:
            servicio = ServicioFinanciero(db_manager)
            liquidacion = servicio.obtener_detalle_liquidacion_ui(id_liquidacion)

            if liquidacion:
                # Verificar que esté En Proceso
                if liquidacion["estado"] != "En Proceso":
                    async with self:
                        self.error_message = (
                            "Solo se pueden editar liquidaciones en estado 'En Proceso'"
                        )
                        self.is_loading = False
                    return

                async with self:
                    self.form_data = {
                        "id_liquidacion": str(id_liquidacion),
                        "nombre_propietario": str(liquidacion.get("propietario", "")),
                        "direccion_propiedad": str(liquidacion.get("propiedad", "")),
                        "canon_mandato": str(liquidacion.get("canon", 0)),
                        "id_contrato_m": str(liquidacion["id_contrato"]),
                        "periodo": str(liquidacion["periodo"]),
                        "otros_ingresos": str(liquidacion.get("otros_ingresos", 0)),
                        "gastos_administracion": str(
                            liquidacion["gastos_admin"]
                            if liquidacion.get("gastos_admin", 0) > 0
                            else int(
                                float(liquidacion.get("valor_administracion") or 0)
                            )
                        ),
                        "gastos_servicios": str(liquidacion.get("gastos_serv", 0)),
                        "gastos_reparaciones": str(liquidacion.get("gastos_rep", 0)),
                        "pago_predial": str(liquidacion.get("pago_predial", 0)),
                        "otros_egresos": str(liquidacion.get("otros_egr", 0)),
                        "observaciones": str(liquidacion.get("observaciones", "")),
                        "valor_incidentes": str(liquidacion.get("valor_incidentes", 0)),
                        "estado": str(liquidacion.get("estado", "")),
                    }
                    self.show_edit_modal = True
                    self.show_create_modal = False
                    self.show_detail_modal = False
                    self.show_payment_modal = False
                    self.is_loading = False
        except Exception as e:
            async with self:
                self.error_message = f"Error al cargar liquidación: {str(e)}"
                self.is_loading = False

    @rx.event(background=True)
    async def open_detail_modal(self, id_liquidacion: int):
        """Abre modal con el detalle completo de la liquidación."""
        async with self:
            self.is_loading = True
            self.error_message = ""
            # Limpiar propiedades consolidadas para vista individual
            self.propiedades_consolidadas = []

            # Contexto Documental
            self.iniciar_contexto_documental("LIQUIDACION", str(id_liquidacion))

        try:
            servicio = ServicioFinanciero(db_manager)
            liquidacion = servicio.obtener_detalle_liquidacion_ui(id_liquidacion)

            if liquidacion:
                # Formatear valores financieros para el detalle
                l_fmt = liquidacion.copy()
                l_fmt["canon_view"] = format_currency(liquidacion.get("canon", 0))
                l_fmt["neto_pagar_view"] = format_currency(
                    liquidacion.get("neto_pagar", 0)
                )
                l_fmt["total_ingresos_view"] = format_currency(
                    liquidacion.get("total_ingresos", 0)
                )
                l_fmt["total_egresos_view"] = format_currency(
                    liquidacion.get("total_egresos", 0)
                )
                l_fmt["comision_monto_view"] = format_currency(
                    liquidacion.get("comision_monto", 0)
                )
                l_fmt["iva_comision_view"] = format_currency(
                    liquidacion.get("iva_comision", 0)
                )
                l_fmt["impuesto_4x1000_view"] = format_currency(
                    liquidacion.get("impuesto_4x1000", 0)
                )
                l_fmt["gastos_admin_view"] = format_currency(
                    liquidacion.get("gastos_admin", 0)
                )
                l_fmt["gastos_serv_view"] = format_currency(
                    liquidacion.get("gastos_serv", 0)
                )
                l_fmt["gastos_rep_view"] = format_currency(
                    liquidacion.get("gastos_rep", 0)
                )
                l_fmt["pago_predial_view"] = format_currency(
                    liquidacion.get("pago_predial", 0)
                )
                l_fmt["seguro_monto_view"] = format_currency(
                    liquidacion.get("seguro_monto", 0)
                )
                l_fmt["otros_egr_view"] = format_currency(
                    liquidacion.get("otros_egr", 0)
                )
                l_fmt["valor_incidentes_view"] = format_currency(
                    liquidacion.get("valor_incidentes", 0)
                )

                # Formatear listas internas si existen
                if "propiedades_detalle" in l_fmt:
                    for p in l_fmt["propiedades_detalle"]:
                        p["canon_view"] = format_currency(p.get("canon", 0))
                        p["neto_view"] = format_currency(p.get("neto", 0))

                if "ingresos" in l_fmt:
                    for ing in l_fmt["ingresos"]:
                        ing["valor_view"] = format_currency(ing.get("valor", 0))

                async with self:
                    self.liquidacion_actual = l_fmt
                    self.show_detail_modal = True
                    self.show_create_modal = False
                    self.show_edit_modal = False
                    self.show_payment_modal = False
                    self.is_loading = False
        except Exception as e:
            async with self:
                self.error_message = f"Error al cargar detalle: {str(e)}"
                self.is_loading = False

    @rx.event(background=True)
    async def open_detail_consolidated(self, id_propietario: int, periodo: str):
        """Abre modal con liquidaciones consolidadas del propietario para el período."""
        async with self:
            self.is_loading = True
            self.error_message = ""

        try:
            # Usar repositorio directamente
            from src.infraestructura.persistencia.database import db_manager as dm
            from src.infraestructura.persistencia.repositorio_liquidacion_postgres import (
                RepositorioLiquidacionPostgres,
            )

            repo = RepositorioLiquidacionPostgres(dm)
            liquidaciones = repo.listar_por_propietario_y_periodo(
                id_propietario, periodo
            )

            if liquidaciones and len(liquidaciones) > 0:
                # Obtener detalles de TODAS las liquidaciones y consolidar
                servicio = ServicioFinanciero(db_manager)
                detalles_lista = []

                for liq in liquidaciones:
                    detalle = servicio.obtener_detalle_liquidacion_ui(
                        liq.id_liquidacion
                    )
                    if detalle:
                        detalles_lista.append(detalle)

                if detalles_lista:
                    # Crear liquidación consolidada sumando todos los valores
                    consolidado = {
                        "id": detalles_lista[0]["id"],  # ID de referencia
                        "periodo": periodo,
                        "fecha_generacion": detalles_lista[0]["fecha_generacion"],
                        "estado": detalles_lista[0]["estado"],
                        "observaciones": f"Consolidado de {len(detalles_lista)} propiedades",
                        # Contexto del propietario
                        "propietario": detalles_lista[0]["propietario"],
                        "documento": detalles_lista[0]["documento"],
                        "propiedad": f"{len(detalles_lista)} propiedades",  # Mostrar cantidad
                        "matricula": "Múltiples",
                        # Lista detallada de cada propiedad
                        "propiedades_detalle": [
                            {
                                "direccion": d["propiedad"],
                                "matricula": d["matricula"],
                                "canon": d["canon"],
                                "neto": d["neto_pagar"],
                            }
                            for d in detalles_lista
                        ],
                        # Sumar todos los valores financieros
                        "canon": sum(d["canon"] for d in detalles_lista),
                        "otros_ingresos": sum(
                            d["otros_ingresos"] for d in detalles_lista
                        ),
                        "total_ingresos": sum(
                            d["total_ingresos"] for d in detalles_lista
                        ),
                        "comision_pct": detalles_lista[0][
                            "comision_pct"
                        ],  # Mismo % para todos
                        "comision_pct_view": f"{int(detalles_lista[0]['comision_pct'])}%",
                        "comision_monto": sum(
                            d["comision_monto"] for d in detalles_lista
                        ),
                        "iva_comision": sum(d["iva_comision"] for d in detalles_lista),
                        "impuesto_4x1000": sum(
                            d["impuesto_4x1000"] for d in detalles_lista
                        ),
                        "gastos_admin": sum(
                            d.get("gastos_admin", 0) for d in detalles_lista
                        ),
                        "gastos_serv": sum(
                            d.get("gastos_serv", 0) for d in detalles_lista
                        ),
                        "gastos_rep": sum(
                            d.get("gastos_rep", 0) for d in detalles_lista
                        ),
                        "pago_predial": sum(
                            d.get("pago_predial", 0) for d in detalles_lista
                        ),
                        "otros_egr": sum(d.get("otros_egr", 0) for d in detalles_lista),
                        "total_egresos": sum(
                            d.get("total_egresos", 0) for d in detalles_lista
                        ),
                        "neto_pagar": sum(d["neto_pagar"] for d in detalles_lista),
                        # Formatted View Values
                        "comision_monto_view": format_currency(
                            sum(d["comision_monto"] for d in detalles_lista)
                        ),
                        "iva_comision_view": format_currency(
                            sum(d["iva_comision"] for d in detalles_lista)
                        ),
                        "impuesto_4x1000_view": format_currency(
                            sum(d["impuesto_4x1000"] for d in detalles_lista)
                        ),
                        "gastos_admin_view": format_currency(
                            sum(d.get("gastos_admin", 0) for d in detalles_lista)
                        ),
                        "gastos_serv_view": format_currency(
                            sum(d.get("gastos_serv", 0) for d in detalles_lista)
                        ),
                        "gastos_rep_view": format_currency(
                            sum(d.get("gastos_rep", 0) for d in detalles_lista)
                        ),
                        "pago_predial_view": format_currency(
                            sum(d.get("pago_predial", 0) for d in detalles_lista)
                        ),
                        "otros_egr_view": format_currency(
                            sum(d.get("otros_egr", 0) for d in detalles_lista)
                        ),
                        "total_egresos_view": format_currency(
                            sum(d.get("total_egresos", 0) for d in detalles_lista)
                        ),
                        "neto_pagar_view": format_currency(
                            sum(d["neto_pagar"] for d in detalles_lista)
                        ),
                        # Pago
                        "fecha_pago": detalles_lista[0].get("fecha_pago"),
                        "metodo_pago": detalles_lista[0].get("metodo_pago"),
                        "referencia_pago": detalles_lista[0].get("referencia_pago"),
                        # Auditoría
                        "created_at": detalles_lista[0]["created_at"],
                        "created_by": detalles_lista[0]["created_by"],
                    }

                    async with self:
                        self.liquidacion_actual = consolidado
                        self.propiedades_consolidadas = consolidado[
                            "propiedades_detalle"
                        ]
                        self.show_detail_modal = True
                        self.is_loading = False
                else:
                    raise ValueError(
                        "No se pudo cargar el detalle de las liquidaciones"
                    )
            else:
                async with self:
                    self.error_message = "No hay liquidaciones para este propietario en el período seleccionado"
                    self.is_loading = False
        except Exception as e:
            async with self:
                self.error_message = f"Error al cargar detalle consolidado: {str(e)}"
                self.is_loading = False

    def open_payment_modal(self, id_liquidacion: int):
        """Abre modal para registrar el pago de una liquidación aprobada."""
        from datetime import datetime

        # Prellenar con fecha de hoy
        self.form_data = {
            "id_liquidacion": id_liquidacion,
            "fecha_pago": datetime.now().date().isoformat(),
            "metodo_pago": "Transferencia Electrónica",
            "referencia_pago": "",
        }
        self.show_payment_modal = True
        self.show_detail_modal = False
        self.show_create_modal = False
        self.show_edit_modal = False
        self.error_message = ""

    def open_payment_modal_bulk(self, id_propietario: int, periodo: str):
        """Abre modal para registrar el pago masivo de liquidaciones de un propietario."""
        from datetime import datetime

        # Prellenar con fecha de hoy y datos del propietario
        self.form_data = {
            "id_propietario": id_propietario,
            "periodo": periodo,
            "fecha_pago": datetime.now().date().isoformat(),
            "metodo_pago": "Transferencia Electrónica",
            "referencia_pago": "",
        }
        self.show_payment_modal = True
        self.show_detail_modal = False
        self.show_create_modal = False
        self.show_edit_modal = False
        self.show_bulk_create_modal = False
        self.error_message = ""

    def close_modal(self):
        """Cierra todos los modales."""
        self.show_detail_modal = False
        self.show_create_modal = False
        self.show_edit_modal = False
        self.show_payment_modal = False
        self.show_bulk_create_modal = False
        self.liquidacion_actual = None
        self.form_data = {}
        self.error_message = ""

    # =========================================================================
    # FUNCIONALIDAD DE LIQUIDACIONES MASIVAS POR PROPIETARIO
    # =========================================================================

    def toggle_vista_agrupada(self):
        """Alterna entre vista individual y vista consolidada por propietario."""
        self.vista_agrupada = not self.vista_agrupada
        self.current_page = 1
        return LiquidacionesState.load_liquidaciones

    def open_bulk_create_modal(self):
        """Abre modal para generar liquidación masiva de TODOS los propietarios."""
        from datetime import datetime

        periodo_actual = datetime.now().strftime("%Y-%m")

        self.show_bulk_create_modal = True
        self.show_detail_modal = False
        self.show_create_modal = False
        self.show_edit_modal = False
        self.show_payment_modal = False
        self.form_data = {
            "periodo": periodo_actual,
        }
        self.error_message = ""

    @rx.event(background=True)
    async def generar_liquidacion_masiva(self, form_data: Dict):
        """Genera liquidaciones consolidadas para TODAS las propiedades de TODOS los propietarios."""
        async with self:
            self.is_loading = True
            self.error_message = ""
            vista_agrupada = self.vista_agrupada

        try:
            servicio = ServicioFinanciero(db_manager)
            usuario_sistema = "admin"  # TODO: Obtener de AuthState

            periodo = form_data.get("periodo", "")

            if not periodo:
                raise ValueError("Debe seleccionar un período")

            # Buscar TODOS los ID_PROPIETARIO con contratos activos
            id_propietarios_activos = []
            with db_manager.obtener_conexion() as conn:
                cursor = db_manager.get_dict_cursor(conn)
                query = """
                SELECT DISTINCT prop.ID_PROPIETARIO
                FROM PROPIETARIOS prop
                INNER JOIN CONTRATOS_MANDATOS cm ON prop.ID_PROPIETARIO = cm.ID_PROPIETARIO
                WHERE cm.ESTADO_CONTRATO_M = 'ACTIVO'
                """
                cursor.execute(query)
                rows = cursor.fetchall()
                id_propietarios_activos = [row["ID_PROPIETARIO"] for row in rows]

            if not id_propietarios_activos:
                raise ValueError(
                    "No se encontraron propietarios con contratos de mandato activos"
                )

            generadas = 0
            errores = 0

            # Generar liquidación consolidada para cada propietario
            for id_propietario in id_propietarios_activos:
                try:
                    servicio.generar_liquidacion_propietario(
                        id_propietario=id_propietario,
                        periodo=periodo,
                        datos_adicionales_por_contrato=None,
                        usuario_sistema=usuario_sistema,
                    )
                    generadas += 1
                except Exception as e:
                    print(
                        f"Error generando liquidacion masiva para id_propietario={id_propietario}: {e}"
                    )
                    errores += 1

            if generadas == 0 and errores > 0:
                raise ValueError("Hubo errores generando todas las liquidaciones.")

            async with self:
                self.show_bulk_create_modal = False
                self.form_data = {}

            # Si estamos en vista agrupada, recargar
            if vista_agrupada:
                yield LiquidacionesState.load_liquidaciones()

        except ValueError as e:
            async with self:
                self.error_message = str(e)
        except Exception as e:
            async with self:
                self.error_message = f"Error al generar liquidación masiva: {str(e)}"
        finally:
            async with self:
                self.is_loading = False
                error_msg = self.error_message

            if not error_msg:
                mensaje = f"Se generaron {generadas} liquidaciones exitosamente."
                if errores > 0:
                    mensaje += f" (Omitidas/Error: {errores})"
                yield rx.toast.success(mensaje, position="bottom-right")
            else:
                yield rx.toast.error(error_msg, position="bottom-right")

    @rx.event(background=True)
    async def aprobar_liquidacion_masiva(self, id_propietario: int, periodo: str):
        """Aprueba todas las liquidaciones de un propietario para un período."""
        async with self:
            self.is_loading = True
            self.error_message = ""

        try:
            servicio = ServicioFinanciero(db_manager)
            usuario_sistema = "admin"  # TODO: Obtener de AuthState

            affected = servicio.aprobar_liquidacion_propietario(
                id_propietario=id_propietario,
                periodo=periodo,
                usuario_sistema=usuario_sistema,
            )

            async with self:
                self.show_detail_modal = False
                self.is_loading = False

            # Recargar lista
            yield LiquidacionesState.load_liquidaciones()

        except Exception as e:
            async with self:
                self.error_message = f"Error al aprobar liquidación masiva: {str(e)}"
                self.is_loading = False
            yield rx.toast.error(self.error_message, position="bottom-right")
            return

        yield rx.toast.success(
            f"Se aprobaron {affected} liquidaciones", position="bottom-right"
        )

    @rx.event(background=True)
    async def marcar_como_pagada_masiva(self, form_data: Dict):
        """Marca como pagadas todas las liquidaciones de un propietario para un período."""
        async with self:
            self.is_loading = True
            self.error_message = ""

        try:
            servicio = ServicioFinanciero(db_manager)
            usuario_sistema = "admin"  # TODO: Obtener de AuthState

            affected = servicio.marcar_liquidacion_propietario_pagada(
                id_propietario=int(form_data["id_propietario"]),
                periodo=form_data["periodo"],
                fecha_pago=form_data["fecha_pago"],
                metodo_pago=form_data["metodo_pago"],
                referencia_pago=form_data["referencia_pago"],
                usuario_sistema=usuario_sistema,
            )

            async with self:
                self.show_payment_modal = False
                self.form_data = {}
                self.is_loading = False

            # Recargar lista
            yield LiquidacionesState.load_liquidaciones()

        except Exception as e:
            async with self:
                self.error_message = f"Error al registrar pago masivo: {str(e)}"
                self.is_loading = False
            yield rx.toast.error(self.error_message, position="bottom-right")
            return

        yield rx.toast.success(
            f"Se registraron {affected} pagos correctamente", position="bottom-right"
        )

    @rx.event(background=True)
    async def save_liquidacion(self, form_data: Dict):
        """Guarda liquidación (crear o editar)."""
        async with self:
            self.is_loading = True
            self.error_message = ""
            is_create_mode = self.show_create_modal

        try:
            servicio = ServicioFinanciero(db_manager)
            usuario_sistema = "admin"  # TODO: Obtener de AuthState

            # Procesar datos del formulario
            datos_procesados = {
                "otros_ingresos": LiquidacionesState.parse_int_safe(form_data.get("otros_ingresos")),
                "gastos_administracion": LiquidacionesState.parse_int_safe(form_data.get("gastos_administracion")),
                "gastos_servicios": LiquidacionesState.parse_int_safe(form_data.get("gastos_servicios")),
                "valor_incidentes": LiquidacionesState.parse_int_safe(form_data.get("valor_incidentes")),
                "pago_predial": LiquidacionesState.parse_int_safe(form_data.get("pago_predial")),
                "otros_egresos": LiquidacionesState.parse_int_safe(form_data.get("otros_egresos")),
                "observaciones": form_data.get("observaciones", ""),
            }

            if is_create_mode:
                # Crear nueva liquidación
                id_contrato_m = LiquidacionesState.parse_int_safe(form_data.get("id_contrato_m"), default=-1)
                if id_contrato_m <= 0:
                    raise ValueError("El ID del contrato es obligatorio. Por favor seleccione una propiedad válida.")
                
                datos_procesados["id_contrato_m"] = id_contrato_m
                datos_procesados["periodo"] = form_data.get("periodo", "")
                servicio.generar_liquidacion_mensual(
                    id_contrato_m=datos_procesados["id_contrato_m"],
                    periodo=datos_procesados["periodo"],
                    datos_adicionales=datos_procesados,
                    usuario_sistema=usuario_sistema,
                )
            else:  # Editar
                id_liquidacion = form_data.get("id_liquidacion")
                if id_liquidacion:
                    servicio.actualizar_liquidacion(
                        id_liquidacion=int(id_liquidacion),
                        datos_actualizados=datos_procesados,
                        usuario_sistema=usuario_sistema,
                    )

            async with self:
                self.show_create_modal = False
                self.show_edit_modal = False
                self.form_data = {}

            # Recargar lista
            yield LiquidacionesState.load_liquidaciones()

        except ValueError as e:
            async with self:
                self.error_message = str(e)
        except Exception as e:
            async with self:
                self.error_message = f"Error al guardar: {str(e)}"
        finally:
            async with self:
                self.is_loading = False
                error_msg = self.error_message

            if not error_msg:
                yield rx.toast.success(
                    "Liquidación guardada correctamente", position="bottom-right"
                )
            else:
                yield rx.toast.error(error_msg, position="bottom-right")

    @rx.event(background=True)
    async def aprobar_liquidacion(self, id_liquidacion: int):
        """Aprueba una liquidación (En Proceso → Aprobada)."""
        async with self:
            self.is_loading = True
            self.error_message = ""

        try:
            servicio = ServicioFinanciero(db_manager)
            usuario_sistema = "admin"  # TODO: Obtener de AuthState

            servicio.aprobar_liquidacion(id_liquidacion, usuario_sistema)

            async with self:
                self.show_detail_modal = False
                self.is_loading = False

            # Recargar lista
            yield LiquidacionesState.load_liquidaciones()

        except Exception as e:
            async with self:
                self.error_message = f"Error al aprobar: {str(e)}"
                self.is_loading = False
            yield rx.toast.error(self.error_message, position="bottom-right")
            return

        yield rx.toast.success(
            "Liquidación aprobada correctamente", position="bottom-right"
        )

    @rx.event(background=True)
    async def marcar_como_pagada(self, form_data: Dict):
        """Marca una liquidación como pagada (Aprobada → Pagada)."""
        async with self:
            self.is_loading = True
            self.error_message = ""

        try:
            servicio = ServicioFinanciero(db_manager)
            usuario_sistema = "admin"  # TODO: Obtener de AuthState

            servicio.marcar_liquidacion_pagada(
                id_liquidacion=int(form_data["id_liquidacion"]),
                fecha_pago=form_data["fecha_pago"],
                metodo_pago=form_data["metodo_pago"],
                referencia_pago=form_data["referencia_pago"],
                usuario_sistema=usuario_sistema,
            )

            # US4: Actualizar estado de pago de incidentes asociados
            try:
                from src.infraestructura.persistencia.repositorio_plan_pago_postgres import (
                    RepositorioPlanPagoPostgres,
                )
                from src.infraestructura.persistencia.repositorio_cuota_postgres import (
                    RepositorioCuotaPostgres,
                )
                from src.infraestructura.persistencia.repositorio_incidente_liq_postgres import (
                    RepositorioIncidenteLiquidacionPostgres,
                )
                from src.infraestructura.persistencia.repositorio_incidentes_postgres import (
                    RepositorioIncidentesPostgres,
                )
                from src.aplicacion.servicios.servicio_estado_pago import (
                    ServicioEstadoPagoAutomatico,
                )

                servicio_estado = ServicioEstadoPagoAutomatico(
                    repositorio_plan=RepositorioPlanPagoPostgres(db_manager),
                    repositorio_cuota=RepositorioCuotaPostgres(db_manager),
                    repositorio_relacion=RepositorioIncidenteLiquidacionPostgres(db_manager),
                    repositorio_incidentes=RepositorioIncidentesPostgres(db_manager),
                )
                servicio_estado.actualizar_estado_pago_por_liquidacion(
                    id_liquidacion=int(form_data["id_liquidacion"]),
                    usuario=usuario_sistema,
                )
            except Exception as e_estado:
                # No fallar el pago principal por error en actualización de estado
                import logging
                logging.getLogger(__name__).warning(
                    f"Error al actualizar estado de pago de incidentes: {e_estado}"
                )

            async with self:
                self.show_payment_modal = False
                self.form_data = {}
                self.is_loading = False

            # Recargar lista
            yield LiquidacionesState.load_liquidaciones()

        except Exception as e:
            async with self:
                self.error_message = f"Error al registrar pago: {str(e)}"
                self.is_loading = False
            yield rx.toast.error(self.error_message, position="bottom-right")
            return

        yield rx.toast.success("Pago registrado exitosamente", position="bottom-right")

    @rx.event(background=True)
    async def cancelar_liquidacion(self, id_liquidacion: int, motivo: str):
        """Cancela una liquidación."""
        async with self:
            self.is_loading = True
            self.error_message = ""

        try:
            servicio = ServicioFinanciero(db_manager)
            usuario_sistema = "admin"  # TODO: Obtener de AuthState

            if not motivo or len(motivo.strip()) < 10:
                async with self:
                    self.error_message = (
                        "El motivo de cancelación debe tener al menos 10 caracteres"
                    )
                    self.is_loading = False
                return

            servicio.cancelar_liquidacion(id_liquidacion, motivo, usuario_sistema)

            async with self:
                self.show_detail_modal = False
                self.is_loading = False

            # Recargar lista
            yield LiquidacionesState.load_liquidaciones()

        except Exception as e:
            async with self:
                self.error_message = f"Error al cancelar: {str(e)}"
                self.is_loading = False

    # =========================================================================
    # REVERSAR LIQUIDACIONES
    # =========================================================================

    def open_reverse_confirm(self, id_liquidacion: int):
        self.liquidacion_id_for_action = id_liquidacion
        self.show_reverse_confirm = True

    def close_reverse_confirm(self):
        self.show_reverse_confirm = False
        self.liquidacion_id_for_action = 0

    @rx.event(background=True)
    async def confirmar_reversar(self):
        async with self:
            self.is_loading = True
            self.error_message = ""

        try:
            servicio = ServicioFinanciero(db_manager)
            servicio.reversar_liquidacion(self.liquidacion_id_for_action, "admin")

            async with self:
                self.show_reverse_confirm = False
                self.show_detail_modal = False
                self.is_loading = False
                self.form_data = {}  # Limpieza de Estado (Post-Reversión)

            yield LiquidacionesState.load_liquidaciones()

        except Exception as e:
            async with self:
                self.error_message = f"Error al reversar: {str(e)}"
                self.is_loading = False
            yield rx.toast.error(self.error_message, position="bottom-right")
            return

        yield rx.toast.success(
            "Liquidación reversada a 'En Proceso'", position="bottom-right"
        )

    def set_cancel_motivo(self, value: str):
        self.cancel_motivo = value

    # =========================================================================
    # REVERSAR PAGO DE LIQUIDACIONES (Pagada → Aprobada)
    # =========================================================================

    def open_reverse_pago_confirm(self, id_liquidacion: int):
        """Abre modal de confirmación para reversar pago de liquidación."""
        self.reverse_pago_liquidacion_id = id_liquidacion
        self.reverse_pago_motivo = ""
        self.error_message = ""
        self.show_reverse_pago_confirm = True

    def close_reverse_pago_confirm(self):
        """Cierra modal de confirmación de reversión de pago."""
        self.show_reverse_pago_confirm = False
        self.reverse_pago_liquidacion_id = 0
        self.reverse_pago_motivo = ""
        self.error_message = ""

    def set_reverse_pago_motivo(self, value: str):
        """Actualiza el motivo de reversión de pago."""
        self.reverse_pago_motivo = value

    @rx.event(background=True)
    async def confirmar_reversar_pago(self):
        """Ejecuta la reversión de pago de una liquidación individual."""
        async with self:
            self.is_loading = True
            self.error_message = ""

        try:
            if not self.reverse_pago_motivo or len(self.reverse_pago_motivo.strip()) < 10:
                async with self:
                    self.error_message = "El motivo debe tener al menos 10 caracteres"
                    self.is_loading = False
                yield rx.toast.warning(
                    "El motivo es muy corto", position="bottom-right"
                )
                return

            servicio = ServicioFinanciero(db_manager)
            result = servicio.reversar_pago_liquidacion(
                self.reverse_pago_liquidacion_id, "admin", self.reverse_pago_motivo
            )

            # US5: Revertir estado de pago de incidentes asociados
            try:
                from src.infraestructura.persistencia.repositorio_plan_pago_postgres import (
                    RepositorioPlanPagoPostgres,
                )
                from src.infraestructura.persistencia.repositorio_cuota_postgres import (
                    RepositorioCuotaPostgres,
                )
                from src.infraestructura.persistencia.repositorio_incidente_liq_postgres import (
                    RepositorioIncidenteLiquidacionPostgres,
                )
                from src.infraestructura.persistencia.repositorio_incidentes_postgres import (
                    RepositorioIncidentesPostgres,
                )
                from src.aplicacion.servicios.servicio_estado_pago import (
                    ServicioEstadoPagoAutomatico,
                )

                servicio_estado = ServicioEstadoPagoAutomatico(
                    repositorio_plan=RepositorioPlanPagoPostgres(db_manager),
                    repositorio_cuota=RepositorioCuotaPostgres(db_manager),
                    repositorio_relacion=RepositorioIncidenteLiquidacionPostgres(db_manager),
                    repositorio_incidentes=RepositorioIncidentesPostgres(db_manager),
                )
                servicio_estado.revertir_estado_pago_por_liquidacion(
                    id_liquidacion=self.reverse_pago_liquidacion_id,
                    usuario="admin",
                )
            except Exception as e_estado:
                import logging
                logging.getLogger(__name__).warning(
                    f"Error al revertir estado de pago de incidentes: {e_estado}"
                )

            async with self:
                self.show_reverse_pago_confirm = False
                self.show_detail_modal = False
                self.reverse_pago_liquidacion_id = 0
                self.reverse_pago_motivo = ""
                self.is_loading = False

            yield LiquidacionesState.load_liquidaciones()

        except Exception as e:
            async with self:
                self.error_message = f"Error al reversar pago: {str(e)}"
                self.is_loading = False
            yield rx.toast.error(self.error_message, position="bottom-right")
            return

        yield rx.toast.success(
            "Pago reversado exitosamente", position="bottom-right"
        )

    @rx.event(background=True)
    async def confirmar_reversar_pago_masivo(self):
        """Ejecuta la reversión de pagos de liquidaciones de un propietario para un período."""
        async with self:
            self.is_loading = True
            self.error_message = ""

        try:
            if not self.reverse_pago_motivo or len(self.reverse_pago_motivo.strip()) < 10:
                async with self:
                    self.error_message = "El motivo debe tener al menos 10 caracteres"
                    self.is_loading = False
                yield rx.toast.warning(
                    "El motivo es muy corto", position="bottom-right"
                )
                return

            servicio = ServicioFinanciero(db_manager)
            result = servicio.reversar_pago_propietario(
                self.form_data.get("id_propietario"),
                self.form_data.get("periodo"),
                "admin",
                self.reverse_pago_motivo,
            )

            # US5: Revertir estado de pago de incidentes asociados a todas las liquidaciones revertidas
            try:
                from src.infraestructura.persistencia.repositorio_plan_pago_postgres import (
                    RepositorioPlanPagoPostgres,
                )
                from src.infraestructura.persistencia.repositorio_cuota_postgres import (
                    RepositorioCuotaPostgres,
                )
                from src.infraestructura.persistencia.repositorio_incidente_liq_postgres import (
                    RepositorioIncidenteLiquidacionPostgres,
                )
                from src.infraestructura.persistencia.repositorio_incidentes_postgres import (
                    RepositorioIncidentesPostgres,
                )
                from src.aplicacion.servicios.servicio_estado_pago import (
                    ServicioEstadoPagoAutomatico,
                )

                servicio_estado = ServicioEstadoPagoAutomatico(
                    repositorio_plan=RepositorioPlanPagoPostgres(db_manager),
                    repositorio_cuota=RepositorioCuotaPostgres(db_manager),
                    repositorio_relacion=RepositorioIncidenteLiquidacionPostgres(db_manager),
                    repositorio_incidentes=RepositorioIncidentesPostgres(db_manager),
                )
                # Actualizar estados de pago para cada liquidación revertida
                if result and "liquidaciones_revertidas" in result:
                    for liq in result["liquidaciones_revertidas"]:
                        servicio_estado.revertir_estado_pago_por_liquidacion(
                            id_liquidacion=liq["id"],
                            usuario="admin",
                        )
            except Exception as e_estado:
                import logging
                logging.getLogger(__name__).warning(
                    f"Error al revertir estados de pago de incidentes: {e_estado}"
                )

            async with self:
                self.show_reverse_pago_confirm = False
                self.reverse_pago_motivo = ""
                self.is_loading = False

            yield LiquidacionesState.load_liquidaciones()

            total = result.get("total_reversadas", 0)
            if total > 0:
                yield rx.toast.success(
                    f"Se reversaron {total} pagos exitosamente", position="bottom-right"
                )
            else:
                yield rx.toast.info(
                    "No se encontraron pagos para reversar", position="bottom-right"
                )

        except Exception as e:
            async with self:
                self.error_message = f"Error al reversar pagos: {str(e)}"
                self.is_loading = False
            yield rx.toast.error(self.error_message, position="bottom-right")

    def open_cancel_modal(self, id_liquidacion: int):
        """Abre modal para cancelar liquidación"""
        self.liquidacion_id_for_action = id_liquidacion
        self.cancel_motivo = ""
        self.error_message = ""
        self.show_cancel_modal = True

    def close_cancel_modal(self):
        """Cierra modal de cancelación"""
        self.show_cancel_modal = False
        self.cancel_motivo = ""
        self.error_message = ""
        self.liquidacion_id_for_action = 0

    @rx.event(background=True)
    async def confirmar_cancelacion(self):
        """Ejecuta cancelación de liquidación individual"""
        async with self:
            self.is_loading = True
            self.error_message = ""

        try:
            if not self.cancel_motivo or len(self.cancel_motivo.strip()) < 10:
                async with self:
                    self.error_message = "El motivo debe tener al menos 10 caracteres"
                    self.is_loading = False
                yield rx.toast.warning(
                    "El motivo es muy corto", position="bottom-right"
                )
                return

            servicio = ServicioFinanciero(db_manager)
            servicio.cancelar_liquidacion(
                self.liquidacion_id_for_action, self.cancel_motivo, "admin"
            )

            async with self:
                self.show_cancel_modal = False
                self.show_detail_modal = False
                self.cancel_motivo = ""
                self.is_loading = False

            yield LiquidacionesState.load_liquidaciones()

        except Exception as e:
            async with self:
                self.error_message = f"Error al cancelar: {str(e)}"
                self.is_loading = False
            yield rx.toast.error(self.error_message, position="bottom-right")
            return

        yield rx.toast.success(
            "Liquidación cancelada correctamente", position="bottom-right"
        )

    # =========================================================================
    # ELIMINAR LIQUIDACIONES (Soft Delete)
    # =========================================================================

    def open_delete_modal(self, id_liquidacion: int):
        """Abre modal para eliminar liquidación"""
        self.liquidacion_id_for_delete = id_liquidacion
        self.delete_confirmed = False
        self.error_message = ""
        
        # Buscar la liquidación en la lista actual para mostrar datos en el diálogo
        for liq in self.liquidaciones:
            if liq.get("id") == id_liquidacion:
                self.liquidacion_actual = liq
                break
        
        self.show_delete_modal = True

    def close_delete_modal(self):
        """Cierra modal de eliminación"""
        self.show_delete_modal = False
        self.liquidacion_id_for_delete = 0
        self.delete_confirmed = False
        self.error_message = ""

    def set_delete_confirmed(self, value: bool):
        """Actualiza el estado del checkbox de confirmación"""
        self.delete_confirmed = value

    # =========================================================================
    # ELIMINACIÓN AGRUPADA
    # =========================================================================

    def open_group_delete_modal(self, id_propietario: int, periodo: str):
        """Abre modal para eliminar grupo de liquidaciones"""
        self.group_delete_id_propietario = id_propietario
        self.group_delete_periodo = periodo
        self.group_delete_confirmed = False
        self.error_message = ""
        
        # Buscar datos del propietario para mostrar en el diálogo
        for liq in self.liquidaciones:
            if liq.get("id_propietario") == id_propietario and liq.get("periodo") == periodo:
                self.liquidacion_actual = liq
                break
        
        self.show_group_delete_modal = True

    def close_group_delete_modal(self):
        """Cierra modal de eliminación agrupada"""
        self.show_group_delete_modal = False
        self.group_delete_id_propietario = 0
        self.group_delete_periodo = ""
        self.group_delete_confirmed = False
        self.error_message = ""

    def set_group_delete_confirmed(self, value: bool):
        """Actualiza el estado del checkbox de confirmación de eliminación agrupada"""
        self.group_delete_confirmed = value

    @rx.event(background=True)
    async def confirmar_eliminar_agrupadas(self):
        """Ejecuta eliminación de liquidaciones agrupadas"""
        async with self:
            self.is_loading = True
            self.error_message = ""

        try:
            if not self.group_delete_confirmed:
                async with self:
                    self.error_message = "Debe confirmar la eliminación marcando el checkbox"
                    self.is_loading = False
                return

            # Llamar al método de eliminación agrupada
            async for _ in LiquidacionesState.eliminar_liquidaciones_agrupadas(
                self.group_delete_id_propietario, self.group_delete_periodo
            ):
                pass

            async with self:
                self.show_group_delete_modal = False
                self.group_delete_id_propietario = 0
                self.group_delete_periodo = ""
                self.group_delete_confirmed = False
                self.is_loading = False

        except Exception as e:
            async with self:
                self.error_message = f"Error al eliminar liquidaciones agrupadas: {str(e)}"
                self.is_loading = False
            yield rx.toast.error(self.error_message, position="bottom-right")

    @rx.event(background=True)
    async def confirmar_eliminar(self):
        """Ejecuta eliminación de liquidación individual"""
        async with self:
            self.is_loading = True
            self.error_message = ""

        try:
            if not self.delete_confirmed:
                async with self:
                    self.error_message = "Debe confirmar la eliminación marcando el checkbox"
                    self.is_loading = False
                return

            servicio = ServicioFinanciero(db_manager)
            usuario_sistema = "admin"  # TODO: Obtener de AuthState

            result = servicio.eliminar_liquidacion(
                self.liquidacion_id_for_delete, usuario_sistema
            )

            async with self:
                self.show_delete_modal = False
                self.show_detail_modal = False
                self.liquidacion_id_for_delete = 0
                self.delete_confirmed = False
                self.is_loading = False

            # Recargar lista
            yield LiquidacionesState.load_liquidaciones()

            if result.get("exitosa"):
                yield rx.toast.success(
                    result.get("mensaje", "Liquidación eliminada correctamente"),
                    position="bottom-right",
                )
            else:
                yield rx.toast.info(
                    result.get("mensaje", "Operación completada"),
                    position="bottom-right",
                )

        except ValueError as e:
            async with self:
                self.error_message = str(e)
                self.is_loading = False
            yield rx.toast.error(str(e), position="bottom-right")
        except Exception as e:
            async with self:
                self.error_message = f"Error al eliminar: {str(e)}"
                self.is_loading = False
            yield rx.toast.error(self.error_message, position="bottom-right")

    # =========================================================================
    # ELIMINACIÓN MASIVA (VISTA AGRUPADA)
    # =========================================================================

    @rx.event(background=True)
    async def eliminar_liquidaciones_agrupadas(self, id_propietario: int, periodo: str):
        """
        Elimina todas las liquidaciones no pagadas de un propietario para un período.
        Muestra diálogo de confirmación antes de ejecutar.
        """
        async with self:
            self.is_loading = True
            self.error_message = ""

        try:
            servicio = ServicioFinanciero(db_manager)
            usuario_sistema = "admin"  # TODO: Obtener de AuthState

            # Obtener liquidaciones del grupo
            liquidaciones_grupo = servicio.repo_liquidacion.listar_por_propietario_y_periodo(
                id_propietario, periodo
            )

            if not liquidaciones_grupo:
                async with self:
                    self.is_loading = False
                yield rx.toast.info("No se encontraron liquidaciones para eliminar", position="bottom-right")
                return

            # Filtrar solo las que no están pagadas
            liquidaciones_eliminables = [
                liq for liq in liquidaciones_grupo
                if liq.estado_liquidacion != "Pagada" and not liq.eliminada
            ]

            if not liquidaciones_eliminables:
                async with self:
                    self.is_loading = False
                yield rx.toast.info(
                    "No hay liquidaciones para eliminar (todas están pagadas o ya fueron eliminadas)",
                    position="bottom-right"
                )
                return

            # Eliminar cada liquidación
            eliminadas = 0
            errores = []
            for liq in liquidaciones_eliminables:
                try:
                    servicio.eliminar_liquidacion(liq.id_liquidacion, usuario_sistema)
                    eliminadas += 1
                except Exception as e:
                    errores.append(f"ID {liq.id_liquidacion}: {str(e)}")

            async with self:
                self.is_loading = False

            # Recargar lista
            yield LiquidacionesState.load_liquidaciones()

            if eliminadas > 0:
                yield rx.toast.success(
                    f"Se eliminaron {eliminadas} liquidaciones del período {periodo}",
                    position="bottom-right"
                )

            if errores:
                yield rx.toast.warning(
                    f"Se omitieron {len(errores)} liquidaciones (posiblemente pagadas)",
                    position="bottom-right"
                )

        except Exception as e:
            async with self:
                self.error_message = f"Error al eliminar liquidaciones agrupadas: {str(e)}"
                self.is_loading = False
            yield rx.toast.error(self.error_message, position="bottom-right")

    # =========================================================================
    # EXPORTACIÓN MASIVA
    # =========================================================================

    def open_export_modal(self):
        """Abre modal para exportar liquidaciones del periodo."""
        from datetime import datetime
        self.show_export_modal = True
        # Preseleccionar el periodo actual o el filtrado
        if not self.filter_periodo or self.filter_periodo == "Todos":
             self.filter_periodo = datetime.now().strftime("%Y-%m")

    def close_export_modal(self):
        """Cierra el modal de exportación."""
        self.show_export_modal = False

    @rx.event(background=True)
    async def exportar_liquidaciones_periodo_zip(self):
        """Exporta todas las liquidaciones (consolidadas) de un periodo en un ZIP."""
        async with self:
            self.exportando_periodo = True
            self.error_message = ""
            
            # Usar el periodo filtrado si existe, si no el actual
            periodo = self.filter_periodo
            if not periodo or periodo == "Todos":
                from datetime import datetime
                periodo = datetime.now().strftime("%Y-%m")
        
        try:
            from pathlib import Path
            # Importar dependencias para inyección
            servicio = ServicioFinanciero(db_manager)
            
            # Ejecutar exportación
            zip_path = servicio.exportar_estados_cuenta_periodo_zip(periodo)
            
            # Entregar para descarga usando el script especializado de PDFState
            if zip_path:
                from src.presentacion_reflex.state.pdf_state import PDFState
                yield PDFState.descargar_pdf_script(zip_path)
                yield rx.toast.success(f"Exportación de {periodo} completada", position="bottom-right")
            
            async with self:
                 self.show_export_modal = False

        except Exception as e:
            async with self:
                self.error_message = f"Error al exportar liquidaciones: {str(e)}"
            yield rx.toast.error(self.error_message, position="bottom-right")
        finally:
            async with self:
                self.exportando_periodo = False

    # -------------------------------------------------------------------------
    # INCIDENT ASSOCIATION MODAL (US2) - T043-T045
    # -------------------------------------------------------------------------
    def set_show_seleccion_incidentes_modal(self, value: bool):
        """Setter para el estado del modal de selección de incidentes."""
        self.show_seleccion_incidentes_modal = value

    @rx.event(background=True)
    async def open_seleccion_incidentes_modal(self, id_liquidacion: int):
        """Abre el modal de selección de incidentes para una liquidación."""
        async with self:
            self.seleccion_incidentes_liquidacion_id = id_liquidacion
            self.seleccion_incidentes_error = ""
            self.seleccion_incidentes_seleccionados = []
            self.seleccion_incidentes_total_descuentos = 0
            self.seleccion_incidentes_loading = True
            self.show_seleccion_incidentes_modal = True

        try:
            from src.infraestructura.persistencia.repositorio_incidentes_postgres import (
                RepositorioIncidentesPostgres,
            )
            from src.infraestructura.persistencia.repositorio_plan_pago_postgres import (
                RepositorioPlanPagoPostgres,
            )
            from src.infraestructura.persistencia.repositorio_cuota_postgres import (
                RepositorioCuotaPostgres,
            )
            from src.infraestructura.persistencia.repositorio_incidente_liq_postgres import (
                RepositorioIncidenteLiquidacionPostgres,
            )
            from src.infraestructura.persistencia.database import db_manager as dm

            repo_incidentes = RepositorioIncidentesPostgres(dm)
            repo_plan = RepositorioPlanPagoPostgres(dm)
            repo_cuota = RepositorioCuotaPostgres(dm)
            repo_relacion = RepositorioIncidenteLiquidacionPostgres(dm)

            # 1. Obtener relaciones existentes para esta liquidación
            relaciones_existentes = repo_relacion.obtener_por_liquidacion(id_liquidacion)
            ids_ya_asociados = {r.id_incidente for r in relaciones_existentes}

            # 2. Buscar incidentes elegibles: estado en [Aprobado, En Reparacion, Finalizado]
            #    y estado_pago != Pagado
            incidentes_elegibles = []
            # Usar búsqueda directa con filtros SQL
            conn = dm.obtener_conexion()
            cursor = dm.get_dict_cursor(conn)
            placeholder = dm.get_placeholder()

            query = f"""
                SELECT i.ID_INCIDENTE, i.DESCRIPCION_INCIDENTE, i.COSTO_INCIDENTE,
                       i.ESTADO, i.ESTADO_PAGO,
                       p.DIRECCION_PROPIEDAD as PROPIEDAD,
                       per.NOMBRE_COMPLETO as PROPIETARIO
                FROM INCIDENTES i
                LEFT JOIN PROPIEDADES p ON i.ID_PROPIEDAD = p.ID_PROPIEDAD
                LEFT JOIN CONTRATOS_MANDATOS cm ON (
                    i.ID_CONTRATO_M = cm.ID_CONTRATO_M
                    OR (i.ID_CONTRATO_M IS NULL AND i.ID_PROPIEDAD = cm.ID_PROPIEDAD AND cm.ESTADO_CONTRATO_M = 'ACTIVO')
                )
                LEFT JOIN PROPIETARIOS prop ON cm.ID_PROPIETARIO = prop.ID_PROPIETARIO
                LEFT JOIN PERSONAS per ON prop.ID_PERSONA = per.ID_PERSONA
                WHERE i.ESTADO IN ({placeholder}, {placeholder}, {placeholder})
                  AND i.ESTADO_PAGO != {placeholder}
                ORDER BY i.ID_INCIDENTE DESC
            """
            cursor.execute(
                query,
                ("Aprobado", "En Reparacion", "Finalizado", "Pagado"),
            )
            rows = cursor.fetchall()

            for row in rows:
                id_inc = row["ID_INCIDENTE"]
                # Obtener plan activo y cuota disponible
                plan = repo_plan.obtener_por_incidente(id_inc)
                if not plan:
                    continue  # Sin plan activo, no se puede asociar

                cuotas = repo_cuota.obtener_por_plan(plan.id_plan_pago)
                # Buscar primera cuota que pueda asociarse
                cuota_disponible = None
                for cuota in cuotas:
                    if cuota.puede_asociarse() and cuota.id_liquidacion != id_liquidacion:
                        cuota_disponible = cuota
                        break

                if cuota_disponible is None:
                    continue  # No hay cuotas disponibles

                ya_asociado = id_inc in ids_ya_asociados
                incidentes_elegibles.append({
                    "id": id_inc,
                    "descripcion": row["DESCRIPCION_INCIDENTE"] or f"Incidente #{id_inc}",
                    "costo": row["COSTO_INCIDENTE"] or 0,
                    "costo_view": format_currency(row["COSTO_INCIDENTE"] or 0),
                    "estado": row["ESTADO"],
                    "estado_pago": row["ESTADO_PAGO"] or "Pendiente",
                    "propiedad": row["PROPIEDAD"] or "N/A",
                    "propietario": row["PROPIETARIO"] or "N/A",
                    "num_cuota": cuota_disponible.numero_cuota,
                    "valor_cuota": plan.valor_cuota,
                    "valor_cuota_view": format_currency(plan.valor_cuota),
                    "ya_asociado": ya_asociado,
                })

            async with self:
                self.seleccion_incidentes_disponibles = incidentes_elegibles
                self.seleccion_incidentes_loading = False

        except Exception as e:
            async with self:
                self.seleccion_incidentes_error = f"Error al cargar incidentes: {str(e)}"
                self.seleccion_incidentes_loading = False

    def toggle_seleccion_incidente(self, id_incidente: int):
        """Alterna la selección de un incidente en el modal."""
        seleccionados = list(self.seleccion_incidentes_seleccionados)
        disponibles = self.seleccion_incidentes_disponibles

        # Verificar si ya está seleccionado
        idx = next(
            (i for i, s in enumerate(seleccionados) if s["id"] == id_incidente),
            None,
        )

        if idx is not None:
            # Quitar de selección
            seleccionados.pop(idx)
        else:
            # Agregar a selección
            incidente = next(
                (inc for inc in disponibles if inc["id"] == id_incidente),
                None,
            )
            if incidente and not incidente.get("ya_asociado", False):
                seleccionados.append(incidente)

        # Recalcular total de descuentos
        total = sum(s.get("valor_cuota", 0) for s in seleccionados)

        self.seleccion_incidentes_seleccionados = seleccionados
        self.seleccion_incidentes_total_descuentos = total

    @rx.event(background=True)
    async def asociar_incidentes_seleccionados(self):
        """Asocia los incidentes seleccionados a la liquidación."""
        if not self.seleccion_incidentes_seleccionados:
            async with self:
                self.seleccion_incidentes_error = "Debe seleccionar al menos un incidente"
            return

        async with self:
            self.seleccion_incidentes_loading = True
            self.seleccion_incidentes_error = ""

        try:
            from src.infraestructura.persistencia.repositorio_incidentes_postgres import (
                RepositorioIncidentesPostgres,
            )
            from src.infraestructura.persistencia.repositorio_plan_pago_postgres import (
                RepositorioPlanPagoPostgres,
            )
            from src.infraestructura.persistencia.repositorio_cuota_postgres import (
                RepositorioCuotaPostgres,
            )
            from src.infraestructura.persistencia.repositorio_incidente_liq_postgres import (
                RepositorioIncidenteLiquidacionPostgres,
            )
            from src.infraestructura.persistencia.repositorio_liquidacion_postgres import (
                RepositorioLiquidacionPostgres,
            )
            from src.infraestructura.persistencia.database import db_manager as dm
            from src.core.auth import obtener_usuario_actual_async
            from src.aplicacion.servicios.servicio_incidente_liquidacion import (
                ServicioIncidenteLiquidacion,
            )

            repo_relacion = RepositorioIncidenteLiquidacionPostgres(dm)
            repo_cuota = RepositorioCuotaPostgres(dm)
            repo_plan = RepositorioPlanPagoPostgres(dm)
            repo_liquidacion = RepositorioLiquidacionPostgres(dm)
            repo_incidentes = RepositorioIncidentesPostgres(dm)

            servicio = ServicioIncidenteLiquidacion(
                repositorio_relacion=repo_relacion,
                repositorio_cuota=repo_cuota,
                repositorio_plan=repo_plan,
                repositorio_liquidacion=repo_liquidacion,
                repositorio_incidentes=repo_incidentes,
            )

            usuario = await obtener_usuario_actual_async()
            id_liquidacion = self.seleccion_incidentes_liquidacion_id
            exitosos = 0
            errores = []

            for incidente in self.seleccion_incidentes_seleccionados:
                resultado = servicio.asociar_incidente(
                    id_incidente=incidente["id"],
                    id_liquidacion=id_liquidacion,
                    numero_cuota=incidente["num_cuota"],
                    valor_descuento=incidente["valor_cuota"],
                    asociado_por=usuario,
                )

                if resultado.get("success"):
                    exitosos += 1
                else:
                    errores.append(
                        f"Incidente #{incidente['id']}: {resultado.get('message', 'Error desconocido')}"
                    )

            async with self:
                if errores:
                    self.seleccion_incidentes_error = (
                        f"Asociados: {exitosos}. Errores: {'; '.join(errores)}"
                    )
                else:
                    self.show_seleccion_incidentes_modal = False
                    yield rx.toast.success(
                        f"{exitosos} incidente(s) asociado(s) exitosamente",
                        position="bottom-right",
                    )
                    yield LiquidacionesState.load_liquidaciones()

                self.seleccion_incidentes_loading = False

        except Exception as e:
            async with self:
                self.seleccion_incidentes_error = f"Error al asociar incidentes: {str(e)}"
                self.seleccion_incidentes_loading = False

    def close_seleccion_incidentes_modal(self):
        """Cierra el modal de selección de incidentes."""
        self.show_seleccion_incidentes_modal = False
        self.seleccion_incidentes_liquidacion_id = None
        self.seleccion_incidentes_disponibles = []
        self.seleccion_incidentes_seleccionados = []
        self.seleccion_incidentes_total_descuentos = 0
        self.seleccion_incidentes_error = ""
