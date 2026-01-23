"""
Entidad de Dominio: LiquidacionAsesor
Representa una liquidación de comisión para un asesor inmobiliario.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class LiquidacionAsesor:
    """
    Entidad que representa una liquidación de comisión de asesor.
    
    Business Rules:
    - UNIQUE constraint: (id_contrato_a, periodo_liquidacion)
    - porcentaje_comision debe estar entre 0-10000 (representa 0.00% - 100.00%)
    - comision_bruta >= 0
    - total_descuentos >= 0
    - valor_neto_asesor = comision_bruta - total_descuentos
    - Estados permitidos: Pendiente, Aprobada, Pagada, Anulada
    - Flujo de estados: Pendiente → Aprobada → Pagada
    - No se puede anular si está en estado Pagada
    """
    
    # Identificación
    id_liquidacion_asesor: Optional[int] = None
    id_contrato_a: int = 0  # FK a CONTRATOS_ARRENDAMIENTOS_OLD
    id_asesor: int = 0  # FK a ASESORES
    
    # Período y Cálculo
    periodo_liquidacion: str = ""  # Formato: 'YYYY-MM'
    canon_arrendamiento_liquidado: int = 0  # Canon del mes
    porcentaje_comision: int = 0  # Representa 0-10000 (0.00% - 100.00%)
    comision_bruta: int = 0  # Calculada: canon × (porcentaje/100)
    total_descuentos: int = 0  # Suma de descuentos aplicados
    total_bonificaciones: int = 0 # Suma de ingresos adicionales/bonificaciones
    valor_neto_asesor: int = 0  # comision_bruta + total_bonificaciones - total_descuentos
    
    # Estado y Flujo
    estado_liquidacion: str = "Pendiente"  # Pendiente, Aprobada, Pagada, Anulada
    fecha_creacion: Optional[str] = None
    fecha_aprobacion: Optional[str] = None
    usuario_creador: Optional[str] = None
    usuario_aprobador: Optional[str] = None
    
    # Observaciones
    observaciones_liquidacion: Optional[str] = None
    motivo_anulacion: Optional[str] = None
    
    # Auditoría
    created_at: Optional[str] = field(default_factory=lambda: datetime.now().isoformat())
    created_by: Optional[str] = None
    updated_at: Optional[str] = None
    updated_by: Optional[str] = None
    
    # Campo adicional (JOIN con ASESORES/PERSONAS)
    nombre_asesor: Optional[str] = None  # Nombre completo del asesor (desde PERSONAS)
    
    # Estados permitidos
    ESTADOS = ['Pendiente', 'Aprobada', 'Pagada', 'Anulada']
    
    def __post_init__(self):
        """Validaciones de reglas de negocio"""
        if self.comision_bruta < 0:
            raise ValueError("La comisión bruta debe ser mayor o igual a cero")
        
        if self.porcentaje_comision < 0 or self.porcentaje_comision > 10000:
            raise ValueError("El porcentaje de comisión debe estar entre 0 y 10000 (0.00% - 100.00%)")
        
        if self.total_descuentos < 0:
            raise ValueError("El total de descuentos debe ser mayor o igual a cero")

        if self.total_bonificaciones < 0:
            raise ValueError("El total de bonificaciones debe ser mayor o igual a cero")
        
        if self.estado_liquidacion not in self.ESTADOS:
            raise ValueError(f"Estado inválido: {self.estado_liquidacion}. "
                           f"Debe ser uno de: {', '.join(self.ESTADOS)}")
        
        # Validar formato de período (YYYY-MM)
        if self.periodo_liquidacion and len(self.periodo_liquidacion) > 0:
            import re
            if not re.match(r'^\d{4}-\d{2}$', self.periodo_liquidacion):
                raise ValueError(f"Formato de período inválido: {self.periodo_liquidacion}. "
                               "Use formato YYYY-MM")
    
    # ==================== Propiedades de Negocio ====================
    
    @property
    def esta_pendiente(self) -> bool:
        """Verifica si la liquidación está pendiente de aprobación"""
        return self.estado_liquidacion == "Pendiente"
    
    @property
    def esta_aprobada(self) -> bool:
        """Verifica si la liquidación fue aprobada"""
        return self.estado_liquidacion == "Aprobada"
    
    @property
    def esta_pagada(self) -> bool:
        """Verifica si la liquidación ya fue pagada"""
        return self.estado_liquidacion == "Pagada"
    
    @property
    def esta_anulada(self) -> bool:
        """Verifica si la liquidación fue anulada"""
        return self.estado_liquidacion == "Anulada"
    
    @property
    def puede_aprobarse(self) -> bool:
        """Verifica si la liquidación puede ser aprobada"""
        return self.esta_pendiente
    
    @property
    def puede_anularse(self) -> bool:
        """Verifica si la liquidación puede ser anulada"""
        # No se puede anular una liquidación ya pagada
        return not self.esta_pagada and not self.esta_anulada
    
    @property
    def puede_editarse(self) -> bool:
        """Verifica si la liquidación puede ser editada"""
        # Solo se puede editar si está pendiente
        return self.esta_pendiente
    
    @property
    def porcentaje_real(self) -> float:
        """Retorna el porcentaje de comisión en formato decimal (ej: 5.5 para 5.5%)"""
        return self.porcentaje_comision / 100.0
    
    # ==================== Métodos de Cálculo ====================
    
    @staticmethod
    def calcular_comision_bruta(canon: int, porcentaje: int) -> int:
        """
        Calcula la comisión bruta a partir del canon y porcentaje.
        
        Args:
            canon: Canon de arrendamiento
            porcentaje: Porcentaje en formato 0-10000 (representa 0.00% - 100.00%)
        
        Returns:
            Comisión bruta calculada
        """
        return int((canon * porcentaje) / 10000)
    
    def calcular_valor_neto(self, total_descuentos: int, total_bonificaciones: int = 0) -> int:
        """
        Calcula el valor neto a pagar al asesor.
        
        Args:
            total_descuentos: Total de descuentos a aplicar
            total_bonificaciones: Total de bonificaciones a sumar
        
        Returns:
            Valor neto (comisión bruta + bonificaciones - descuentos)
        """
        comision_base = self.comision_bruta
        # Use existing value if not passed? No, logic usually passes current state.
        # But here method takes arguments.
        # If I use self.comision_bruta, it's fine.
        return max(0, comision_base + total_bonificaciones - total_descuentos)
    
    def recalcular_valor_neto(self, nuevo_total_descuentos: int, nuevo_total_bonificaciones: Optional[int] = None) -> None:
        """
        Recalcula el valor neto con un nuevo total de descuentos y/o bonificaciones.
        
        Args:
            nuevo_total_descuentos: Nuevo total de descuentos
            nuevo_total_bonificaciones: Nuevo total de bonificaciones (opcional, usa actual si None)
        """
        if nuevo_total_descuentos < 0:
            raise ValueError("El total de descuentos no puede ser negativo")
            
        if nuevo_total_bonificaciones is not None:
            if nuevo_total_bonificaciones < 0:
                raise ValueError("El total de bonificaciones no puede ser negativo")
            self.total_bonificaciones = nuevo_total_bonificaciones
            
        self.total_descuentos = nuevo_total_descuentos
        self.valor_neto_asesor = self.calcular_valor_neto(self.total_descuentos, self.total_bonificaciones)
        self.updated_at = datetime.now().isoformat()
    
    # ==================== Métodos de Acción ====================
    
    def aprobar(self, usuario_aprobador: str) -> None:
        """
        Aprueba la liquidación.
        
        Args:
            usuario_aprobador: Usuario que aprueba
        
        Raises:
            ValueError: Si la liquidación no puede ser aprobada
        """
        if not self.puede_aprobarse:
            raise ValueError(f"No se puede aprobar una liquidación en estado {self.estado_liquidacion}")
        
        self.estado_liquidacion = "Aprobada"
        self.fecha_aprobacion = datetime.now().isoformat()
        self.usuario_aprobador = usuario_aprobador
        self.updated_at = datetime.now().isoformat()
        self.updated_by = usuario_aprobador
    
    def marcar_como_pagada(self, usuario: str) -> None:
        """
        Marca la liquidación como pagada.
        
        Args:
            usuario: Usuario que registra el pago
        
        Raises:
            ValueError: Si la liquidación no está aprobada
        """
        if not self.esta_aprobada:
            raise ValueError("Solo se pueden marcar como pagadas las liquidaciones aprobadas")
        
        self.estado_liquidacion = "Pagada"
        self.updated_at = datetime.now().isoformat()
        self.updated_by = usuario
    
    def anular(self, motivo: str, usuario: str) -> None:
        """
        Anula la liquidación.
        
        Args:
            motivo: Motivo de la anulación
            usuario: Usuario que anula
        
        Raises:
            ValueError: Si la liquidación no puede ser anulada
        """
        if not self.puede_anularse:
            raise ValueError("No se puede anular una liquidación pagada")
        
        if not motivo or motivo.strip() == "":
            raise ValueError("Debe especificar un motivo para la anulación")
        
        self.estado_liquidacion = "Anulada"
        self.motivo_anulacion = motivo
        self.updated_at = datetime.now().isoformat()
        self.updated_by = usuario
