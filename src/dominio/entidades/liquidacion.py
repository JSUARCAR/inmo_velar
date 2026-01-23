"""
Entidad de Dominio: Liquidación
Representa el estado de cuenta mensual del propietario.
Una liquidación puede existir ANTES de recibir el pago del inquilino (adelanto).
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class Liquidacion:
    """
    Entidad que representa el estado de cuenta mensual del propietario.
    
    Business Rules:
    - Solo puede haber UNA liquidación por contrato por período
    - Neto a pagar = Total Ingresos - Total Egresos
    - Estados válidos: 'En Proceso', 'Aprobada', 'Pagada', 'Cancelada'
    - Transiciones de estado controladas por roles
    """
    
    # Identificación
    id_liquidacion: Optional[int] = None
    id_contrato_m: int = 0  # FK a CONTRATOS_MANDATOS
    
    # Período
    periodo: str = ""  # Formato 'YYYY-MM' (ej: '2024-10')
    fecha_generacion: str = ""  # Cuándo se creó este estado de cuenta
    
    # Cálculo de Ingresos
    canon_bruto: int = 0  # Canon pactado en el contrato
    otros_ingresos: int = 0  # Multas cobradas al inquilino, etc.
    total_ingresos: int = 0  # = canon_bruto + otros_ingresos
    
    # Cálculo de Egresos
    comision_porcentaje: int = 0  # Guardado por si cambia en el futuro (en base 10000)
    comision_monto: int = 0  # Calculado: canon_bruto * (comision_porcentaje / 10000)
    iva_comision: int = 0  # Calculado: comision_monto * 19%
    impuesto_4x1000: int = 0  # Calculado: total_ingresos * 0.004
    gastos_administracion: int = 0  # Cuota admin del conjunto pagada por inmob.
    gastos_servicios: int = 0  # Agua, luz común pagada por inmob.
    gastos_reparaciones: int = 0  # Incidentes/mantenimientos del mes
    otros_egresos: int = 0  # Imprevistos
    total_egresos: int = 0  # Suma de todos los egresos
    
    # Resultado Final
    neto_a_pagar: int = 0  # total_ingresos - total_egresos
    
    # Estado del Proceso
    estado_liquidacion: str = "En Proceso"  
    # Estados: 'En Proceso', 'Aprobada', 'Pagada', 'Cancelada'
    
    # Pago al Propietario
    fecha_pago: Optional[str] = None  # Cuándo se transfirió el dinero
    metodo_pago: Optional[str] = None  # 'Transferencia Electrónica', etc.
    referencia_pago: Optional[str] = None  # Número de comprobante bancario
    
    # Observaciones
    observaciones: Optional[str] = None
    motivo_cancelacion: Optional[str] = None  # Si estado = 'Cancelada'
    
    # Auditoría y Control
    aprobada_por: Optional[str] = None  # Usuario que cambió a 'Aprobada'
    aprobada_en: Optional[str] = None
    pagada_por: Optional[str] = None  # Usuario que registró el comprobante
    pagada_en: Optional[str] = None
    
    created_at: Optional[str] = field(default_factory=lambda: datetime.now().isoformat())
    created_by: Optional[str] = None
    updated_at: Optional[str] = None
    updated_by: Optional[str] = None
    
    def __post_init__(self):
        """Validaciones de reglas de negocio"""
        if self.estado_liquidacion not in ['En Proceso', 'Aprobada', 'Pagada', 'Cancelada']:
            raise ValueError(f"Estado de liquidación inválido: {self.estado_liquidacion}")
        
        # Validar formato de período (YYYY-MM)
        if len(self.periodo) != 7 or self.periodo[4] != '-':
            raise ValueError(f"Formato de período inválido: {self.periodo}. Use YYYY-MM")
    
    def calcular_totales(self):
        """Calcula automáticamente los totales y el neto a pagar"""
        self.total_ingresos = self.canon_bruto + self.otros_ingresos
        
        self.total_egresos = (
            self.comision_monto +
            self.iva_comision +
            self.impuesto_4x1000 +
            self.gastos_administracion +
            self.gastos_servicios +
            self.gastos_reparaciones +
            self.otros_egresos
        )
        
        self.neto_a_pagar = self.total_ingresos - self.total_egresos
    
    @property
    def esta_en_proceso(self) -> bool:
        """Verifica si la liquidación está siendo editada"""
        return self.estado_liquidacion == "En Proceso"
    
    @property
    def esta_aprobada(self) -> bool:
        """Verifica si la liquidación fue aprobada y está lista para pago"""
        return self.estado_liquidacion == "Aprobada"
    
    @property
    def esta_pagada(self) -> bool:
        """Verifica si la liquidación ya fue pagada al propietario"""
        return self.estado_liquidacion == "Pagada"
    
    @property
    def esta_cancelada(self) -> bool:
        """Verifica si la liquidación fue anulada"""
        return self.estado_liquidacion == "Cancelada"
