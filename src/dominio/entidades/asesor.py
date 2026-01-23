"""
Entidad: Asesor

Mapeo exacto de la tabla ASESORES.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

@dataclass
class Asesor:
    """
    Entidad: Asesor
    Tabla: ASESORES
    
    Columnas:
    - ID_ASESOR (PK)
    - ID_PERSONA (FK)
    - ID_USUARIO (FK opcional?)
    - COMISION_PORCENTAJE_ARRIENDO
    - COMISION_PORCENTAJE_VENTA
    - FECHA_INGRESO
    - ESTADO
    - MOTIVO_INACTIVACION
    - Audit columns
    
    Eliminados:
    - zona_asignada, meta_mensual, etc.
    """
    
    id_asesor: Optional[int] = None
    id_persona: int = 0
    id_usuario: Optional[int] = None
    
    comision_porcentaje_arriendo: int = 0
    comision_porcentaje_venta: int = 0
    
    fecha_ingreso: Optional[str] = None
    estado: Optional[bool] = True
    motivo_inactivacion: Optional[str] = None
    
    created_at: Optional[str] = field(default_factory=lambda: datetime.now().isoformat())
    created_by: Optional[str] = None
    updated_at: Optional[str] = None
    updated_by: Optional[str] = None
