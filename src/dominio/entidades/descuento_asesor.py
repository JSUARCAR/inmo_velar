"""
Entidad de Dominio: DescuentoAsesor
Representa un descuento aplicado a una liquidación de asesor.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class DescuentoAsesor:
    """
    Entidad que representa un descuento aplicado a una liquidación de asesor.

    Business Rules:
    - valor_descuento debe ser >= 0
    - tipo_descuento debe estar en los tipos permitidos
    - Tipos: Préstamo, Anticipo, Sanción, Ajuste, Otros
    """

    # Identificación
    id_descuento_asesor: Optional[int] = None
    id_liquidacion_asesor: int = 0  # FK a LIQUIDACIONES_ASESORES

    # Detalles del Descuento
    tipo_descuento: str = ""  # Préstamo, Anticipo, Sanción, Ajuste, Otros
    descripcion_descuento: str = ""
    valor_descuento: int = 0

    # Fechas
    fecha_registro: Optional[str] = None

    # Auditoría
    created_at: Optional[str] = field(default_factory=lambda: datetime.now().isoformat())
    created_by: Optional[str] = None

    # Tipos que realmente existen en la base de datos
    # Consultados desde DESCUENTOS_ASESORES el 2026-01-17
    TIPOS_DESCUENTO = ["Debug", "Otros", "Préstamo"]

    def __post_init__(self):
        """Validaciones de reglas de negocio"""
        if self.valor_descuento < 0:
            raise ValueError("El valor del descuento debe ser mayor o igual a cero")

        if self.tipo_descuento and self.tipo_descuento not in self.TIPOS_DESCUENTO:
            raise ValueError(
                f"Tipo de descuento inválido: {self.tipo_descuento}. "
                f"Debe ser uno de: {', '.join(self.TIPOS_DESCUENTO)}"
            )

        if not self.descripcion_descuento or self.descripcion_descuento.strip() == "":
            raise ValueError("La descripción del descuento es obligatoria")

    @property
    def es_prestamo(self) -> bool:
        """Verifica si el descuento es un préstamo"""
        return self.tipo_descuento == "Préstamo"

    @property
    def es_anticipo(self) -> bool:
        """Verifica si el descuento es un anticipo"""
        return self.tipo_descuento == "Anticipo"

    @property
    def es_sancion(self) -> bool:
        """Verifica si el descuento es una sanción"""
        return self.tipo_descuento == "Sanción"
