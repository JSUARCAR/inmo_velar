"""
Entidad: Auditoría de Cambios

Registro inmutable de acciones realizadas en el sistema.
Aunque se implementa principalmente con Triggers, esta entidad permite
mapear y consultar el historial desde la aplicación.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class AuditoriaCambio:
    """
    Entidad: Registro de Auditoría

    Mapea la tabla AUDITORIA_CAMBIOS.
    """

    id_auditoria: int
    tabla: str
    id_registro: int
    accion: str
    campo: Optional[str]
    valor_anterior: Optional[str]
    valor_nuevo: Optional[str]
    usuario: str
    fecha_cambio: str  # Se recibe como string desde BD
    motivo_cambio: Optional[str]
    ip_origen: Optional[str]

    @property
    def fecha_dt(self) -> Optional[datetime]:
        """Convierte la fecha string a datetime si es posible."""
        try:
            return datetime.fromisoformat(self.fecha_cambio)
        except (ValueError, TypeError):
            return None

    def __repr__(self) -> str:
        return (
            f"Audit(id={self.id_auditoria}, accion={self.accion}, "
            f"tabla={self.tabla}, campo={self.campo})"
        )
