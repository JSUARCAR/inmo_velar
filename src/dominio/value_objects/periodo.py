"""
Value Object: Periodo
Representa un período contable en formato YYYY-MM.
Inmutable y con validación estricta.
"""
from dataclasses import dataclass
from datetime import date
from typing import Final


@dataclass(frozen=True)
class Periodo:
    """
    Período inmutable en formato YYYY-MM.

    Attributes:
        valor: String en formato 'YYYY-MM' (ej: '2026-04')

    Raises:
        ValueError: Si el formato es inválido o la fecha no existe
    """
    valor: str

    def __post_init__(self) -> None:
        """Validaciones de formato y rango."""
        if len(self.valor) != 7 or self.valor[4] != "-":
            raise ValueError(
                f"Formato de período inválido: {self.valor}. Use YYYY-MM"
            )
        try:
            año = int(self.valor[:4])
            mes = int(self.valor[5:])
            if not (1900 <= año <= 2100 and 1 <= mes <= 12):
                raise ValueError(f"Fecha fuera de rango: {self.valor}")
        except ValueError as e:
            raise ValueError(f"Período inválido: {self.valor}") from e

    @classmethod
    def actual(cls) -> "Periodo":
        """Crea un Periodo con el mes y año actuales."""
        hoy = date.today()
        return cls(f"{hoy.year}-{hoy.month:02d}")

    @classmethod
    def desde_fecha(cls, fecha: date) -> "Periodo":
        """Crea un Periodo a partir de una fecha."""
        return cls(f"{fecha.year}-{fecha.month:02d}")

    @property
    def año(self) -> int:
        """Retorna el año del período."""
        return int(self.valor[:4])

    @property
    def mes(self) -> int:
        """Retorna el mes del período."""
        return int(self.valor[5:])

    def __str__(self) -> str:
        return self.valor

    def __repr__(self) -> str:
        return f"Periodo('{self.valor}')"
