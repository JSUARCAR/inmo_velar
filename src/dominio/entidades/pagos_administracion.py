"""
Entidad: PagosAdministracion

Mapeo de la tabla PAGOS_ADMINISTRACION.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class PagosAdministracion:
    """
    Entidad: PagosAdministracion
    Tabla: PAGOS_ADMINISTRACION

    Columnas:
    - ID_PAGO_ADMIN (PK)
    - ID_PROPIEDAD (FK)
    - NOMBRE_PROPIETARIO (denormalizado)
    - DIRECCION_PROPIEDAD (denormalizado)
    - VALOR_ADMINISTRACION
    - FECHA_PAGO (día del mes 1-28)
    - LINK_PAGO (URL externa)
    - PERIODO_PAGO (YYYY-MM)
    - ESTADO_PAGO (Pendiente|Pagado|Vencido)
    - FECHA_GENERACION
    - FECHA_PAGO_REAL
    """

    id_pago_admin: Optional[int] = None
    id_propiedad: int = 0
    nombre_propietario: str = ""
    direccion_propiedad: str = ""
    valor_administracion: Decimal = Decimal("0")
    fecha_pago: int = 1
    link_pago: Optional[str] = None
    periodo_pago: str = ""
    estado_pago: str = "Pendiente"
    created_at: Optional[str] = field(
        default_factory=lambda: datetime.now().isoformat()
    )
    fecha_pago_real: Optional[str] = None

    @property
    def esta_pendiente(self) -> bool:
        return self.estado_pago == "Pendiente"

    @property
    def esta_pagado(self) -> bool:
        return self.estado_pago == "Pagado"

    @property
    def esta_vencido(self) -> bool:
        return self.estado_pago == "Vencido"

    @property
    def monto_formateado(self) -> str:
        return f"${self.valor_administracion:,.0f}"

    @property
    def periodo_formateado(self) -> str:
        return self.periodo_pago
