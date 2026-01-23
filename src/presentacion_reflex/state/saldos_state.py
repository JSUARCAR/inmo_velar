
import reflex as rx
from typing import List, Dict, Any, Optional
from src.aplicacion.servicios.servicio_saldos_favor import ServicioSaldosFavor
from src.infraestructura.persistencia.database import db_manager
from src.dominio.entidades.saldo_favor import SaldoFavor
from src.presentacion_reflex.state.auth_state import AuthState

class SaldoModel(rx.Base):
    """Modelo serializable para Reflex."""
    id_saldo: int
    fecha_generacion: str
    tipo_beneficiario: str
    id_propietario: Optional[int] = None
    id_asesor: Optional[int] = None
    motivo: str
    valor_saldo: float
    estado: str
    valor_formateado: str

class SaldosState(rx.State):
    """Estado para gestión de Saldos a Favor."""
    
    saldos: List[SaldoModel] = []
    is_loading: bool = False
    error_message: str = ""
    
    # Filters
    filter_tipo: str = "Todos" # Todos, Propietario, Asesor
    filter_estado: str = "Pendiente" # Pendiente, Historial (Aplicado/Devuelto), Todos
    
    # Form Modal State
    show_create_modal: bool = False
    
    # Form Fields
    form_tipo_beneficiario: str = "Propietario"
    form_id_beneficiario: int = 0
    form_valor: int = 0
    form_motivo: str = ""
    form_observaciones: str = ""

    @rx.event(background=True)
    async def load_saldos(self):
        """Carga lista de saldos con filtros."""
        async with self:
            self.is_loading = True
            self.error_message = ""
            
        try:
            servicio = ServicioSaldosFavor(db_manager)
            
            # Mapeo de filtros UI a Backend parameters
            tipo = None if self.filter_tipo == "Todos" else self.filter_tipo
            estado = None
            if self.filter_estado == "Pendiente":
                estado = 'Pendiente'
            
            # Usamos listar_saldos base
            lista_entidades = servicio.listar_saldos(tipo_beneficiario=tipo, estado=estado)
            
            # Refinamiento si es Historial (excluir pendientes)
            if self.filter_estado == "Historial":
                lista_entidades = [s for s in lista_entidades if s.estado != 'Pendiente']

            # MAPEO Entidad -> Modelo Reflex
            modelos = []
            for ent in lista_entidades:
                modelos.append(
                    SaldoModel(
                        id_saldo=ent.id_saldo_favor, # Mapeo clave
                        fecha_generacion=ent.fecha_generacion or "",
                        tipo_beneficiario=ent.tipo_beneficiario,
                        id_propietario=ent.id_propietario,
                        id_asesor=ent.id_asesor,
                        motivo=ent.motivo,
                        valor_saldo=ent.valor_saldo,
                        estado=ent.estado,
                        valor_formateado=ent.valor_formateado
                    )
                )

            async with self:
                self.saldos = modelos
                self.is_loading = False
        except Exception as e:
            async with self:
                self.error_message = str(e)
                self.is_loading = False

    def open_create_modal(self):
        self.form_tipo_beneficiario = "Propietario"
        self.form_id_beneficiario = 0
        self.form_valor = 0
        self.form_motivo = ""
        self.form_observaciones = ""
        self.show_create_modal = True

    def close_create_modal(self):
        self.show_create_modal = False
        
    def set_filter_tipo(self, value: str):
        self.filter_tipo = value
        
    def set_filter_estado(self, value: str):
        self.filter_estado = value

    # Custom Setters para evitar tipos str vs int en inputs
    def set_form_id_beneficiario_safe(self, value: str):
        if not value:
            self.form_id_beneficiario = 0
        try:
            self.form_id_beneficiario = int(value)
        except ValueError:
            pass

    def set_form_valor_safe(self, value: str):
        if not value:
            self.form_valor = 0
        try:
            self.form_valor = int(value)
        except ValueError:
            pass

    # Explicit setters to avoid warnings
    def set_form_motivo(self, value: str):
        self.form_motivo = value

    def set_form_observaciones(self, value: str):
        self.form_observaciones = value

    def set_show_create_modal(self, value: bool):
        self.show_create_modal = value

    def set_form_tipo_beneficiario(self, value: str):
        self.form_tipo_beneficiario = value

    @rx.event(background=True)
    async def create_saldo(self):
        """Crea un nuevo saldo."""
        async with self:
            self.is_loading = True
            current_user = await self.get_state(AuthState)
            usuario = current_user.user["nombre_usuario"] if current_user.user else "sistema"

        try:
            servicio = ServicioSaldosFavor(db_manager)
            servicio.registrar_saldo(
                tipo_beneficiario=self.form_tipo_beneficiario,
                id_beneficiario=int(self.form_id_beneficiario),
                valor=int(self.form_valor),
                motivo=self.form_motivo,
                observaciones=self.form_observaciones,
                usuario=usuario
            )
            
            async with self:
                self.show_create_modal = False
                self.is_loading = False
            
            # Reload
            await self.load_saldos()
                
        except Exception as e:
            async with self:
                self.error_message = str(e)
                self.is_loading = False

    @rx.event(background=True)
    async def action_saldo(self, id_saldo: int, action: str):
        """
        Ejecuta acción sobre saldo (aplicar o devolver).
        Action: 'aplicar' | 'devolver'
        """
        async with self:
            self.is_loading = True
            current_user = await self.get_state(AuthState)
            usuario = current_user.user["nombre_usuario"] if current_user.user else "sistema"
            
        try:
            servicio = ServicioSaldosFavor(db_manager)
            if action == 'aplicar':
                servicio.aplicar_saldo(id_saldo, "Aplicado desde web", usuario)
            elif action == 'devolver':
                servicio.devolver_saldo(id_saldo, "Devolución registrada desde web", usuario)
            elif action == 'eliminar':
                servicio.eliminar_saldo(id_saldo, usuario)
            
            async with self:
                self.is_loading = False
            
            await self.load_saldos()

        except Exception as e:
            async with self:
                self.error_message = str(e)
                self.is_loading = False
