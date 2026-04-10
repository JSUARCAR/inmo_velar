"""
Entidad: AsistenciaAsambleas

Mapeo de la tabla ASAMBLEAS.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class AsistenciaAsambleas:
    """
    Entidad: AsistenciaAsambleas
    Tabla: ASAMBLEAS

    Columnas:
    - ID_ASISTENCIA (PK)
    - ID_PROPIEDAD (FK)
    - FECHA_ASISTENCIA
    - HORA_ASISTENCIA
    - TIPO_REUNION (Ordinaria|Extraordinaria|SegundaConvocatoria)
    - TIPO_ASISTENTE (Propietario|Inmobiliaria)
    - COSTO_ASISTENTE
    - ID_ASISTENTE_PERSONA (FK)
    - DIRECCION_ASISTENCIA
    - ESTADO_ASISTENCIA (Programada|Realizada|Cancelada)
    - CREATED_AT
    - UPDATED_AT
    """

    id_asistencia: Optional[int] = None
    id_propiedad: int = 0
    fecha_asistencia: str = ""
    hora_asistencia: str = ""
    tipo_reunion: str = "Ordinaria"
    tipo_asistente: str = "Propietario"
    costo_asistente: Decimal = Decimal("0")
    id_asistente_persona: Optional[int] = None
    direccion_asistencia: str = ""
    estado_asistencia: str = "Programada"
    created_at: Optional[str] = field(
        default_factory=lambda: datetime.now().isoformat()
    )
    updated_at: Optional[str] = None

    @property
    def es_programada(self) -> bool:
        return self.estado_asistencia == "Programada"

    @property
    def es_realizada(self) -> bool:
        return self.estado_asistencia == "Realizada"

    @property
    def es_cancelada(self) -> bool:
        return self.estado_asistencia == "Cancelada"

    @property
    def es_ordinaria(self) -> bool:
        return self.tipo_reunion == "Ordinaria"

    @property
    def es_extraordinaria(self) -> bool:
        return self.tipo_reunion == "Extraordinaria"

    @property
    def es_segunda_convocatoria(self) -> bool:
        return self.tipo_reunion == "SegundaConvocatoria"

    @property
    def es_propietario(self) -> bool:
        return self.tipo_asistente == "Propietario"

    @property
    def es_inmobiliaria(self) -> bool:
        return self.tipo_asistente == "Inmobiliaria"
