"""
Entidad de Dominio: Recaudo Concepto
Representa el desglose de conceptos incluidos en un recaudo.
Permite que un solo pago cubra Canon + Administración + Mora.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from src.dominio.constantes.recaudo import TipoConcepto


@dataclass
class RecaudoConcepto:
    """
    Desglose de conceptos pagados en un recaudo.

    Business Rules:
    - La suma de valores de todos los conceptos debe igualar el valor_total del Recaudo
    - Período debe estar en formato YYYY-MM
    - Valor debe ser > 0
    """

    # Identificación
    id_recaudo_concepto: Optional[int] = None
    id_recaudo: int = 0  # FK a RECAUDOS

    # Detalles del Concepto
    tipo_concepto: TipoConcepto = TipoConcepto.CANON
    periodo: str = ""  # Formato 'YYYY-MM' (ej: '2024-10')
    valor: int = 0  # Cuánto de este pago fue para este concepto

    # Auditoría
    created_at: Optional[str] = field(
        default_factory=lambda: datetime.now().isoformat()
    )

    def __post_init__(self) -> None:
        """Validaciones de reglas de negocio."""
        # Normalizar string → Enum si viene de la BD
        if isinstance(self.tipo_concepto, str):
            self.tipo_concepto = TipoConcepto(self.tipo_concepto)

        if self.valor <= 0:
            raise ValueError("El valor del concepto debe ser mayor a cero")

        # Validar formato de período (YYYY-MM)
        if len(self.periodo) != 7 or self.periodo[4] != "-":
            raise ValueError(
                f"Formato de período inválido: {self.periodo}. Use YYYY-MM"
            )
