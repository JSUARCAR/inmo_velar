import reflex as rx
from typing import Optional, Dict, Any, List
from datetime import datetime
from src.aplicacion.servicios.servicio_liquidacion_asesores import ServicioLiquidacionAsesores
from src.infraestructura.persistencia.database import db_manager
from src.infraestructura.repositorios.repositorio_liquidacion_asesor_sqlite import RepositorioLiquidacionAsesorSQLite
from src.infraestructura.repositorios.repositorio_descuento_asesor_sqlite import RepositorioDescuentoAsesorSQLite
from src.infraestructura.repositorios.repositorio_pago_asesor_sqlite import RepositorioPagoAsesorSQLite
from src.infraestructura.repositorios.repositorio_bonificacion_asesor_sqlite import RepositorioBonificacionAsesorSQLite
from src.infraestructura.persistencia.repositorio_contrato_arrendamiento_sqlite import RepositorioContratoArrendamientoSQLite


class LiquidacionAsesoresState(rx.State):
    """Estado para gestión de liquidaciones de asesores.
    Maneja paginación, filtros, CRUD, state machine y descuentos.
    """
    # Paginación
    current_page: int = 1
    page_size: int = 25
    total_items: int = 0
    
    # Datos
    liquidaciones: List[Dict[str, Any]] = []
    liquidacion_actual: Optional[Dict[str, Any]] = None
    descuentos_actuales: List[Dict[str, Any]] = []
    is_loading: bool = False
    error_message: str = ""
    
    # Filtros
    search_text: str = ""
    filter_estado: str = "Todos"
    filter_periodo: str = ""
    filter_asesor: str = ""
    
    # Opciones de filtros
    estado_options: List[str] = ["Todos", "Pendiente", "Aprobada", "Pagada", "Anulada"]
    periodo_options: List[str] = []
    asesores_options: List[Dict[str, Any]] = []
    asesores_select_options: List[str] = []
    
    # Modales
    show_form_modal: bool = False
    show_detail_modal: bool = False
    show_discount_modal: bool = False
    show_annul_modal: bool = False
    selected_annul_id: int = 0
    annul_reason: str = ""
    show_edit_modal: bool = False
    
    # Form data
    selected_liquidacion_id: int = 0
    form_data: Dict[str, Any] = {}
    discount_form: Dict[str, Any] = {}
    edit_form: Dict[str, Any] = {}
    
    # Detalles actuales para modal
    descuentos_actuales: List[Dict[str, Any]] = []
    bonificaciones_actuales: List[Dict[str, Any]] = []
    
    # Enhanced Form Data
    advisor_properties: List[Dict[str, Any]] = []
    
    # Existing items (saved in DB) - for edit mode
    existing_discounts: List[Dict[str, Any]] = []
    existing_bonuses: List[Dict[str, Any]] = []
    
    # New items (temporary) - for create/edit mode
    new_discounts: List[Dict[str, Any]] = []
    new_bonuses: List[Dict[str, Any]] = []
    temp_discount: Dict[str, Any] = {"tipo": "Otros", "descripcion": "", "valor": ""}
    temp_bonus: Dict[str, Any] = {"tipo": "Bono", "descripcion": "", "valor": ""}
    
    @rx.event(background=True)
    async def on_load(self):
        """Carga inicial al montar la página."""
        try:
            with open("debug_on_load.log", "w") as f:
                f.write("on_load started\n")
        except:
            pass
            
        async with self:
            self.is_loading = True
        
        try:
            # Cargar opciones de filtros
            yield LiquidacionAsesoresState.load_filter_options()
            # Cargar liquidaciones
            yield LiquidacionAsesoresState.load_liquidaciones()
        except Exception as e:
            with open("debug_on_load_error.log", "w") as f:
                f.write(f"Error in on_load: {str(e)}\n")
        finally:
            async with self:
                self.is_loading = False
    
    @rx.event(background=True)
    async def load_filter_options(self):
        """Carga opciones para filtros (asesores, períodos)."""
        try:
            with open("debug_filter_start.log", "w") as f:
                f.write("load_filter_options started\n")
        except:
            pass

        try:
            # Cargar asesores que tienen contratos de mandato activos
            query_asesores = """
            SELECT DISTINCT
                a.ID_ASESOR,
                p.NOMBRE_COMPLETO,
                a.COMISION_PORCENTAJE_ARRIENDO
            FROM ASESORES a
            INNER JOIN PERSONAS p ON a.ID_PERSONA = p.ID_PERSONA
            -- LEFT JOIN to include advisors without active mandates
            LEFT JOIN CONTRATOS_MANDATOS cm ON a.ID_ASESOR = cm.ID_ASESOR
            WHERE a.ESTADO = TRUE
            ORDER BY p.NOMBRE_COMPLETO
            """
            
            with db_manager.obtener_conexion() as conn:
                cursor = db_manager.get_dict_cursor(conn)
                cursor.execute(query_asesores)
                rows_asesores = cursor.fetchall()
                
                asesores = []
                for row in rows_asesores:
                    # Handle both dict-like and tuple rows
                    if isinstance(row, (dict, object)) and hasattr(row, '__getitem__') and not isinstance(row, tuple):
                         # Dict-like access
                         id_val = row['ID_ASESOR']
                         nombre = row['NOMBRE_COMPLETO']
                         comision = row['COMISION_PORCENTAJE_ARRIENDO']
                    else:
                         # Tuple access (assume order: ID, NOMBRE, COMISION)
                         id_val = row[0]
                         nombre = row[1]
                         comision = row[2]

                    asesores.append({
                        "id": str(id_val),
                        "texto": nombre,
                        "comision_porcentaje": comision if comision is not None else 5.0
                    })

                # Create select options as "texto" only
                asesores_select = [a['texto'] for a in asesores]
                
                # Cargar últimos 24 períodos (2 años)
                from datetime import datetime
                from dateutil.relativedelta import relativedelta
                
                periodos = []
                fecha_actual = datetime.now()
                for i in range(24):
                    fecha = fecha_actual - relativedelta(months=i)
                    periodos.append(fecha.strftime("%Y-%m"))
            
            async with self:
                self.asesores_options = asesores
                self.asesores_select_options = asesores_select
                self.periodo_options = periodos
                
        except Exception as e:
            with open("debug_filter_error.log", "w") as f:
                f.write(f"Error in load_filter_options: {str(e)}\n")
            async with self:
                self.error_message = f"Error al cargar filtros: {str(e)}"

    @rx.event(background=True)
    async def fetch_advisor_properties(self, id_asesor: int):
        """Carga las propiedades/contratos activos para visualización."""
        try:
            repo = RepositorioContratoArrendamientoSQLite(db_manager)
            props = repo.obtener_detalle_contratos_asesor(id_asesor)
            async with self:
                self.advisor_properties = props
        except Exception as e:
            print(f"Error fetching properties: {e}")
            async with self:
                self.advisor_properties = []
    
    @rx.event(background=True)
    async def load_liquidaciones(self):
        """Carga liquidaciones con filtros y paginación."""
        async with self:
            self.is_loading = True
            self.error_message = ""
        
        try:
            # Inicializar servicio
            repo_liquidacion = RepositorioLiquidacionAsesorSQLite(db_manager)
            repo_descuento = RepositorioDescuentoAsesorSQLite(db_manager)
            repo_pago = RepositorioPagoAsesorSQLite(db_manager)
            
            servicio = ServicioLiquidacionAsesores(
                repo_liquidacion=repo_liquidacion,
                repo_descuento=repo_descuento,
                repo_pago=repo_pago
            )
            
            # Construir filtros
            filtros = {}
            if self.filter_estado and self.filter_estado != "Todos":
                filtros["estado"] = self.filter_estado
            if self.filter_periodo:
                filtros["periodo"] = self.filter_periodo
            if self.filter_asesor:
                # Buscar ID del asesor seleccionado
                for asesor in self.asesores_options:
                    if asesor["texto"] == self.filter_asesor:
                        filtros["id_asesor"] = int(asesor["id"])
                        break
            if self.search_text:
                filtros["search"] = self.search_text
            
            # Obtener datos paginados
            resultado = servicio.listar_liquidaciones_paginado(
                page=self.current_page,
                page_size=self.page_size,
                filtros=filtros
            )
            
            liquidaciones_list = [
                {
                    "id_liquidacion": liq.id_liquidacion_asesor,
                    "periodo": liq.periodo_liquidacion,
                    "asesor": liq.nombre_asesor if hasattr(liq, 'nombre_asesor') else "N/A",
                    "id_asesor": liq.id_asesor,
                    "canon_liquidado": liq.canon_arrendamiento_liquidado,
                    "porcentaje": liq.porcentaje_comision / 100.0,  # Convertir a decimal
                    "comision_bruta": liq.comision_bruta,
                    "total_descuentos": liq.total_descuentos,
                    "total_bonificaciones": getattr(liq, 'total_bonificaciones', 0),
                    "valor_neto": liq.valor_neto_asesor,
                    "estado": liq.estado_liquidacion,
                    "fecha_creacion": liq.fecha_creacion,
                    "fecha_aprobacion": liq.fecha_aprobacion,
                    "observaciones": liq.observaciones_liquidacion or ""
                }
                for liq in resultado["items"]
            ]
            
            async with self:
                self.liquidaciones = liquidaciones_list
                self.total_items = resultado["total"]
                self.is_loading = False
                
        except Exception as e:
            async with self:
                self.error_message = f"Error al cargar liquidaciones: {str(e)}"
                self.liquidaciones = []
                self.total_items = 0
                self.is_loading = False
    
    @rx.event(background=True)
    async def limpiar_filtros(self):
        """Limpia todos los filtros y recarga."""
        async with self:
            self.search_text = ""
            self.filter_estado = "Todos"
            self.filter_periodo = ""
            self.filter_asesor = ""
        
        yield LiquidacionAsesoresState.load_liquidaciones

    # Paginación
    def next_page(self):
        """Avanza a la siguiente página."""
        if self.current_page * self.page_size < self.total_items:
            self.current_page += 1
            return LiquidacionAsesoresState.load_liquidaciones
    
    def prev_page(self):
        """Retrocede a la página anterior."""
        if self.current_page > 1:
            self.current_page -= 1
            return LiquidacionAsesoresState.load_liquidaciones
    
    def set_page_size(self, size: str):
        """Cambia el tamaño de página."""
        self.page_size = int(size)
        self.current_page = 1
        return LiquidacionAsesoresState.load_liquidaciones
    
    # Búsqueda y Filtros
    def set_search(self, value: str):
        """Actualiza búsqueda."""
        self.search_text = value
    
    def search_liquidaciones(self):
        """Ejecuta búsqueda."""
        self.current_page = 1
        return LiquidacionAsesoresState.load_liquidaciones
    
    def handle_search_key_down(self, key: str):
        """Maneja Enter en búsqueda."""
        if key == "Enter":
            return self.search_liquidaciones()
    
    def set_filter_estado(self, value: str):
        """Cambia filtro de estado."""
        self.filter_estado = value
        self.current_page = 1
        return LiquidacionAsesoresState.load_liquidaciones
    
    def set_filter_periodo(self, value: str):
        """Cambia filtro de período."""
        self.filter_periodo = value
        self.current_page = 1
        return LiquidacionAsesoresState.load_liquidaciones
    
    def set_filter_asesor(self, value: str):
        """Cambia filtro de asesor."""
        self.filter_asesor = value
        self.current_page = 1
        return LiquidacionAsesoresState.load_liquidaciones
    
    # Modal CRUD
    def open_create_modal(self):
        """Abre modal para crear nueva liquidación."""
        self.selected_liquidacion_id = 0
        self.show_form_modal = True
        self.show_detail_modal = False
        self.form_data = {
            "id_asesor": "",
            "periodo": datetime.now().strftime("%Y-%m"),
            "contratos": [],
            "porcentaje_comision": "5.0",
            "observaciones": ""
        }
        self.advisor_properties = []
        self.advisor_properties = []
        self.new_discounts = []
        self.new_bonuses = []
        self.temp_discount = {"tipo": "Otros", "descripcion": "", "valor": ""}
        self.temp_bonus = {"tipo": "Bono", "descripcion": "", "valor": ""}
        self.error_message = ""

    @rx.event(background=True)
    async def crear_liquidacion(self, form_data: Dict):
        """Crea una nueva liquidación."""
        async with self:
            self.is_loading = True
            self.error_message = ""
        
        try:
            repo_liquidacion = RepositorioLiquidacionAsesorSQLite(db_manager)
            repo_descuento = RepositorioDescuentoAsesorSQLite(db_manager)
            repo_pago = RepositorioPagoAsesorSQLite(db_manager)
            repo_bonificacion = RepositorioBonificacionAsesorSQLite(db_manager)
            
            servicio = ServicioLiquidacionAsesores(
                repo_liquidacion=repo_liquidacion,
                repo_descuento=repo_descuento,
                repo_pago=repo_pago,
                repo_bonificacion=repo_bonificacion
            )
            
            # Validar y convertir datos
            id_asesor_str = form_data.get("id_asesor")
            if not id_asesor_str:
                async with self:
                    self.error_message = "Debe seleccionar un asesor"
                    self.is_loading = False
                return
                
            id_asesor = int(id_asesor_str)
            periodo = form_data.get("periodo")
            porcentaje_str = form_data.get("porcentaje_comision", "5.0")
            try:
                porcentaje_decimal = float(porcentaje_str)
                porcentaje_entero = int(porcentaje_decimal * 100)
            except ValueError:
                porcentaje_entero = 500 # Default 5%
            
            # ELITE LOGIC: Obtener contratos activos del asesor automáticamente
            repo_contrato = RepositorioContratoArrendamientoSQLite(db_manager)
            contratos_activos = repo_contrato.obtener_activos_por_asesor(id_asesor)
            
            # Convertir a formato esperado por el servicio (List[Dict])
            contratos = [
                {
                    "id": c.id_contrato_a, 
                    "canon": c.canon_arrendamiento
                }
                for c in contratos_activos
            ]
            
            # Log para depuración (opcional, pero útil)
            print(f"Liquidando asesor {id_asesor}: {len(contratos)} contratos encontrados. Total canon: {sum(c['canon'] for c in contratos)}")
            
            usuario_sistema = "admin" # TODO: Obtener de AuthState
            
            observaciones = form_data.get("observaciones", "")
            # Servicio espera basis points (ej: 8% -> 800)
            pct_basis_points = int(float(porcentaje_str) * 100)
            
            # Calcular Total Bonificaciones
            total_bonificaciones = sum(int(b.get("valor", 0)) for b in self.new_bonuses)

            # 4. Crear liquidación con descuentos
            liquidacion = servicio.generar_liquidacion_multi_contrato(
                id_asesor=id_asesor,
                periodo=periodo,
                contratos_lista=contratos,
                porcentaje_comision=pct_basis_points,
                total_bonificaciones=total_bonificaciones,
                datos_adicionales={"observaciones": observaciones},
                usuario=usuario_sistema
            )

             # Agregar descuentos adicionales ingresados en el formulario
            for descuento in self.new_discounts:
                 try:
                     servicio.agregar_descuento(
                         id_liquidacion=liquidacion.id_liquidacion_asesor,
                         tipo=descuento["tipo"],
                         descripcion=descuento["descripcion"],
                         valor=int(descuento["valor"]),
                         usuario=usuario_sistema
                     )
                 except Exception as e:
                     print(f"Error agregando descuento {descuento}: {e}")
                     async with self:
                         self.error_message = f"Se creó la liquidación pero falló al agregar descuento '{descuento['tipo']}': {str(e)}"
            
            # Agregar bonificaciones ingresadas en el formulario
            for bonificacion in self.new_bonuses:
                 try:
                     servicio.agregar_bonificacion(
                         id_liquidacion=liquidacion.id_liquidacion_asesor,
                         tipo=bonificacion["tipo"],
                         descripcion=bonificacion["descripcion"],
                         valor=int(bonificacion["valor"]),
                         usuario=usuario_sistema
                     )
                 except Exception as e:
                     print(f"Error agregando bonificacion {bonificacion}: {e}")
                     # No fallamos todo el proceso, pero logueamos

            
            async with self:
                self.show_form_modal = False
                self.is_loading = False
                self.form_data = {
                    "id_asesor": "",
                    "periodo": datetime.now().strftime("%Y-%m"),
                    "contratos": [],
                    "porcentaje_comision": "5.0",
                    "observaciones": ""
                }
                self.new_discounts = []
                self.new_bonuses = []
                self.advisor_properties = []
            
            # Recargar lista
            yield rx.toast.success("Liquidación creada exitosamente", position="top-center")
            yield LiquidacionAsesoresState.load_liquidaciones()
            
        except Exception as e:
            async with self:
                self.error_message = f"Error al crear liquidación: {str(e)}"
                self.is_loading = False
            yield rx.toast.error(f"Error al crear liquidación: {str(e)}", position="top-center")
    
    @rx.event(background=True)
    async def open_detail_modal(self, id_liquidacion: int):
        """Abre modal de detalles de liquidación."""
        async with self:
            self.is_loading = True
            self.error_message = ""
        
        try:
            repo_liquidacion = RepositorioLiquidacionAsesorSQLite(db_manager)
            repo_descuento = RepositorioDescuentoAsesorSQLite(db_manager)
            repo_pago = RepositorioPagoAsesorSQLite(db_manager)
            
            servicio = ServicioLiquidacionAsesores(
                repo_liquidacion=repo_liquidacion,
                repo_descuento=repo_descuento,
                repo_pago=repo_pago
            )
            
            liquidacion = servicio.obtener_detalle_completo(id_liquidacion)
            descuentos = liquidacion.get("descuentos", [])
            bonificaciones = liquidacion.get("bonificaciones", [])
            contratos_data = liquidacion.get("contratos", [])
            
            if not liquidacion or "liquidacion" not in liquidacion:
                async with self:
                    self.error_message = "Liquidación no encontrada"
                    self.is_loading = False
                return
            
            # Extraer datos de la liquidación
            liq_data = liquidacion["liquidacion"]
            
            async with self:
                self.liquidacion_actual = {
                    "id_liquidacion": liq_data["id_liquidacion_asesor"],
                    "periodo": liq_data["periodo_liquidacion"],
                    "asesor": liq_data.get("nombre_asesor", "N/A"),
                    "canon_liquidado": liq_data["canon_arrendamiento_liquidado"],
                    "porcentaje": liq_data["porcentaje_comision"] / 100.0,
                    "comision_bruta": liq_data["comision_bruta"],
                    "total_descuentos": liq_data["total_descuentos"],
                    "total_bonificaciones": liq_data.get("total_bonificaciones", 0),
                    "valor_neto": liq_data["valor_neto_asesor"],
                    "estado": liq_data["estado_liquidacion"],
                    "observaciones": liq_data["observaciones_liquidacion"] or ""
                }
                self.descuentos_actuales = [
                    {
                        "id_descuento": d["id_descuento_asesor"],
                        "tipo": d["tipo_descuento"],
                        "descripcion": d["descripcion_descuento"],
                        "valor": d["valor_descuento"]
                    }
                    for d in descuentos
                ]
                self.bonificaciones_actuales = [
                    {
                        "id_bonificacion": b["id_bonificacion_asesor"],
                        "tipo": b["tipo_bonificacion"],
                        "descripcion": b["descripcion_bonificacion"],
                        "valor": b["valor_bonificacion"]
                    }
                    for b in bonificaciones
                    for b in bonificaciones
                ]
                
                # Cargar propiedades para el detalle
                properties_list = []
                for c in contratos_data:
                     properties_list.append({
                        "DIRECCION_PROPIEDAD": c.get("direccion_propiedad") or c.get("direccion", "N/A"),
                        "CANON_ARRENDAMIENTO": c.get("canon_arrendamiento") or c.get("canon_incluido", 0),
                        "ID_CONTRATO_A": c.get("id_contrato") or c.get("id_contrato_a")
                     })
                self.advisor_properties = properties_list
                
                self.show_detail_modal = True
                self.show_form_modal = False
                self.is_loading = False
        except Exception as e:
            async with self:
                self.error_message = f"Error al cargar detalles: {str(e)}"
                self.is_loading = False
    
    def close_modal(self):
        """Cierra todos los modales."""
        self.show_form_modal = False
        self.show_detail_modal = False
        self.show_discount_modal = False
        self.liquidacion_actual = None
        self.descuentos_actuales = []
        self.bonificaciones_actuales = []
        self.form_data = {}
        self.discount_form = {}
        self.error_message = ""
        # Clear edit modal lists
        self.existing_discounts = []
        self.existing_bonuses = []
        self.new_discounts = []
        self.new_bonuses = []
        self.selected_liquidacion_id = 0

    def set_show_form_modal(self, value: bool):
        self.show_form_modal = value

    def set_show_detail_modal(self, value: bool):
        self.show_detail_modal = value

    def set_show_discount_modal(self, value: bool):
        self.show_discount_modal = value
    
    def close_form_modal(self):
        """Cierra el modal de formulario."""
        self.show_form_modal = False
        self.form_data = {}
        self.error_message = ""
        self.existing_discounts = []
        self.existing_bonuses = []
        self.new_discounts = []
        self.new_bonuses = []
        self.selected_liquidacion_id = 0

    def open_annul_modal(self, id_liquidacion: int):
        """Abre el modal de anulación."""
        self.selected_annul_id = id_liquidacion
        self.annul_reason = ""
        self.show_annul_modal = True

    def close_annul_modal(self):
        """Cierra el modal de anulación."""
        self.show_annul_modal = False
        self.annul_reason = ""
        self.selected_annul_id = 0

    def set_annul_reason(self, value: str):
        """Actualiza el motivo de anulación."""
        self.annul_reason = value

    @rx.event(background=True)
    async def confirm_annulment(self):
        """Confirma la anulación y llama al servicio."""
        if not self.annul_reason.strip():
            async with self:
                self.error_message = "Debe ingresar un motivo para la anulación."
            return

        yield LiquidacionAsesoresState.anular_liquidacion(self.selected_annul_id, self.annul_reason)

    
    @rx.event(background=True)
    async def open_create_modal(self):
        """Abre el modal para crear una nueva liquidación."""
        async with self:
            # Reset all form data
            self.form_data = {
                "id_asesor": "",
                "periodo": "",
                "porcentaje_comision": "",
                "observaciones": ""
            }
            self.selected_liquidacion_id = 0
            self.existing_discounts = []
            self.existing_bonuses = []
            self.new_discounts = []
            self.new_bonuses = []
            self.advisor_properties = []
            self.show_form_modal = True
    
    @rx.event(background=True)
    async def open_edit_modal(self, id_liquidacion: int):
        """Abre el modal para editar una liquidación existente."""
        async with self:
            self.is_loading = True
            self.error_message = ""
        
        try:
            repo_liquidacion = RepositorioLiquidacionAsesorSQLite(db_manager)
            repo_descuento = RepositorioDescuentoAsesorSQLite(db_manager)
            repo_pago = RepositorioPagoAsesorSQLite(db_manager)
            repo_contrato = RepositorioContratoArrendamientoSQLite(db_manager)
            
            servicio = ServicioLiquidacionAsesores(
                repo_liquidacion=repo_liquidacion,
                repo_descuento=repo_descuento,
                repo_pago=repo_pago
            )
            
            # Obtener detalles completos
            detalles = servicio.obtener_detalle_completo(id_liquidacion)
            
            if not detalles or "liquidacion" not in detalles:
                raise ValueError("No se encontró la liquidación")

            liq = detalles["liquidacion"]
            
            # Cargar propiedades del asesor (usando los datos ya traídos por el servicio)
            # Esto evita llamadas redundantes y errores de métodos inexistentes
            contratos_data = detalles.get("contratos", [])
            properties_list = []
            
            # El servicio devuelve lista de dicts con info de contrato y propiedad
            for c in contratos_data:
                 properties_list.append({
                    "DIRECCION_PROPIEDAD": c.get("direccion_propiedad") or c.get("direccion", "N/A"),
                    "CANON_ARRENDAMIENTO": c.get("canon_arrendamiento") or c.get("canon_incluido", 0),
                    "ID_CONTRATO_A": c.get("id_contrato") or c.get("id_contrato_a")
                 })
            
            async with self:
                self.advisor_properties = properties_list
            
            async with self:
                # Poblar form_data con datos de la liquidación
                self.form_data = {
                    "id_asesor": str(liq["id_asesor"]),
                    "periodo": liq["periodo_liquidacion"],
                    "porcentaje_comision": str(liq["porcentaje_comision"]),
                    "observaciones": liq["observaciones_liquidacion"] or ""
                }
                
                # Separar descuentos GUARDADOS de los nuevos
                # Mapeamos las claves para coincidir con lo que espera el frontend (modal_form.py)
                raw_discounts = detalles.get("descuentos", [])
                self.existing_discounts = [
                    {
                        "id_descuento": d.get("id_descuento_asesor"),
                        "tipo": d.get("tipo_descuento"),
                        "descripcion": d.get("descripcion_descuento"),
                        "valor": d.get("valor_descuento")
                    }
                    for d in raw_discounts
                ]

                raw_bonuses = detalles.get("bonificaciones", [])
                self.existing_bonuses = [
                    {
                        "id_bonificacion": b.get("id_bonificacion_asesor"),
                        "tipo": b.get("tipo_bonificacion"),
                        "descripcion": b.get("descripcion_bonificacion"),
                        "valor": b.get("valor_bonificacion")
                    }
                    for b in raw_bonuses
                ]
                
                # Limpiar listas temporales
                self.new_discounts = []
                self.new_bonuses = []
                
                self.selected_liquidacion_id = id_liquidacion
                self.is_loading = False
                self.show_form_modal = True
                
        except Exception as e:
            async with self:
                self.error_message = f"Error al cargar liquidación: {str(e)}"
                self.is_loading = False
    
    # State Machine Transitions
    @rx.event(background=True)
    async def aprobar_liquidacion(self, id_liquidacion: int):
        """Aprueba una liquidación (Pendiente → Aprobada)."""
        async with self:
            self.is_loading = True
            self.error_message = ""
        
        try:
            repo_liquidacion = RepositorioLiquidacionAsesorSQLite(db_manager)
            repo_descuento = RepositorioDescuentoAsesorSQLite(db_manager)
            repo_pago = RepositorioPagoAsesorSQLite(db_manager)
            
            servicio = ServicioLiquidacionAsesores(
                repo_liquidacion=repo_liquidacion,
                repo_descuento=repo_descuento,
                repo_pago=repo_pago
            )
            
            usuario_sistema = "admin"  # TODO: Obtener de AuthState
            servicio.aprobar_liquidacion(id_liquidacion, usuario_sistema)
            
            async with self:
                self.is_loading = False
                self.show_detail_modal = False
            
            # Recargar lista
            yield rx.toast.success("Liquidación aprobada correctamente", position="top-center")
            yield LiquidacionAsesoresState.load_liquidaciones()
                
        except Exception as e:
            async with self:
                self.error_message = f"Error al aprobar liquidación: {str(e)}"
                self.is_loading = False
            yield rx.toast.error(f"Error al aprobar liquidación: {str(e)}", position="top-center")
    
    @rx.event(background=True)
    async def marcar_como_pagada(self, id_liquidacion: int):
        """Marca liquidación como pagada (Aprobada → Pagada)."""
        async with self:
            self.is_loading = True
            self.error_message = ""
        
        try:
            repo_liquidacion = RepositorioLiquidacionAsesorSQLite(db_manager)
            repo_descuento = RepositorioDescuentoAsesorSQLite(db_manager)
            repo_pago = RepositorioPagoAsesorSQLite(db_manager )
            
            servicio = ServicioLiquidacionAsesores(
                repo_liquidacion=repo_liquidacion,
                repo_descuento=repo_descuento,
                repo_pago=repo_pago
            )
            
            usuario_sistema = "admin"  # TODO: Obtener de AuthState
            # Registrar pago
            servicio.registrar_pago(
                id_liquidacion=id_liquidacion,
                metodo_pago="Transferencia",
                referencia_pago=f"PAGO-{id_liquidacion}-{datetime.now().strftime('%Y%m%d')}",
                fecha_pago=datetime.now().strftime("%Y-%m-%d"),
                usuario=usuario_sistema
            )
            
            async with self:
                self.is_loading = False
                self.show_detail_modal = False
            
            # Recargar lista
            yield rx.toast.success("Pago registrado correctamente", position="top-center")
            yield LiquidacionAsesoresState.load_liquidaciones()
                
        except Exception as e:
            async with self:
                self.error_message = f"Error al marcar como pagada: {str(e)}"
                self.is_loading = False
            yield rx.toast.error(f"Error al registrar pago: {str(e)}", position="top-center")
    
    @rx.event(background=True)
    async def anular_liquidacion(self, id_liquidacion: int, motivo: str):
        """Anula una liquidación."""
        async with self:
            self.is_loading = True
            self.error_message = ""
        
        try:
            repo_liquidacion = RepositorioLiquidacionAsesorSQLite(db_manager)
            repo_descuento = RepositorioDescuentoAsesorSQLite(db_manager)
            repo_pago = RepositorioPagoAsesorSQLite(db_manager)
            
            servicio = ServicioLiquidacionAsesores(
                repo_liquidacion=repo_liquidacion,
                repo_descuento=repo_descuento,
                repo_pago=repo_pago
            )
            
            usuario_sistema = "admin"  # TODO: Obtener de AuthState
            servicio.anular_liquidacion(id_liquidacion, motivo, usuario_sistema)
            
            async with self:
                self.is_loading = False
                self.show_detail_modal = False
                self.show_annul_modal = False
                self.annul_reason = ""
                self.selected_annul_id = 0
            
            yield rx.toast.success("Liquidación anulada correctamente", position="top-center")
            # Recargar lista
            yield LiquidacionAsesoresState.load_liquidaciones()
                
        except Exception as e:
            async with self:
                self.error_message = f"Error al anular liquidación: {str(e)}"
                self.is_loading = False
            yield rx.toast.error(f"Error al anular liquidación: {str(e)}", position="top-center")
    
    # Method removed (duplicate)

    @rx.event(background=True)
    async def eliminar_bonificacion(self, id_bonificacion: int):
        """Elimina una bonificación existente."""
        async with self:
            self.is_loading = True
            
        try:
            # Check for synthetic bonus (id -1)
            # Check for synthetic bonus (id -1)
            if id_bonificacion == -1:
                # Caso especial: Eliminar bonificación consolidada antigua
                repo_liquidacion = RepositorioLiquidacionAsesorSQLite(db_manager)
                repo_descuento = RepositorioDescuentoAsesorSQLite(db_manager)
                repo_pago = RepositorioPagoAsesorSQLite(db_manager)
                repo_bonificacion = RepositorioBonificacionAsesorSQLite(db_manager)
                
                servicio = ServicioLiquidacionAsesores(
                    repo_liquidacion=repo_liquidacion,
                    repo_descuento=repo_descuento,
                    repo_pago=repo_pago,
                    repo_bonificacion=repo_bonificacion
                )
                
                usuario_sistema = "admin" # TODO: Auth
                if self.selected_liquidacion_id:
                    servicio.remover_bonificacion_consolidada(self.selected_liquidacion_id, usuario_sistema)
                
                # Recargar modal
                if self.selected_liquidacion_id:
                    yield LiquidacionAsesoresState.open_edit_modal(self.selected_liquidacion_id)
                    
                yield LiquidacionAsesoresState.load_liquidaciones()
                
                async with self:
                    self.is_loading = False
                return

            repo_liquidacion = RepositorioLiquidacionAsesorSQLite(db_manager)
            repo_descuento = RepositorioDescuentoAsesorSQLite(db_manager)
            repo_pago = RepositorioPagoAsesorSQLite(db_manager)
            repo_bonificacion = RepositorioBonificacionAsesorSQLite(db_manager)
             
            servicio = ServicioLiquidacionAsesores(
                 repo_liquidacion=repo_liquidacion,
                 repo_descuento=repo_descuento,
                 repo_pago=repo_pago,
                 repo_bonificacion=repo_bonificacion
            )
             
            servicio.eliminar_bonificacion(id_bonificacion, "admin") # TODO: Obtener usuario real
             
             # Recargar modal
            if self.selected_liquidacion_id:
                 yield LiquidacionAsesoresState.open_edit_modal(self.selected_liquidacion_id)
                 
            yield LiquidacionAsesoresState.load_liquidaciones()
            
            yield rx.toast.success("Bonificación eliminada", position="top-center")
             
        except Exception as e:
            print(f"Error eliminando bonificación: {e}")
            async with self:
                self.error_message = f"Error al eliminar bonificación: {str(e)}"
                self.is_loading = False
            yield rx.toast.error(f"Error al eliminar bonificación: {str(e)}", position="top-center")

    @rx.event(background=True)
    async def handle_save_form(self, form_data: Dict):
        """Manejador central para guardar el formulario (Crear o Editar)."""
        if self.selected_liquidacion_id > 0:
            return LiquidacionAsesoresState.actualizar_liquidacion_completa(form_data)
        else:
            return LiquidacionAsesoresState.crear_liquidacion(form_data)

    def close_edit_modal(self):
        """Deprecado - usar close_form_modal."""
        self.show_form_modal = False
        self.show_edit_modal = False

    def set_edit_field(self, field: str, value: Any):
        """Deprecado - usar set_form_field."""
        pass

    @rx.event(background=True)
    async def actualizar_liquidacion_completa(self, form_data: Dict):
        """Actualiza liquidación completa desde el formulario compartido."""
        async with self:
            self.is_loading = True
            self.error_message = ""
        
        try:
            repo_liquidacion = RepositorioLiquidacionAsesorSQLite(db_manager)
            repo_descuento = RepositorioDescuentoAsesorSQLite(db_manager)
            repo_pago = RepositorioPagoAsesorSQLite(db_manager)
            repo_bonificacion = RepositorioBonificacionAsesorSQLite(db_manager)
            
            servicio = ServicioLiquidacionAsesores(
                repo_liquidacion=repo_liquidacion,
                repo_descuento=repo_descuento,
                repo_pago=repo_pago,
                repo_bonificacion=repo_bonificacion
            )
            
            usuario_sistema = "admin" # TODO: Auth
            
            # 1. Actualizar campos básicos
            datos_actualizar = {}
            
            try:
                pct_str = form_data.get("porcentaje_comision", "0")
                pct_float = float(pct_str)
                datos_actualizar["porcentaje_comision"] = int(pct_float * 100)
            except ValueError:
                raise ValueError("El porcentaje debe ser un número válido")

            datos_actualizar["observaciones_liquidacion"] = form_data.get("observaciones", "")

            servicio.actualizar_liquidacion(
                id_liquidacion=self.selected_liquidacion_id,
                datos=datos_actualizar,
                usuario=usuario_sistema
            )

            # 2. Agregar NUEVOS descuentos/bonos ingresados en el formulario
            # Nota: No elimina los existentes, solo agrega los nuevos de la lista temporal.
            for descuento in self.new_discounts:
                 try:
                     servicio.agregar_descuento(
                         id_liquidacion=self.selected_liquidacion_id,
                         tipo=descuento["tipo"],
                         descripcion=descuento["descripcion"],
                         valor=int(descuento["valor"]),
                         usuario=usuario_sistema
                     )
                 except Exception as e:
                     print(f"Error agregando descuento extra: {e}")

            # 3. Agregar NUEVAS bonificaciones ingresadas en el formulario
            for bono in self.new_bonuses:
                 try:
                     servicio.agregar_bonificacion(
                         id_liquidacion=self.selected_liquidacion_id,
                         tipo=bono["tipo"],
                         descripcion=bono["descripcion"],
                         valor=int(bono["valor"]),
                         usuario=usuario_sistema
                     )
                 except Exception as e:
                     print(f"Error agregando bonificación extra: {e}")
            
            async with self:
                self.show_form_modal = False
                self.form_data = {}
                self.new_discounts = []
                self.new_bonuses = []
                self.is_loading = False
            
            # Recargar lista
            yield rx.toast.success("Liquidación actualizada correctamente", position="top-center")
            yield LiquidacionAsesoresState.load_liquidaciones()

        except Exception as e:
            async with self:
                self.error_message = f"Error al actualizar: {str(e)}"
                self.is_loading = False
            yield rx.toast.error(f"Error al actualizar liquidación: {str(e)}", position="top-center")
    
    # Descuentos
    def open_discount_modal(self, id_liquidacion: int):
        """Abre modal para agregar descuento."""
        self.selected_liquidacion_id = id_liquidacion
        self.discount_form = {
            "id_liquidacion": id_liquidacion,
            "tipo": "Descuento Manual",
            "descripcion": "",
            "valor": ""
        }
        self.show_discount_modal = True
        self.error_message = ""
    
    @rx.event(background=True)
    async def save_descuento(self, form_data: Dict):
        """Guarda un descuento y recalcula valor neto."""
        async with self:
            self.is_loading = True
            self.error_message = ""
        
        try:
            print(f"DEBUG: save_descuento called with form_data keys: {list(form_data.keys())}")
            print(f"DEBUG: form_data content: {form_data}")
            
            repo_liquidacion = RepositorioLiquidacionAsesorSQLite(db_manager)
            repo_descuento = RepositorioDescuentoAsesorSQLite(db_manager)
            repo_pago = RepositorioPagoAsesorSQLite(db_manager)
            
            servicio = ServicioLiquidacionAsesores(
                repo_liquidacion=repo_liquidacion,
                repo_descuento=repo_descuento,
                repo_pago=repo_pago
            )
            
            # Validaciones de ID
            # CRITICAL FIX: Usar el ID del estado, no del formulario (evita error [object Object])
            if not self.selected_liquidacion_id:
                print("CRITICAL: selected_liquidacion_id is 0 or None")
                async with self:
                    self.error_message = "Error interno: No hay liquidación seleccionada"
                    self.is_loading = False
                return
            
            id_liquidacion = self.selected_liquidacion_id

            # Validaciones de valor
            try:
                valor = int(form_data.get("valor", 0))
            except ValueError:
                async with self:
                    self.error_message = "El valor debe ser un número válido"
                    self.is_loading = False
                return

            if valor <= 0:
                async with self:
                    self.error_message = "El valor del descuento debe ser mayor a cero"
                    self.is_loading = False
                return
            
            usuario_sistema = "admin"  # TODO: Obtener de AuthState
            servicio.agregar_descuento(
                id_liquidacion=id_liquidacion,
                tipo=form_data["tipo"],
                descripcion=form_data.get("descripcion", "").strip(),
                valor=valor,
                usuario=usuario_sistema
            )
            
            async with self:
                self.show_discount_modal = False
                self.discount_form = {}
            
            # Recargar detalles y lista
            yield rx.toast.success("Descuento agregado correctamente", position="top-center")
            yield LiquidacionAsesoresState.open_detail_modal(id_liquidacion)
            yield LiquidacionAsesoresState.load_liquidaciones()
                
        except Exception as e:
            async with self:
                self.error_message = f"Error al agregar descuento: {str(e)}"
                self.is_loading = False
            yield rx.toast.error(f"Error al agregar descuento: {str(e)}", position="top-center")
    
    @rx.event(background=True)
    async def eliminar_descuento(self, id_descuento: int):
        """Elimina un descuento y recalcula valor neto."""
        print(f"\n{'='*70}")
        print(f"[STATE] eliminar_descuento CALLED")
        print(f"[STATE] id_descuento recibido: {id_descuento} (tipo: {type(id_descuento)})")
        print(f"[STATE] liquidacion_actual: {self.liquidacion_actual.get('id_liquidacion') if self.liquidacion_actual else 'None'}")
        print(f"{'='*70}\n")
        
        async with self:
            self.is_loading = True
            self.error_message = ""
        
        try:
            # Obtener id_liquidacion del estado actual
            if not self.liquidacion_actual:
                raise ValueError("No hay liquidación actual en el estado")
            
            id_liquidacion = self.liquidacion_actual["id_liquidacion"]
            print(f"[STATE] ID Liquidacion extraído: {id_liquidacion}")
            
            repo_liquidacion = RepositorioLiquidacionAsesorSQLite(db_manager)
            repo_descuento = RepositorioDescuentoAsesorSQLite(db_manager)
            repo_pago = RepositorioPagoAsesorSQLite(db_manager)
            
            servicio = ServicioLiquidacionAsesores(
                repo_liquidacion=repo_liquidacion,
                repo_descuento=repo_descuento,
                repo_pago=repo_pago
            )
            
            usuario_sistema = "admin"  # TODO: Obtener de AuthState
            print(f"[STATE] Llamando servicio.eliminar_descuento({id_descuento}, {usuario_sistema})")
            
            eliminado = servicio.eliminar_descuento(id_descuento, usuario_sistema)
            
            print(f"[STATE] Resultado eliminación: {eliminado}")
            
            async with self:
                self.is_loading = False
            
            # Recargar detalles y lista
            yield rx.toast.success("Descuento eliminado correctamente", position="top-center")
            print(f"[STATE] Recargando modal y lista...")
            yield LiquidacionAsesoresState.open_detail_modal(id_liquidacion)
            yield LiquidacionAsesoresState.load_liquidaciones()
            print(f"[STATE] Recarga completada\n")
                
        except Exception as e:
            print(f"[STATE] ❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            async with self:
                self.error_message = f"Error al eliminar descuento: {str(e)}"
                self.is_loading = False
            yield rx.toast.error(f"Error al eliminar descuento: {str(e)}", position="top-center")

    # Helper methods for modals and forms
    def set_form_field(self, field: str, value: Any):
        """Actualiza un campo del formulario de liquidación."""
        self.form_data[field] = value
        
        # Auto-llenar el porcentaje de comisión cuando se selecciona un asesor
        if field == "id_asesor" and value:
            # Buscar el asesor seleccionado por ID
            for asesor in self.asesores_options:
                if asesor["id"] == str(value):  # Convert to string for comparison
                    # El valor ya está en formato de porcentaje (ej: 8 = 8%)
                    comision = asesor.get("comision_porcentaje", 5)
                    self.form_data["porcentaje_comision"] = str(float(comision))
                    break
            # Trigger render update for fetching properties
            return LiquidacionAsesoresState.fetch_advisor_properties(int(value))

    def set_temp_discount_field(self, field: str, value: Any):
        """Actualiza campo del descuento temporal."""
        self.temp_discount[field] = value

    def add_temp_discount(self):
        """Agrega el descuento temporal a la lista."""
        try:
            valor = int(self.temp_discount["valor"])
            if valor <= 0:
                print("Valor debe ser mayor a 0")
                return
            
            self.new_discounts.append({
                "tipo": self.temp_discount["tipo"],
                "descripcion": self.temp_discount["descripcion"],
                "valor": valor
            })
            # Reset temp form (keep type just in case)
            self.temp_discount = {"tipo": "Otros", "descripcion": "", "valor": ""}
        except ValueError:
            pass # Handle invalid number

    def remove_temp_discount(self, item_dict: Dict[str, Any]):
        """Elimina un descuento de la lista temporal basado en sus valores."""
        try:
            # Filtrar la lista para remover el item que coincida
            self.new_discounts = [
                d for d in self.new_discounts 
                if not (d.get("tipo") == item_dict.get("tipo") and 
                        d.get("descripcion") == item_dict.get("descripcion") and 
                        d.get("valor") == item_dict.get("valor"))
            ]
        except Exception as e:
            print(f"Error removing temp discount: {e}")

    def set_temp_bonus_field(self, field: str, value: Any):
        """Actualiza campo del bono temporal."""
        self.temp_bonus[field] = value

    def add_temp_bonus(self):
        """Agrega el bono temporal a la lista."""
        try:
            valor = int(self.temp_bonus["valor"])
            if valor <= 0:
                print("Valor debe ser mayor a 0")
                return
            
            self.new_bonuses.append({
                "tipo": self.temp_bonus["tipo"],
                "descripcion": self.temp_bonus["descripcion"],
                "valor": valor
            })
            # Reset temp (keep type)
            self.temp_bonus = {"tipo": "Bono", "descripcion": "", "valor": ""}
        except ValueError:
            pass 

    def remove_temp_bonus(self, item_dict: Dict[str, Any]):
        """Elimina un bono de la lista temporal basado en sus valores."""
        try:
            # Filtrar la lista para remover el item que coincida
            self.new_bonuses = [
                b for b in self.new_bonuses 
                if not (b.get("tipo") == item_dict.get("tipo") and 
                        b.get("descripcion") == item_dict.get("descripcion") and 
                        b.get("valor") == item_dict.get("valor"))
            ]
        except Exception as e:
            print(f"Error removing temp bonus: {e}")

    def set_discount_field(self, field: str, value: Any):
        """Actualiza un campo del formulario de descuento."""
        self.discount_form[field] = value

    def close_form_modal(self):
        """Cierra el modal de creación."""
        self.show_form_modal = False
        self.form_data = {
            "id_asesor": "",
            "periodo": datetime.now().strftime("%Y-%m"),
            "contratos": [],
            "porcentaje_comision": "5.0",
            "observaciones": ""
        }
        self.error_message = ""

    def close_discount_modal(self):
        """Cierra el modal de descuento."""
        self.show_discount_modal = False
        self.discount_form = {}
        self.error_message = ""
