"""
Entidad de Dominio: Renovación de Contrato
Registra el historial de renovaciones o actualizaciones de contratos.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class RenovacionContrato:
    """
    Entidad: RenovacionContrato
    Tabla: RENOVACIONES_CONTRATOS
    """
    
    id_renovacion: Optional[int] = None
    id_contrato_m: Optional[int] = None
    id_contrato_a: Optional[int] = None
    
    tipo_contrato: str = ""  # 'Mandato', 'Arrendamiento'
    
    fecha_inicio_original: str = ""
    fecha_fin_original: str = ""
    fecha_inicio_renovacion: str = ""
    fecha_fin_renovacion: str = ""
    
    canon_anterior: int = 0
    canon_nuevo: int = 0
    porcentaje_incremento: Optional[int] = None
    motivo_renovacion: Optional[str] = None
    
    fecha_renovacion: str = field(default_factory=lambda: datetime.now().date().isoformat())
    
    created_at: Optional[str] = field(default_factory=lambda: datetime.now().isoformat())
    created_by: Optional[str] = None
