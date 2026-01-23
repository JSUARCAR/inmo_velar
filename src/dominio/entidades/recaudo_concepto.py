"""
Entidad de Dominio: Recaudo Concepto
Representa el desglose de conceptos incluidos en un recaudo.
Permite que un solo pago cubra Canon + Administración + Mora.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class RecaudoConcepto:
    """
    Desglose de conceptos pagados en un recaudo.
    
    Business Rules:
    - La suma de valores de todos los conceptos debe igualar el valor_total del Recaudo
    - Período debe estar en formato YYYY-MM
    - Valor debe ser > 0
    """
    
    # Identificación
    id_recaudo_concepto: Optional[int] = None
    id_recaudo: int = 0  # FK a RECAUDOS
    
    # Detalles del Concepto
    tipo_concepto: str = ""  # 'Canon', 'Administración', 'Mora', 'Servicios', 'Otro'
    periodo: str = ""  # Formato 'YYYY-MM' (ej: '2024-10' para indicar qué mes se está pagando)
    valor: int = 0  # Cuánto de este pago fue para este concepto
    
    # Auditoría
    created_at: Optional[str] = field(default_factory=lambda: datetime.now().isoformat())
    
    def __post_init__(self):
        """Validaciones de reglas de negocio"""
        if self.valor <= 0:
            raise ValueError("El valor del concepto debe ser mayor a cero")
        
        if self.tipo_concepto not in ['Canon', 'Administración', 'Mora', 'Servicios', 'Otro']:
            raise ValueError(f"Tipo de concepto inválido: {self.tipo_concepto}")
        
        # Validar formato de período (YYYY-MM)
        if len(self.periodo) != 7 or self.periodo[4] != '-':
            raise ValueError(f"Formato de período inválido: {self.periodo}. Use YYYY-MM")
