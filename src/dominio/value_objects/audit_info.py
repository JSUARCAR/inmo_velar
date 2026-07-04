"""
Value Object: AuditInfo
Información de auditoría para entidades del dominio.
Inmutable, genera nuevas instancias al actualizar.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class AuditInfo:
    """
    Información de auditoría inmutable.

    Attributes:
        created_at: Fecha de creación en formato ISO 8601
        created_by: Usuario que creó el registro
        updated_at: Fecha de última actualización (ISO 8601)
        updated_by: Usuario que realizó la última actualización
    """

    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    created_by: Optional[str] = None
    updated_at: Optional[str] = None
    updated_by: Optional[str] = None

    def con_update(self, usuario: str) -> "AuditInfo":
        """
        Crea nueva instancia con datos de actualización.

        Args:
            usuario: Nombre del usuario que realiza la actualización

        Returns:
            Nueva instancia de AuditInfo con updated_at y updated_by
        """
        return AuditInfo(
            created_at=self.created_at,
            created_by=self.created_by,
            updated_at=datetime.now().isoformat(),
            updated_by=usuario,
        )

    def __str__(self) -> str:
        return f"Creado: {self.created_at} por {self.created_by or 'Sistema'}"
