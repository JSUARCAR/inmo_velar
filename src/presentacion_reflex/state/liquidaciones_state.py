import reflex as rx
from typing import Optional, Dict, Any, List
from src.infraestructura.persistencia.database import db_manager
from src.aplicacion.servicios.servicio_financiero import ServicioFinanciero


from src.presentacion_reflex.state.documentos_mixin import DocumentosStateMixin

class LiquidacionesState(DocumentosStateMixin):
    """Estado para gestión de liquidaciones de propietarios.
    Maneja paginación, filtros, CRUD y transiciones de estado.
    """
    # Paginación
    current_page: int = 1
    page_size: int = 25
    total_items: int = 0
    
    # Datos
    liquidaciones: List[Dict[str, Any]] = []
    liquidacion_actual: Optional[Dict[str, Any]] = None  # Para vista de detalle
    is_loading: bool = False
    error_message: str = ""
    
    # Búsqueda y Filtros
    search_text: str = ""
    filter_periodo: str = ""  # YYYY-MM format
    filter_estado: str = "Todos"
    filter_propiedad_id: str = ""
    filter_propietario_id: str = ""
    
    # Opciones de filtros (para dropdowns)
    estado_options: List[str] = ["Todos", "En Proceso", "Aprobada", "Pagada", "Cancelada"]
    periodos_options: List[str] = []  # Se llenarán dinámicamente
    propiedades_options: List[Dict[str, Any]] = []
    propietarios_options: List[Dict[str, Any]] = []
    
    # Select options (listas simples para rx.select - evitar VarTypeError)
    periodos_select_options: List[str] = []
    propiedades_select_options: List[str] = []
    propietarios_select_options: List[str] = []  # Strings "Nombre - Documento"
    
    # Vista agrupada/consolidada
    vista_agrupada: bool = False  # False = Individual, True = Por propietario
    
    # Modales
    show_detail_modal: bool = False
    show_create_modal: bool = False
    show_edit_modal: bool = False
    show_payment_modal: bool = False
    show_bulk_create_modal: bool = False  # Modal para generar masivas
    show_cancel_modal: bool = False  # Modal para cancelar individual
    show_reverse_confirm: bool = False  # Confirmación para reversar
    
    # Propiedades en vista consolidada
    propiedades_consolidadas: List[Dict[str, Any]] = []
    
    # Form data
    form_data: Dict[str, Any] = {}
    
    # Cancel/Reverse data
    cancel_motivo: str = ""
    liquidacion_id_for_action: int = 0  # ID de liquidación para acción pendiente
    selected_liquidaciones_ids: List[int] = []  # IDs seleccionados para acciones masivas
    
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
            yield LiquidacionesState.load_filter_options()
            # Cargar liquidaciones
            yield LiquidacionesState.load_liquidaciones()
        finally:
            async with self:
                self.is_loading = False
    
    @rx.event(background=True)
    async def load_filter_options(self):
        """Carga opciones para dropdowns de filtros."""
        from datetime import datetime
        from dateutil.relativedelta import relativedelta
        
        # Generar últimos 24 periodos (meses)
        today = datetime.now()
        periodos = []
        for i in range(24):
            periodo = (today - relativedelta(months=i)).strftime('%Y-%m')
            periodos.append(periodo)
        
        # Cargar propiedades (solo con contratos de mandato activos)
        query_propiedades = """
        SELECT DISTINCT p.ID_PROPIEDAD, p.MATRICULA_INMOBILIARIA, p.DIRECCION_PROPIEDAD
        FROM PROPIEDADES p
        INNER JOIN CONTRATOS_MANDATOS cm ON p.ID_PROPIEDAD = cm.ID_PROPIEDAD
        WHERE cm.ESTADO_CONTRATO_M = 'Activo'
        ORDER BY p.DIRECCION_PROPIEDAD
        """
        
        # Cargar propietarios (con contratos activos)
        query_propietarios = """
        SELECT DISTINCT prop.ID_PROPIETARIO, per.ID_PERSONA, per.NOMBRE_COMPLETO, per.NUMERO_DOCUMENTO
        FROM PERSONAS per
        INNER JOIN PROPIETARIOS prop ON per.ID_PERSONA = prop.ID_PERSONA
        INNER JOIN CONTRATOS_MANDATOS cm ON prop.ID_PROPIETARIO = cm.ID_PROPIETARIO
        WHERE cm.ESTADO_CONTRATO_M = 'Activo'
        ORDER BY per.NOMBRE_COMPLETO
        """
        
        with db_manager.obtener_conexion() as conn:
            cursor = db_manager.get_dict_cursor(conn)
            
            # Propiedades
            cursor.execute(query_propiedades)
            rows_propiedades = cursor.fetchall()
            propiedades = [
                {
                    "id": str(row['ID_PROPIEDAD']),
                    "texto": f"{row['MATRICULA_INMOBILIARIA']} - {row['DIRECCION_PROPIEDAD']}"
                }
                for row in rows_propiedades
            ]
            propiedades_select = [f"{row['MATRICULA_INMOBILIARIA']} - {row['DIRECCION_PROPIEDAD']}" for row in rows_propiedades]
            
            # Propietarios
            cursor.execute(query_propietarios)
            rows_propietarios = cursor.fetchall()
            propietarios = [
                {
                    "id": str(row['ID_PROPIETARIO']),
                    "texto": f"{row['NOMBRE_COMPLETO']} - {row['NUMERO_DOCUMENTO']}"
                }
                for row in rows_propietarios
            ]
            # Para rx.select: solo strings formateados (se parseará en backend)
            propietarios_select = [f"{row['NOMBRE_COMPLETO']} - {row['NUMERO_DOCUMENTO']}" for row in rows_propietarios]
        
        async with self:
            self.periodos_options = ["Todos"] + periodos
            self.periodos_select_options = ["Todos"] + periodos
            self.propiedades_options = propiedades
            self.propiedades_select_options = propiedades_select
            self.propietarios_options = propietarios
            self.propietarios_select_options = propietarios_select
    
    async def load_liquidaciones(self):
        """Carga liquidaciones con filtros y paginación (modo individual o agrupado)."""
        async with self:
            self.is_loading = True
            self.error_message = ""
        
        try:
            servicio = ServicioFinanciero(db_manager)
            
            # Preparar filtros
            periodo = self.filter_periodo if self.filter_periodo and self.filter_periodo != "Todos" else None
            estado = self.filter_estado if self.filter_estado != "Todos" else None
            busqueda = self.search_text.strip() if self.search_text else None
            
            # Llamar al servicio según el modo de vista
            if self.vista_agrupada:
                # Vista consolidada por propietario
                resultado = servicio.listar_liquidaciones_propietarios_paginado(
                    page=self.current_page,
                    page_size=self.page_size,
                    periodo=periodo,
                    estado=estado,
                    busqueda=busqueda
                )
            else:
                # Vista individual por propiedad
                resultado = servicio.listar_liquidaciones_paginado(
                    page=self.current_page,
                    page_size=self.page_size,
                    periodo=periodo,
                    estado=estado,
                    busqueda=busqueda
                )
            
            async with self:
                self.liquidaciones = resultado.items
                self.total_items = resultado.total
                self.is_loading = False
                
        except Exception as e:
            async with self:
                self.error_message = f"Error al cargar liquidaciones: {str(e)}"
                self.liquidaciones = []
                self.total_items = 0
                self.is_loading = False
    
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
    
    def open_bulk_create_modal(self):
        """Abre modal para generar liquidación masiva por propietario."""
        from datetime import datetime
        
        # Asegurar que las opciones estén cargadas
        if not self.propietarios_select_options:
            return self.load_filter_options()
        
        # Prellenar con periodo actual
        self.form_data = {
            "id_propietario": "",
            "periodo": datetime.now().strftime('%Y-%m')
        }
        self.show_bulk_create_modal = True
        self.show_create_modal = False
        self.show_edit_modal = False
        self.show_detail_modal = False
        self.show_payment_modal = False
        self.error_message = ""
    
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
            "otros_ingresos": 0,
            "gastos_administracion": 0,
            "gastos_servicios": 0,
            "gastos_reparaciones": 0,
            "otros_egresos": 0,
            "observaciones": ""
        }
        self.error_message = ""

    def set_form_field(self, field: str, value: str):
        """Actualiza un campo del formulario."""
        self.form_data[field] = value

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
            self.form_data["id_propiedad"] = valor_seleccionado # Guardamos el texto para que el select lo muestre
            # Reset values
            self.form_data["id_contrato_m"] = ""
            self.form_data["gastos_administracion"] = 0

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
                WHERE cm.ID_PROPIEDAD = {placeholder} AND cm.ESTADO_CONTRATO_M = 'Activo'
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
                    self.form_data["canon_mandato"] = f"${mandato['CANON_MANDATO']:,}".replace(",", ".")
                    self.form_data["direccion_propiedad"] = mandato["DIRECCION_PROPIEDAD"]
                    self.form_data["nombre_propietario"] = mandato["NOMBRE_PROPIETARIO"]
                
                if propiedad and propiedad["VALOR_ADMINISTRACION"]:
                    self.form_data["gastos_administracion"] = int(propiedad["VALOR_ADMINISTRACION"])
        
        except Exception as e:
            # En producción loguearíamos esto, por ahora silencioso o print en consola
            pass  # print(f"Error fetching contract details: {e}") [OpSec Removed]
    
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
                if liquidacion['estado'] != 'En Proceso':
                    async with self:
                        self.error_message = "Solo se pueden editar liquidaciones en estado 'En Proceso'"
                        self.is_loading = False
                    return
                
                async with self:
                    self.form_data = {
                        "id_liquidacion": id_liquidacion,
                        "id_contrato_m": liquidacion['id_contrato'],
                        "periodo": liquidacion['periodo'],
                        "otros_ingresos": liquidacion['otros_ingresos'],
                        "gastos_administracion": liquidacion['gastos_admin'],
                        "gastos_servicios": liquidacion['gastos_serv'],
                        "gastos_reparaciones": liquidacion['gastos_rep'],
                        "otros_egresos": liquidacion['otros_egr'],
                        "observaciones": liquidacion['observaciones']
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
            self.current_entidad_tipo = "LIQUIDACION"
            self.current_entidad_id = str(id_liquidacion)
            self.cargar_documentos()
        
        try:
            servicio = ServicioFinanciero(db_manager)
            liquidacion = servicio.obtener_detalle_liquidacion_ui(id_liquidacion)
            
            if liquidacion:
                async with self:
                    self.liquidacion_actual = liquidacion
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
            from src.infraestructura.persistencia.repositorio_liquidacion_sqlite import RepositorioLiquidacionSQLite
            from src.infraestructura.persistencia.database import db_manager as dm
            
            repo = RepositorioLiquidacionSQLite(dm)
            liquidaciones = repo.listar_por_propietario_y_periodo(id_propietario, periodo)
            
            if liquidaciones and len(liquidaciones) > 0:
                # Obtener detalles de TODAS las liquidaciones y consolidar
                servicio = ServicioFinanciero(db_manager)
                detalles_lista = []
                
                for liq in liquidaciones:
                    detalle = servicio.obtener_detalle_liquidacion_ui(liq.id_liquidacion)
                    if detalle:
                        detalles_lista.append(detalle)
                
                if detalles_lista:
                    # Crear liquidación consolidada sumando todos los valores
                    consolidado = {
                        'id': detalles_lista[0]['id'],  # ID de referencia
                        'periodo': periodo,
                        'fecha_generacion': detalles_lista[0]['fecha_generacion'],
                        'estado': detalles_lista[0]['estado'],
                        'observaciones': f"Consolidado de {len(detalles_lista)} propiedades",
                        
                        # Contexto del propietario
                        'propietario': detalles_lista[0]['propietario'],
                        'documento': detalles_lista[0]['documento'],
                        'propiedad': f"{len(detalles_lista)} propiedades",  # Mostrar cantidad
                        'matricula': 'Múltiples',
                        
                        # Lista detallada de cada propiedad
                        'propiedades_detalle': [
                            {
                                'direccion': d['propiedad'],
                                'matricula': d['matricula'],
                                'canon': d['canon'],
                                'neto': d['neto_pagar'],
                            }
                            for d in detalles_lista
                        ],
                        
                        # Sumar todos los valores financieros
                        'canon': sum(d['canon'] for d in detalles_lista),
                        'otros_ingresos': sum(d['otros_ingresos'] for d in detalles_lista),
                        'total_ingresos': sum(d['total_ingresos'] for d in detalles_lista),
                        
                        'comision_pct': detalles_lista[0]['comision_pct'],  # Mismo % para todos
                        'comision_pct_view': detalles_lista[0]['comision_pct_view'],
                        'comision_monto': sum(d['comision_monto'] for d in detalles_lista),
                        'iva_comision': sum(d['iva_comision'] for d in detalles_lista),
                        'impuesto_4x1000': sum(d['impuesto_4x1000'] for d in detalles_lista),
                        
                        'gastos_admin': sum(d['gastos_admin'] for d in detalles_lista),
                        'gastos_serv': sum(d['gastos_serv'] for d in detalles_lista),
                        'gastos_rep': sum(d['gastos_rep'] for d in detalles_lista),
                        'otros_egr': sum(d['otros_egr'] for d in detalles_lista),
                        'total_egresos': sum(d['total_egresos'] for d in detalles_lista),
                        
                        'neto_pagar': sum(d['neto_pagar'] for d in detalles_lista),
                        
                        # Pago
                        'fecha_pago': detalles_lista[0].get('fecha_pago'),
                        'metodo_pago': detalles_lista[0].get('metodo_pago'),
                        'referencia_pago': detalles_lista[0].get('referencia_pago'),
                        
                        # Auditoría
                        'created_at': detalles_lista[0]['created_at'],
                        'created_by': detalles_lista[0]['created_by'],
                    }
                    
                    async with self:
                        self.liquidacion_actual = consolidado
                        self.propiedades_consolidadas = consolidado['propiedades_detalle']
                        self.show_detail_modal = True
                        self.is_loading = False
                else:
                    raise ValueError("No se pudo cargar el detalle de las liquidaciones")
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
            "referencia_pago": ""
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
            "referencia_pago": ""
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
        """Abre modal para generar liquidación masiva de un propietario."""
        from datetime import datetime
        periodo_actual = datetime.now().strftime('%Y-%m')
        
        self.show_bulk_create_modal = True
        self.show_detail_modal = False
        self.show_create_modal = False
        self.show_edit_modal = False
        self.show_payment_modal = False
        self.form_data = {
            "id_propietario": "",
            "periodo": periodo_actual,
            "propiedades_preview": []  # Se llenará al seleccionar propietario
        }
        self.error_message = ""
    
    @rx.event(background=True)
    async def generar_liquidacion_masiva(self, form_data: Dict):
        """Genera liquidaciones consolidadas para todas las propiedades de un propietario."""
        async with self:
            self.is_loading = True
            self.error_message = ""
        
        try:
            servicio = ServicioFinanciero(db_manager)
            usuario_sistema = "admin"  # TODO: Obtener de AuthState
            
            # Parsear id_propietario que viene como "NOMBRE - DOCUMENTO"
            propietario_texto = form_data.get("id_propietario", "")
            periodo = form_data.get("periodo", "")
            
            if not propietario_texto or not periodo:
                raise ValueError("Debe seleccionar un propietario y un período")
            
            # Extraer el número de documento del string "Nombre - Documento"
            try:
                documento = propietario_texto.split(' - ')[-1].strip()
            except:
                raise ValueError("Error al procesar el propietario seleccionado")
            
            # Buscar ID_PROPIETARIO en la base de datos usando el documento
            id_propietario = None
            with db_manager.obtener_conexion() as conn:
                cursor = db_manager.get_dict_cursor(conn)
                query = """
                SELECT prop.ID_PROPIETARIO
                FROM PERSONAS per
                INNER JOIN PROPIETARIOS prop ON per.ID_PERSONA = prop.ID_PERSONA
                WHERE per.NUMERO_DOCUMENTO = %s
                LIMIT 1
                """
                cursor.execute(query, (documento,))
                row = cursor.fetchone()
                if row:
                    id_propietario = row['ID_PROPIETARIO']
            
            if not id_propietario:
                raise ValueError(f"No se encontró propietario con documento {documento}")
            
            # Generar liquidación consolidada (crea N liquidaciones individuales)
            liquidacion_consolidada = servicio.generar_liquidacion_propietario(
                id_propietario=id_propietario,
                periodo=periodo,
                datos_adicionales_por_contrato=None,  # Valores por defecto
                usuario_sistema=usuario_sistema
            )
            
            async with self:
                self.show_bulk_create_modal = False
                self.form_data = {}
            
            # Si estamos en vista agrupada, recargar
            if self.vista_agrupada:
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
            
            if not self.error_message:
                 yield rx.toast.success(f"Liquidaciones generadas para {propietario_texto}", position="bottom-right")
            else:
                 yield rx.toast.error(self.error_message, position="bottom-right")
    
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
                usuario_sistema=usuario_sistema
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

        yield rx.toast.success(f"Se aprobaron {affected} liquidaciones", position="bottom-right")
    
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
                usuario_sistema=usuario_sistema
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
        
        yield rx.toast.success(f"Se registraron {affected} pagos correctamente", position="bottom-right")
    
    @rx.event(background=True)
    async def save_liquidacion(self, form_data: Dict):
        """Guarda liquidación (crear o editar)."""
        async with self:
            self.is_loading = True
            self.error_message = ""
        
        try:
            servicio = ServicioFinanciero(db_manager)
            usuario_sistema = "admin"  # TODO: Obtener de AuthState
            
            # Procesar datos del formulario
            datos_procesados = {
                "otros_ingresos": int(form_data.get("otros_ingresos", 0)),
                "gastos_administracion": int(form_data.get("gastos_administracion", 0)),
                "gastos_servicios": int(form_data.get("gastos_servicios", 0)),
                "gastos_reparaciones": int(form_data.get("gastos_reparaciones", 0)),
                "otros_egresos": int(form_data.get("otros_egresos", 0)),
                "observaciones": form_data.get("observaciones", "")
            }
            
            if self.show_create_modal:
                # Crear nueva liquidación
                datos_procesados["id_contrato_m"] = int(form_data["id_contrato_m"])
                datos_procesados["periodo"] = form_data["periodo"]
                servicio.generar_liquidacion_mensual(
                    id_contrato_m=datos_procesados["id_contrato_m"],
                    periodo=datos_procesados["periodo"],
                    datos_adicionales=datos_procesados,
                    usuario_sistema=usuario_sistema
                )
            else:  # Editar
                id_liquidacion = form_data.get("id_liquidacion")
                if id_liquidacion:
                    servicio.actualizar_liquidacion(
                        id_liquidacion=int(id_liquidacion),
                        datos_actualizados=datos_procesados,
                        usuario_sistema=usuario_sistema
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
            
            if not self.error_message:
                yield rx.toast.success(f"Liquidación guardada correctamente", position="bottom-right")
            else:
                yield rx.toast.error(self.error_message, position="bottom-right")
    
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

        yield rx.toast.success("Liquidación aprobada correctamente", position="bottom-right")
    
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
                usuario_sistema=usuario_sistema
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
                    self.error_message = "El motivo de cancelación debe tener al menos 10 caracteres"
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
            
            yield LiquidacionesState.load_liquidaciones()
                
        except Exception as e:
            async with self:
                self.error_message = f"Error al reversar: {str(e)}"
                self.is_loading = False
            yield rx.toast.error(self.error_message, position="bottom-right")
            return

        yield rx.toast.success("Liquidación reversada a 'En Proceso'", position="bottom-right")

    def set_cancel_motivo(self, value: str):
        self.cancel_motivo = value

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
                yield rx.toast.warning("El motivo es muy corto", position="bottom-right")
                return
            
            servicio = ServicioFinanciero(db_manager)
            servicio.cancelar_liquidacion(
                self.liquidacion_id_for_action,
                self.cancel_motivo,
                "admin"
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

        yield rx.toast.success("Liquidación cancelada correctamente", position="bottom-right")
