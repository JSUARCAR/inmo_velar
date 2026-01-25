"""
Entidad: Arrendatario

Mapeo exacto de la tabla ARRENDATARIOS.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Arrendatario:
    """
    Entidad: Arrendatario
    Tabla: ARRENDATARIOS

    Columnas:
    - ID_ARRENDATARIO
    - ID_PERSONA
    - ID_SEGURO (FK)
    - CODIGO_APROBACION_SEGURO
    - DIRECCION_REFERENCIA
    - ESTADO_ARRENDATARIO
    - FECHA_INGRESO_ARRENDATARIO
    - MOTIVO_INACTIVACION
    - Audit

    Eliminados:
    - scoring, ingresos, etc. (Todo eso no estaba en el esquema)
    """

    id_arrendatario: Optional[int] = None
    id_persona: int = 0
    id_seguro: Optional[int] = None

    codigo_aprobacion_seguro: Optional[str] = None
    direccion_referencia: Optional[str] = None

    estado_arrendatario: Optional[bool] = True
    fecha_ingreso_arrendatario: Optional[str] = None
    motivo_inactivacion: Optional[str] = None

    created_at: Optional[str] = field(default_factory=lambda: datetime.now().isoformat())
    created_by: Optional[str] = None
    updated_at: Optional[str] = None
    updated_by: Optional[str] = None
