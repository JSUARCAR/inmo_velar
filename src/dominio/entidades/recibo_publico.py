"""
Entidad de Dominio: ReciboPublico
Representa un recibo de servicio público (Agua, Luz, Gas, etc.) asociado a una propiedad.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime, date


@dataclass
class ReciboPublico:
    """
    Entidad que representa un recibo de servicio público.
    
    Business Rules:
    - valor_recibo debe ser >= 0
    - UNIQUE constraint: (id_propiedad, periodo_recibo, tipo_servicio)
    - tipo_servicio debe estar en: Agua, Luz, Gas, Internet, Teléfono, Aseo, Otros
    - estado debe estar en: Pendiente, Pagado, Vencido
    - Si fecha_vencimiento < hoy y estado = 'Pendiente' -> debería ser 'Vencido'
    """
    
    # Identificación
    id_recibo_publico: Optional[int] = None
    id_propiedad: int = 0  # FK a PROPIEDADES
    
    # Detalles del Recibo
    periodo_recibo: str = ""  # Formato: 'YYYY-MM'
    tipo_servicio: str = ""  # Agua, Luz, Gas, Internet, Teléfono, Aseo, Otros
    valor_recibo: int = 0  # Valor en pesos colombianos
    
    # Fechas
    fecha_vencimiento: Optional[str] = None  # Formato: 'YYYY-MM-DD'
    fecha_pago: Optional[str] = None  # Formato: 'YYYY-MM-DD'
    
    # Comprobante y Estado
    comprobante: Optional[str] = None  # Referencia o número de transacción
    estado: str = "Pendiente"  # Pendiente, Pagado, Vencido
    
    # Detalle de Periodo
    fecha_desde: Optional[str] = None # Formato: 'YYYY-MM-DD'
    fecha_hasta: Optional[str] = None # Formato: 'YYYY-MM-DD'
    dias_facturados: int = 0
    
    # Auditoría
    created_at: Optional[str] = field(default_factory=lambda: datetime.now().isoformat())
    created_by: Optional[str] = None
    updated_at: Optional[str] = None
    updated_by: Optional[str] = None
    
    # Tipos de servicio permitidos
    TIPOS_SERVICIO = ['Agua', 'Luz', 'Gas', 'Internet', 'Teléfono', 'Aseo', 'Otros']
    ESTADOS = ['Pendiente', 'Pagado', 'Vencido']
    
    def __post_init__(self):
        """Validaciones de reglas de negocio"""
        if self.valor_recibo < 0:
            raise ValueError("El valor del recibo debe ser mayor o igual a cero")
        
        if self.tipo_servicio and self.tipo_servicio not in self.TIPOS_SERVICIO:
            raise ValueError(f"Tipo de servicio inválido: {self.tipo_servicio}. "
                           f"Debe ser uno de: {', '.join(self.TIPOS_SERVICIO)}")
        
        if self.estado not in self.ESTADOS:
            raise ValueError(f"Estado inválido: {self.estado}. "
                           f"Debe ser uno de: {', '.join(self.ESTADOS)}")
        
        # Validar formato de período (YYYY-MM)
        if self.periodo_recibo and len(self.periodo_recibo) > 0:
            import re
            if not re.match(r'^\d{4}-\d{2}$', self.periodo_recibo):
                raise ValueError(f"Formato de período inválido: {self.periodo_recibo}. "
                               "Use formato YYYY-MM")
    
    @property
    def esta_pagado(self) -> bool:
        """Verifica si el recibo ya fue pagado"""
        return self.estado == "Pagado"
    
    @property
    def esta_vencido(self) -> bool:
        """Verifica si el recibo está vencido"""
        if self.estado == "Vencido":
            return True
        
        # Si está pendiente y tiene fecha de vencimiento pasada
        if self.estado == "Pendiente" and self.fecha_vencimiento:
            try:
                fecha_venc = date.fromisoformat(self.fecha_vencimiento)
                return fecha_venc < date.today()
            except (ValueError, TypeError):
                return False
        
        return False
    
    @property
    def dias_para_vencimiento(self) -> Optional[int]:
        """Calcula los días que faltan para el vencimiento (negativo si ya venció)"""
        if not self.fecha_vencimiento:
            return None
        
        try:
            fecha_venc = date.fromisoformat(self.fecha_vencimiento)
            delta = fecha_venc - date.today()
            return delta.days
        except (ValueError, TypeError):
            return None
    
    def marcar_como_pagado(self, fecha_pago: str, comprobante: str) -> None:
        """
        Marca el recibo como pagado.
        
        Args:
            fecha_pago: Fecha del pago (YYYY-MM-DD)
            comprobante: Referencia o número de comprobante
        
        Raises:
            ValueError: Si el recibo ya está pagado
        """
        if self.esta_pagado:
            raise ValueError("El recibo ya está marcado como pagado")
        
        self.estado = "Pagado"
        self.fecha_pago = fecha_pago
        self.comprobante = comprobante
        self.updated_at = datetime.now().isoformat()
    
    def actualizar_estado_vencimiento(self) -> bool:
        """
        Actualiza el estado a 'Vencido' si está pendiente y pasó la fecha de vencimiento.
        
        Returns:
            True si se cambió el estado, False si no
        """
        if self.estado == "Pendiente" and self.esta_vencido:
            self.estado = "Vencido"
            self.updated_at = datetime.now().isoformat()
            return True
        return False
