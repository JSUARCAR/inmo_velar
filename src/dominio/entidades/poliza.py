"""
Entidad de Dominio: Póliza de Seguro
Representa la asignación concreta de un producto de seguro a un contrato de arrendamiento.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class PolizaSeguro:
    """
    Entidad que representa una Póliza de Seguro asignada a un contrato.
    """

    id_poliza: Optional[int]
    id_contrato: int
    id_seguro: int
    fecha_inicio: str  # ISO YYYY-MM-DD
    fecha_fin: str  # ISO YYYY-MM-DD
    numero_poliza: Optional[str]  # Identificador externo de la aseguradora
    estado: str  # 'Activa', 'Vencida', 'Cancelada'

    # Campos informativos (joins) - No persisten en tabla POLIZAS directamente, pero útiles en UI
    nombre_seguro: Optional[str] = None
    propiedad_info: Optional[str] = None
    inquilino_info: Optional[str] = None

    # Auditoría
    created_at: Optional[str] = None
    created_by: Optional[str] = None
    updated_at: Optional[str] = None
    updated_by: Optional[str] = None

    @property
    def esta_activa(self) -> bool:
        return self.estado == "Activa"
