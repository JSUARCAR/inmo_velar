"""
Entidad: Propietario

Mapeo exacto de la tabla PROPIETARIOS.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Propietario:
    """
    Entidad: Propietario
    Tabla: PROPIETARIOS

    Columnas:
    - ID_PROPIETARIO
    - ID_PERSONA
    - BANCO_PROPIETARIO
    - NUMERO_CUENTA_PROPIETARIO
    - TIPO_CUENTA
    - OBSERVACIONES_PROPIETARIO
    - ESTADO_PROPIETARIO
    - FECHA_INGRESO_PROPIETARIO
    - MOTIVO_INACTIVACION
    - Audit
    """

    id_propietario: Optional[int] = None
    id_persona: int = 0

    banco_propietario: Optional[str] = None
    numero_cuenta_propietario: Optional[str] = None
    tipo_cuenta: Optional[str] = None

    observaciones_propietario: Optional[str] = None
    consignatario: Optional[str] = None
    documento_consignatario: Optional[str] = None
    estado_propietario: Optional[bool] = True
    fecha_ingreso_propietario: Optional[str] = None
    motivo_inactivacion: Optional[str] = None

    created_at: Optional[str] = field(default_factory=lambda: datetime.now().isoformat())
    created_by: Optional[str] = None
    updated_at: Optional[str] = None
    updated_by: Optional[str] = None
