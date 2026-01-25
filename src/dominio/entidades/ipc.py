"""
Entidad: IPC

Mapeo exacto de la tabla IPC.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class IPC:
    """
    Entidad: IPC
    Tabla: IPC

    Columnas:
    - ID_IPC (PK)
    - ANIO (INTEGER)
    - VALOR_IPC (INTEGER/REAL?) -> En esquema dice INTEGER pero debería ser REAL.
      Nota: Si el esquema dice INTEGER para un porcentaje, puede estar escalado (x100).
      Sin embargo, asumo que puede haber error en definición SQL o es 13 en lugar de 13.5.
      Mapearemos tal cual.
    - FECHA_PUBLICACION (TEXT)
    - ESTADO_REGISTRO
    - CREATED_AT
    - CREATED_BY
    """

    id_ipc: Optional[int] = None

    anio: int = 0
    valor_ipc: float = 0.0  # Mapeo a REAL/DECIMAL para soportar porcentajes con decimales
    fecha_publicacion: Optional[str] = None

    estado_registro: Optional[bool] = True
    created_at: Optional[str] = field(default_factory=lambda: datetime.now().isoformat())
    created_by: Optional[str] = None

    def valor_decimal(self) -> Decimal:
        """Helper para obtener valor como decimal si está guardado como entero (ej. 13 -> 0.13)"""
        # Suponiendo que el entero es el porcentaje (13 = 13%)
        return Decimal(self.valor_ipc) / Decimal("100")
