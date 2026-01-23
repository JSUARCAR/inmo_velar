"""
Entidad de dominio: Seguro de Arrendamiento.
Representa las pólizas de seguro disponibles para asignar a arrendatarios.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Seguro:
    """
    Entidad de dominio para Seguros de Arrendamiento.
    
    Attributes:
        id_seguro: Identificador único del seguro
        nombre_seguro: Nombre del seguro (ej: "Seguro Básico", "Seguro Plus")
        fecha_inicio_seguro: Fecha de inicio de vigencia del seguro
        porcentaje_seguro: Porcentaje del seguro en base 10000 (ej: 200 = 2%)
        estado_seguro: 1=activo, 0=inactivo
        fecha_ingreso_seguro: Fecha de registro en el sistema
        motivo_inactivacion: Razón de inactivación (si aplica)
        created_at: Timestamp de creación
        created_by: Usuario que creó el registro
        updated_at: Timestamp de última actualización
        updated_by: Usuario que actualizó el registro
    """
    id_seguro: Optional[int]
    nombre_seguro: str
    fecha_inicio_seguro: Optional[str]
    porcentaje_seguro: int  # Base 10000 (200 = 2%, 300 = 3%)
    estado_seguro: int  # 1=activo, 0=inactivo
    fecha_ingreso_seguro: Optional[str]
    motivo_inactivacion: Optional[str]
    created_at: Optional[str]
    created_by: Optional[str]
    updated_at: Optional[str]
    updated_by: Optional[str]
    
    def esta_activo(self) -> bool:
        """Verifica si el seguro está activo."""
        return self.estado_seguro == 1
    
    def obtener_porcentaje_decimal(self) -> float:
        """Retorna el porcentaje en formato decimal (ej: 2.0 para 200)."""
        return self.porcentaje_seguro / 100.0
