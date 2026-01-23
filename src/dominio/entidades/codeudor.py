"""
Entidad: Codeudor

Mapeo exacto de la tabla CODEUDORES.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

@dataclass
class Codeudor:
    """
    Entidad: Codeudor
    Tabla: CODEUDORES
    
    Columnas:
    - ID_CODEUDOR
    - ID_PERSONA
    - FECHA_INGRESO_CODEUDOR
    - ESTADO_REGISTRO
    - MOTIVO_INACTIVACION
    - CREATED_AT, CREATED_BY
    
    Nota: La tabla CODEUDORES es muy simple, solo vincula Persona como codeudor.
    No tiene FK a Contrato aquí, probablemente esté en la tabla de Contratos.
    (Verifiqué CONTRATOS_ARRENDAMIENTOS y sí tiene ID_CODEUDOR).
    """
    
    id_codeudor: Optional[int] = None
    id_persona: int = 0
    
    fecha_ingreso_codeudor: Optional[str] = None
    estado_registro: Optional[bool] = True
    motivo_inactivacion: Optional[str] = None
    
    created_at: Optional[str] = field(default_factory=lambda: datetime.now().isoformat())
    created_by: Optional[str] = None
