"""
Entidad IncidenteLiquidacion - Relación entre incidentes y liquidaciones.

Feature: 003-integracion-incidentes-liquidaciones
Date: 2026-06-30
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class IncidenteLiquidacion:
    """
    Entidad que representa la relación entre un incidente y una liquidación.

    Attributes:
        id_relacion: Identificador único de la relación
        id_incidente: Referencia al incidente
        id_liquidacion: Referencia a la liquidación
        numero_cuota: Cuota del incidente asociada
        valor_descuento: Valor del descuento
        asociado_por: Usuario que asoció
        fecha_asociacion: Fecha de asociación
    """

    id_relacion: Optional[int] = None
    id_incidente: int = 0
    id_liquidacion: int = 0
    numero_cuota: int = 0
    valor_descuento: int = 0
    asociado_por: str = ""
    fecha_asociacion: Optional[str] = None

    def __post_init__(self):
        """Validaciones post inicialización."""
        self._validar_valor_descuento()

    def _validar_valor_descuento(self):
        """Valida que el valor del descuento sea mayor a 0."""
        if self.valor_descuento <= 0:
            raise ValueError("El valor del descuento debe ser mayor a 0")

    @classmethod
    def crear(
        cls,
        id_incidente: int,
        id_liquidacion: int,
        numero_cuota: int,
        valor_descuento: int,
        asociado_por: str,
    ) -> "IncidenteLiquidacion":
        """
        Factory method para crear una nueva relación.

        Args:
            id_incidente: ID del incidente
            id_liquidacion: ID de la liquidación
            numero_cuota: Número de cuota
            valor_descuento: Valor del descuento
            asociado_por: Usuario que asocia

        Returns:
            Nueva instancia de IncidenteLiquidacion
        """
        return cls(
            id_incidente=id_incidente,
            id_liquidacion=id_liquidacion,
            numero_cuota=numero_cuota,
            valor_descuento=valor_descuento,
            asociado_por=asociado_por,
            fecha_asociacion=datetime.now().isoformat(),
        )

    def to_dict(self) -> dict:
        """Convierte la entidad a diccionario."""
        return {
            "id_relacion": self.id_relacion,
            "id_incidente": self.id_incidente,
            "id_liquidacion": self.id_liquidacion,
            "numero_cuota": self.numero_cuota,
            "valor_descuento": self.valor_descuento,
            "asociado_por": self.asociado_por,
            "fecha_asociacion": self.fecha_asociacion,
        }
