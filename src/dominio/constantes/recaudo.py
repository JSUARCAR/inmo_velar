"""
Constantes y Enums del Dominio de Recaudos.
Sistema Velar - Inmobiliaria Velar SAS

Define los tipos enumerados para métodos de pago, estados de recaudo
y tipos de concepto, eliminando magic strings del código.
"""

from enum import Enum
from typing import Final


class MetodoPago(str, Enum):
    """Métodos de pago válidos para un recaudo."""

    EFECTIVO: Final = "Efectivo"
    TRANSFERENCIA: Final = "Transferencia"
    PSE: Final = "PSE"
    CONSIGNACION: Final = "Consignación"

    @classmethod
    def valores(cls) -> list[str]:
        """Retorna lista de valores string de todos los métodos."""
        return [e.value for e in cls]

    @classmethod
    def requiere_referencia(cls, metodo: "MetodoPago") -> bool:
        """Determina si el método de pago requiere referencia bancaria."""
        return metodo != cls.EFECTIVO


class EstadoRecaudo(str, Enum):
    """Estados posibles de un recaudo en su ciclo de vida."""

    PENDIENTE: Final = "Pendiente"
    APLICADO: Final = "Aplicado"
    REVERSADO: Final = "Reversado"
    VENCIDO: Final = "Vencido"

    @classmethod
    def valores(cls) -> list[str]:
        """Retorna lista de valores string de todos los estados."""
        return [e.value for e in cls]

    def puede_editarse(self) -> bool:
        """Solo los recaudos Pendientes y Vencidos pueden editarse."""
        return self in (EstadoRecaudo.PENDIENTE, EstadoRecaudo.VENCIDO)

    def puede_aplicarse(self) -> bool:
        """Solo los recaudos Pendientes y Vencidos pueden aplicarse."""
        return self in (EstadoRecaudo.PENDIENTE, EstadoRecaudo.VENCIDO)

    def puede_reversarse(self) -> bool:
        """Solo los recaudos Aplicados pueden reversarse."""
        return self == EstadoRecaudo.APLICADO

    def puede_eliminarse(self) -> bool:
        """Solo los recaudos Pendientes y Vencidos pueden eliminarse."""
        return self in (EstadoRecaudo.PENDIENTE, EstadoRecaudo.VENCIDO)

    def es_vencido(self) -> bool:
        """Indica si el recaudo está vencido."""
        return self == EstadoRecaudo.VENCIDO


class TipoConcepto(str, Enum):
    """Tipos de concepto que puede incluir un recaudo."""

    CANON: Final = "Canon"
    ADMINISTRACION: Final = "Administración"
    MORA: Final = "Mora"
    SERVICIOS: Final = "Servicios"
    OTRO: Final = "Otro"

    @classmethod
    def valores(cls) -> list[str]:
        """Retorna lista de valores string de todos los tipos."""
        return [e.value for e in cls]
