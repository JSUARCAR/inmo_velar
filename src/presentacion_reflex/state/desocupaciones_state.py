import reflex as rx
from typing import Optional, Dict, Any, List
from src.infraestructura.persistencia.database import db_manager
from src.aplicacion.servicios.servicio_desocupaciones import ServicioDesocupaciones

class DesocupacionesState(rx.State):
    """Estado para gestión de Desocupaciones."""
    
    # Paginación
    current_page: int = 1
    page_size: int = 25
    total_items: int = 0
    
    # Datos
    desocupaciones: List[Dict[str, Any]] = []
    contratos_candidatos: List[Dict[str, Any]] = []
    checklist_actual: List[Dict[str, Any]] = []
    
    # UI State
    is_loading: bool = False
    error_message: str = ""
    
    # Filtros
    filter_estado: str = "Todos"
    estado_options: List[str] = ["Todos", "En Proceso", "Completada", "Cancelada"]
    
    # Modales
    modal_create_open: bool = False
    modal_checklist_open: bool = False
    modal_confirm_finalize_open: bool = False
    
    # Finalize Info
    finalize_info: Dict[str, Any] = {
        "id": 0,
        "direccion": "",
        "inquilino": "",
        "progreso": 0,
        "puede_finalizar": False,
        "mensaje_validacion": ""
    }
    
    # Checklist Modal Info
    checklist_info: Dict[str, Any] = {
        "direccion": "",
        "inquilino": "",
        "fecha_programada": "",
        "estado": "",
        "progreso": 0,
        "tareas_completadas": 0,
        "tareas_total": 0
    }
    
    # Form Data
    id_desocupacion_seleccionada: Optional[int] = None
    form_create_data: Dict[str, Any] = {
        "id_contrato": "",
        "fecha_programada": "",
        "observaciones": ""
    }
    
    observacion_cancelacion: str = ""
    
    @rx.event(background=True)
    async def on_load(self):
        """Carga inicial."""
        async with self:
            self.is_loading = True
            
        try:
            yield DesocupacionesState.load_desocupaciones()
            yield DesocupacionesState.load_contratos_candidatos()
        finally:
            async with self:
                self.is_loading = False

    @rx.event(background=True)
    async def load_desocupaciones(self):
        """Carga lista paginada de desocupaciones."""
        async with self:
            self.is_loading = True
            self.error_message = ""
            
        try:
            servicio = ServicioDesocupaciones(db_manager)
            estado_filtro = self.filter_estado if self.filter_estado != "Todos" else None
            
            resultado = servicio.listar_desocupaciones_paginado(
                page=self.current_page,
                page_size=self.page_size,
                estado=estado_filtro
            )
            
            # Convertir objetos a dicts para serialización
            items = []
            for d in resultado.items:
                progreso = servicio.calcular_progreso(d.id_desocupacion)
                item_dict = {
                    "id": d.id_desocupacion,
                    "id_contrato": d.id_contrato,
                    "direccion": d.direccion_propiedad or "Sin dirección",
                    "inquilino": d.nombre_inquilino or "",
                    "fecha_solicitud": d.fecha_solicitud,
                    "fecha_programada": d.fecha_programada,
                    "estado": d.estado,
                    "progreso": progreso['porcentaje'],
                    "puede_finalizar": progreso['puede_finalizar']
                }
                items.append(item_dict)
            
            async with self:
                self.desocupaciones = items
                self.total_items = resultado.total
                
        except Exception as e:
            async with self:
                self.error_message = f"Error al cargar desocupaciones: {str(e)}"
        finally:
            async with self:
                self.is_loading = False

    @rx.event(background=True)
    async def load_contratos_candidatos(self):
        """Carga contratos disponibles para desocupar."""
        try:
            servicio = ServicioDesocupaciones(db_manager)
            contratos = servicio.listar_contratos_candidatos()
            
            # Formatear para select
            opciones = [
                {
                    "id": str(c["id_contrato"]),
                    "texto": f"#{c['id_contrato']} - {c['direccion']} ({c['inquilino']})"
                }
                for c in contratos
            ]
            
            async with self:
                self.contratos_candidatos = opciones
        except Exception as e:
            print(f"Error cargando candidatos: {e}")

    # --- Acciones CRUD ---

    def set_modal_create_open(self, value: bool):
        self.modal_create_open = value

    def open_create_modal(self):
        self.modal_create_open = True
        self.form_create_data = {
            "id_contrato": "",
            "fecha_programada": "",
            "observaciones": ""
        }
        return DesocupacionesState.load_contratos_candidatos

    def close_create_modal(self):
        self.modal_create_open = False

    def set_id_contrato(self, value: str):
        self.form_create_data["id_contrato"] = value

    def set_fecha_programada(self, value: str):
        self.form_create_data["fecha_programada"] = value

    def set_observaciones(self, value: str):
        self.form_create_data["observaciones"] = value

    @rx.event(background=True)
    async def create_desocupacion(self, form_data: Dict):
        async with self:
            self.is_loading = True
            self.error_message = ""
            
        try:
            servicio = ServicioDesocupaciones(db_manager)
            usuario = "admin" # TODO: Auth
            
            servicio.iniciar_desocupacion(
                id_contrato=int(form_data["id_contrato"]),
                fecha_programada=form_data["fecha_programada"],
                observaciones=form_data.get("observaciones"),
                usuario=usuario
            )
            
            async with self:
                self.modal_create_open = False
            
            yield rx.toast.success("Proceso de desocupación iniciado exitosamente")
            yield DesocupacionesState.load_desocupaciones()
            
        except ValueError as e:
            # Error de validación (contrato duplicado, etc.)
            yield rx.toast.error(str(e))
            async with self:
                self.error_message = str(e)
        except Exception as e:
            yield rx.toast.error(f"Error al crear desocupación: {str(e)}")
            async with self:
                self.error_message = f"Error al crear: {str(e)}"
        finally:
            async with self:
                self.is_loading = False

    @rx.event(background=True)
    async def open_checklist(self, id_desocupacion: int):
        """Abre el modal de checklist con información completa."""
        async with self:
            self.id_desocupacion_seleccionada = id_desocupacion
            self.is_loading = True
        
        try:
            servicio = ServicioDesocupaciones(db_manager)
            
            # Obtener información de la desocupación
            desocupacion = servicio.obtener_desocupacion(id_desocupacion)
            if not desocupacion:
                raise ValueError(f"Desocupación {id_desocupacion} no encontrada")
            
            # Obtener tareas
            tareas = servicio.obtener_checklist(id_desocupacion)
            
            # Calcular progreso
            progreso = servicio.calcular_progreso(id_desocupacion)
            
            # Mapear tareas a diccionarios
            checklist_data = [
                {
                    "id_tarea": t.id_tarea,
                    "descripcion": t.descripcion,
                    "orden": t.orden,
                    "completada": bool(t.completada),
                    "fecha_completada": t.fecha_completada or "",
                    "responsable": t.responsable or "",
                    "observaciones": t.observaciones or ""
                }
                for t in tareas
            ]
            
            async with self:
                self.checklist_actual = checklist_data
                self.checklist_info = {
                    "direccion": desocupacion.direccion_propiedad or "Sin dirección",
                    "inquilino": desocupacion.nombre_inquilino or "Sin inquilino",
                    "fecha_programada": desocupacion.fecha_programada or "",
                    "estado": desocupacion.estado or "",
                    "progreso": progreso['porcentaje'],
                    "tareas_completadas": progreso['completadas'],
                    "tareas_total": progreso['total']
                }
                self.modal_checklist_open = True
                
        except Exception as e:
            yield rx.toast.error(f"Error cargando checklist: {str(e)}")
            async with self:
                self.error_message = f"Error cargando checklist: {str(e)}"
        finally:
            async with self:
                self.is_loading = False

    def close_checklist_modal(self):
        """Cierra el modal de checklist y limpia el estado."""
        self.modal_checklist_open = False
        self.checklist_actual = []
        self.id_desocupacion_seleccionada = None
        self.checklist_info = {
            "direccion": "",
            "inquilino": "",
            "fecha_programada": "",
            "estado": "",
            "progreso": 0,
            "tareas_completadas": 0,
            "tareas_total": 0
        }

    def set_modal_checklist_open(self, value: bool):
        self.modal_checklist_open = value

    @rx.event(background=True)
    async def toggle_tarea(self, id_tarea: int, completed: bool):
        """Marca una tarea como completada."""
        # Solo se puede marcar como completada (no desmarcar)
        if not completed:
            yield rx.toast.warning("Las tareas completadas no se pueden desmarcar")
            return

        try:
            servicio = ServicioDesocupaciones(db_manager)
            usuario = "admin"
            servicio.completar_tarea(id_tarea, usuario)
            
            yield rx.toast.success("✓ Tarea completada")
            
            # Recargar checklist para actualizar estado visual
            if self.id_desocupacion_seleccionada:
                yield DesocupacionesState.open_checklist(self.id_desocupacion_seleccionada)
            
            # También recargar la lista principal para actualizar progreso
            yield DesocupacionesState.load_desocupaciones()
            
        except Exception as e:
            yield rx.toast.error(f"Error al completar tarea: {str(e)}")
            async with self:
                self.error_message = f"Error actualizando tarea: {str(e)}"

    @rx.event(background=True)
    async def open_finalize_modal(self, id_desocupacion: int):
        """Abre el modal de confirmación para finalizar."""
        async with self:
            self.id_desocupacion_seleccionada = id_desocupacion
            self.is_loading = True
            
        try:
            servicio = ServicioDesocupaciones(db_manager)
            desocupacion = servicio.obtener_desocupacion(id_desocupacion)
            progreso = servicio.calcular_progreso(id_desocupacion)
            
            async with self:
                self.finalize_info = {
                    "id": id_desocupacion,
                    "direccion": desocupacion.direccion_propiedad or "",
                    "inquilino": desocupacion.nombre_inquilino or "",
                    "progreso": progreso['porcentaje'],
                    "puede_finalizar": progreso['puede_finalizar'],
                    "mensaje_validacion": "" if progreso['puede_finalizar'] else f"Faltan {progreso['total'] - progreso['completadas']} tareas por completar"
                }
                self.modal_confirm_finalize_open = True
                
        except Exception as e:
            yield rx.toast.error(f"Error al preparar finalización: {str(e)}")
        finally:
            async with self:
                self.is_loading = False

    def close_finalize_modal(self):
        self.modal_confirm_finalize_open = False
        self.id_desocupacion_seleccionada = None

    @rx.event(background=True)
    async def confirm_finalize_process(self):
        """Ejecuta la finalización del proceso."""
        async with self:
            self.is_loading = True
            
        try:
            servicio = ServicioDesocupaciones(db_manager)
            
            # Nota: Ahora permitimos finalizar aunque haya tareas pendientes (Forzado)
            # El servicio se encargará de autocompletarlas.
            
            servicio.finalizar_desocupacion(self.id_desocupacion_seleccionada, "admin")
            
            async with self:
                self.modal_confirm_finalize_open = False
            
            yield rx.toast.success("Proceso finalizado exitosamente. Contrato cerrado y propiedad disponible.")
            yield DesocupacionesState.load_desocupaciones()
            
        except Exception as e:
             yield rx.toast.error(f"Error al finalizar: {str(e)}")
             async with self:
                self.error_message = f"Error al finalizar: {str(e)}"
        finally:
            async with self:
                self.is_loading = False

    # Filtros y Paginación
    def set_filter_estado(self, value: str):
        self.filter_estado = value
        self.current_page = 1
        return DesocupacionesState.load_desocupaciones

    def next_page(self):
        if self.current_page * self.page_size < self.total_items:
            self.current_page += 1
            return DesocupacionesState.load_desocupaciones

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            return DesocupacionesState.load_desocupaciones
