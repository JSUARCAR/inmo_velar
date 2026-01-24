import reflex as rx
from typing import Optional, Dict, Any, List
from src.infraestructura.persistencia.database import db_manager
from src.aplicacion.servicios.servicio_seguros import ServicioSeguros


class SegurosState(rx.State):
    """
    Estado para gestión de Seguros y Pólizas.
    Maneja paginación, filtros y CRUD operations para seguros y sus pólizas.
    """
    
    # Paginación
    current_page: int = 1
    page_size: int = 25
    total_items: int = 0
    
    # Filtros
    search_text: str = ""
    filter_estado: str = "Activos"  # "Todos", "Activos", "Inactivos"
    
    # Estado de carga
    is_loading: bool = False
    error_message: str = ""
    
    # Datos
    seguros: List[Dict[str, Any]] = []
    polizas: List[Dict[str, Any]] = []
    contratos_candidatos: List[Dict[str, Any]] = []
    
    # Modal state - Seguros
    show_seguro_modal: bool = False
    is_editing_seguro: bool = False
    seguro_form_data: Dict[str, Any] = {}
    
    # Modal state - Pólizas
    show_poliza_modal: bool = False
    is_editing_poliza: bool = False
    poliza_form_data: Dict[str, Any] = {}
    
    # Modal state - Detalle
    show_detail_modal: bool = False
    selected_seguro: Optional[Dict[str, Any]] = None
    seguro_polizas: List[Dict[str, Any]] = []
    
    def on_load(self):
        """Carga inicial al montar la página."""
        yield SegurosState.load_seguros
    
    @rx.event(background=True)
    async def load_seguros(self):
        """Carga seguros con filtros y paginación."""
        async with self:
            self.is_loading = True
            self.error_message = ""
        
        try:
            # Obtener valores de filtros
            search = self.search_text
            estado_filter = self.filter_estado
            
            # Determinar solo_activos
            solo_activos = None
            if estado_filter == "Activos":
                solo_activos = True
            elif estado_filter == "Inactivos":
                solo_activos = False
            
            # Servicio
            servicio = ServicioSeguros(db_manager)
            seguros_list = servicio.listar_seguros(solo_activos=solo_activos)
            
            # Filtrar por búsqueda si existe
            if search.strip():
                search_lower = search.lower()
                seguros_list = [
                    s for s in seguros_list
                    if search_lower in s.nombre_seguro.lower()
                ]
            
            # Convertir a dict
            seguros_data = [
                {
                    "id_seguro": s.id_seguro,
                    "nombre_seguro": s.nombre_seguro,
                    "porcentaje_seguro": s.porcentaje_seguro,
                    "fecha_inicio_seguro": s.fecha_inicio_seguro or "",
                    "estado_seguro": s.estado_seguro,
                    "fecha_ingreso_seguro": s.fecha_ingreso_seguro or "",
                    "motivo_inactivacion": s.motivo_inactivacion or "",
                }
                for s in seguros_list
            ]
            
            async with self:
                self.seguros = seguros_data
                self.total_items = len(seguros_data)
                self.is_loading = False
                
        except Exception as e:
            pass  # print(f"Error cargando seguros: {e}") [OpSec Removed]
            import traceback
            traceback.print_exc()
            async with self:
                self.error_message = f"Error al cargar seguros: {str(e)}"
                self.is_loading = False
    
    @rx.event(background=True)
    async def load_polizas(self):
        """Carga todas las pólizas registradas."""
        try:
            servicio = ServicioSeguros(db_manager)
            polizas_list = servicio.listar_polizas()
            
            # Convertir a dict
            polizas_data = [
                {
                    "id_poliza": p.id_poliza,
                    "id_contrato": p.id_contrato,
                    "id_seguro": p.id_seguro,
                    "numero_poliza": p.numero_poliza,
                    "fecha_inicio": p.fecha_inicio,
                    "fecha_fin": p.fecha_fin,
                    "estado": p.estado,
                }
                for p in polizas_list
            ]
            
            async with self:
                self.polizas = polizas_data
                
        except Exception as e:
            pass  # print(f"Error cargando pólizas: {e}") [OpSec Removed]
            async with self:
                self.error_message = f"Error al cargar pólizas: {str(e)}"
    
    def load_contratos_for_poliza(self):
        """Carga contratos candidatos para asignar póliza."""
        try:
            servicio = ServicioSeguros(db_manager)
            contratos = servicio.listar_contratos_candidatos()
            
            self.contratos_candidatos = [
                {
                    "value": str(c["id_contrato"]),
                    "label": f"{c['codigo_contrato']} - {c['direccion']}"
                }
                for c in contratos
            ]
        except Exception as e:
            pass  # print(f"Error cargando contratos: {e}") [OpSec Removed]
            self.contratos_candidatos = []
    
    # Filtros y búsqueda
    def set_search(self, value: str):
        """Actualiza búsqueda."""
        self.search_text = value
    
    def search_seguros(self):
        """Ejecuta búsqueda."""
        return SegurosState.load_seguros
    
    def set_filter_estado(self, value: str):
        """Cambia filtro de estado."""
        self.filter_estado = value
        return SegurosState.load_seguros
    
    # Modal CRUD - Seguros
    def open_create_seguro_modal(self):
        """Abre modal para crear nuevo seguro."""
        self.is_editing_seguro = False
        self.seguro_form_data = {
            "nombre_seguro": "",
            "porcentaje_seguro": "",
            "fecha_inicio_seguro": "",
        }
        self.show_seguro_modal = True
        self.error_message = ""
    
    def open_edit_seguro_modal(self, id_seguro: int):
        """Abre modal para editar seguro existente."""
        try:
            servicio = ServicioSeguros(db_manager)
            seguro = servicio.obtener_seguro(id_seguro)
            
            if seguro:
                self.is_editing_seguro = True
                self.seguro_form_data = {
                    "id_seguro": seguro.id_seguro,
                    "nombre_seguro": seguro.nombre_seguro or "",
                    "porcentaje_seguro": str(seguro.porcentaje_seguro) if seguro.porcentaje_seguro else "",
                    "fecha_inicio_seguro": seguro.fecha_inicio_seguro or "",
                }
                self.show_seguro_modal = True
                self.error_message = ""
        except Exception as e:
            pass  # print(f"Error cargando seguro: {e}") [OpSec Removed]
            self.error_message = f"Error al cargar seguro: {str(e)}"
    
    def close_seguro_modal(self):
        """Cierra el modal de seguro."""
        self.show_seguro_modal = False
        self.error_message = ""
        self.seguro_form_data = {}
    
    def save_seguro(self, form_data: Dict):
        """Guarda seguro (crear o editar)."""
        try:
            servicio = ServicioSeguros(db_manager)
            
            # Validaciones
            if not form_data.get("nombre_seguro"):
                self.error_message = "El nombre del seguro es requerido"
                return
            
            if not form_data.get("porcentaje_seguro"):
                self.error_message = "El porcentaje es requerido"
                return
            
            # Preparar datos
            datos = {
                "nombre_seguro": form_data["nombre_seguro"],
                "porcentaje_seguro": int(form_data["porcentaje_seguro"]),
                "fecha_inicio_seguro": form_data.get("fecha_inicio_seguro") or None,
            }
            
            if self.is_editing_seguro:
                # Actualizar
                id_seg = form_data.get("id_seguro")
                servicio.actualizar_seguro(id_seg, datos, usuario_sistema="admin")
            else:
                # Crear nuevo
                servicio.crear_seguro(datos, usuario_sistema="admin")
            
            # Cerrar modal y recargar
            self.close_seguro_modal()
            return SegurosState.load_seguros
            
        except Exception as e:
            pass  # print(f"Error guardando seguro: {e}") [OpSec Removed]
            import traceback
            traceback.print_exc()
            self.error_message = f"Error: {str(e)}"
    
    def toggle_estado_seguro(self, id_seguro: int, estado_actual: int):
        """Activa o desactiva un seguro."""
        try:
            servicio = ServicioSeguros(db_manager)
            
            # Convert estado_actual to int if it's a dict or other type
            estado_int = int(estado_actual) if isinstance(estado_actual, (int, float, str)) else int(estado_actual.get("estado_seguro", 0) if isinstance(estado_actual, dict) else 0)
            
            if estado_int == 1:
                # Desactivar
                servicio.desactivar_seguro(id_seguro, motivo="Desactivado desde interfaz", usuario_sistema="admin")
            else:
                # Activar
                servicio.activar_seguro(id_seguro, usuario_sistema="admin")
            
            return SegurosState.load_seguros
        except Exception as e:
            pass  # print(f"Error cambiando estado: {e}") [OpSec Removed]
            self.error_message = f"Error al cambiar estado: {str(e)}"
    
    # Modal CRUD - Pólizas
    def open_create_poliza_modal(self):
        """Abre modal para crear nueva póliza."""
        self.load_contratos_for_poliza()
        self.is_editing_poliza = False
        self.poliza_form_data = {
            "id_contrato": "",
            "id_seguro": "",
            "numero_poliza": "",
            "fecha_inicio": "",
            "fecha_fin": "",
        }
        self.show_poliza_modal = True
        self.error_message = ""
    
    def close_poliza_modal(self):
        """Cierra el modal de póliza."""
        self.show_poliza_modal = False
        self.error_message = ""
        self.poliza_form_data = {}
    
    def save_poliza(self, form_data: Dict):
        """Guarda póliza."""
        try:
            servicio = ServicioSeguros(db_manager)
            
            # Validaciones
            if not form_data.get("id_contrato"):
                self.error_message = "El contrato es requerido"
                return
            
            if not form_data.get("id_seguro"):
                self.error_message = "El seguro es requerido"
                return
            
            if not form_data.get("numero_poliza"):
                self.error_message = "El número de póliza es requerido"
                return
            
            # Crear póliza
            servicio.crear_poliza(
                id_contrato=int(form_data["id_contrato"]),
                id_seguro=int(form_data["id_seguro"]),
                fecha_inicio=form_data.get("fecha_inicio", ""),
                fecha_fin=form_data.get("fecha_fin", ""),
                numero_poliza=form_data["numero_poliza"],
                usuario="admin"
            )
            
            # Cerrar modal y recargar
            self.close_poliza_modal()
            return SegurosState.load_polizas
            
        except Exception as e:
            pass  # print(f"Error guardando póliza: {e}") [OpSec Removed]
            import traceback
            traceback.print_exc()
            self.error_message = f"Error: {str(e)}"
    
    # Modal Detalle
    def open_detail_modal(self, id_seguro: int):
        """Abre modal de detalle de seguro con sus pólizas."""
        try:
            servicio = ServicioSeguros(db_manager)
            seguro = servicio.obtener_seguro(id_seguro)
            
            if seguro:
                self.selected_seguro = {
                    "id_seguro": seguro.id_seguro,
                    "nombre_seguro": seguro.nombre_seguro,
                    "porcentaje_seguro": seguro.porcentaje_seguro,
                    "fecha_inicio_seguro": seguro.fecha_inicio_seguro or "N/A",
                    "estado_seguro": "Activo" if seguro.estado_seguro == 1 else "Inactivo",
                    "fecha_ingreso_seguro": seguro.fecha_ingreso_seguro or "N/A",
                    "motivo_inactivacion": seguro.motivo_inactivacion or "N/A",
                }
                
                # Cargar pólizas del seguro
                todas_polizas = servicio.listar_polizas()
                polizas_seguro = [
                    {
                        "id_poliza": p.id_poliza,
                        "numero_poliza": p.numero_poliza,
                        "fecha_inicio": p.fecha_inicio,
                        "fecha_fin": p.fecha_fin,
                        "estado": p.estado,
                        "id_contrato": p.id_contrato,
                    }
                    for p in todas_polizas
                    if p.id_seguro == id_seguro
                ]
                
                self.seguro_polizas = polizas_seguro
                self.show_detail_modal = True
                self.error_message = ""
        except Exception as e:
            pass  # print(f"Error cargando detalle: {e}") [OpSec Removed]
            self.error_message = f"Error al cargar detalle: {str(e)}"
    
    def close_detail_modal(self):
        """Cierra el modal de detalle."""
        self.show_detail_modal = False
        self.selected_seguro = None
        self.seguro_polizas = []
