"""
Patrón Strategy: Cálculo de Comisiones

Implementa estrategias extensibles para cálculos de comisiones.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol


@dataclass
class ContextoComision:
    """
    Datos necesarios para calcular una comisión.

    Attributes:
        monto_base: Monto sobre el cual calcular
        id_asesor: ID del asesor
        numero_meses: Duración del contrato
        es_primera_vez: Si es primer contrato del cliente
    """

    monto_base: Decimal
    id_asesor: int
    numero_meses: int = 12
    es_primera_vez: bool = False


@dataclass
class ResultadoComision:
    """
    Resultado del cálculo de comisión.

    Attributes:
        monto_comision: Monto final calculado
        porcentaje_aplicado: Porcentaje usado
        nombre_estrategia: Nombre de la estrategia
        detalles: Explicación del cálculo
    """

    monto_comision: Decimal
    porcentaje_aplicado: Decimal
    nombre_estrategia: str
    detalles: str = ""


class IEstrategiaComision(Protocol):
    """
    Protocol para estrategias de cálculo de comisión.

    Permite implementar diferentes algoritmos de cálculo
    sin modificar el código que las usa (OCP).
    """

    @property
    def nombre(self) -> str:
        """Nombre descriptivo de la estrategia."""
        ...

    def calcular(self, contexto: ContextoComision) -> ResultadoComision:
        """
        Calcula la comisión según la estrategia.

        Args:
            contexto: Datos para el cálculo

        Returns:
            Resultado con monto y detalles
        """
        ...


class EstrategiaComisionPorcentajeFijo:
    """
    Implementación: Comisión como porcentaje fijo.

    Ejemplo: Siempre 10% del monto base.
    """

    def __init__(self, porcentaje: Decimal):
        if porcentaje < 0 or porcentaje > 100:
            raise ValueError("Porcentaje debe estar entre 0 y 100")
        self._porcentaje = porcentaje

    @property
    def nombre(self) -> str:
        return f"Comisión Porcentaje Fijo ({self._porcentaje}%)"

    def calcular(self, contexto: ContextoComision) -> ResultadoComision:
        monto = (contexto.monto_base * self._porcentaje) / Decimal("100")

        return ResultadoComision(
            monto_comision=monto.quantize(Decimal("0.01")),
            porcentaje_aplicado=self._porcentaje,
            nombre_estrategia=self.nombre,
            detalles=f"Base ${contexto.monto_base} × {self._porcentaje}%",
        )
