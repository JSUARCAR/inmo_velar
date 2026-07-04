"""
Entidad CuotaIncidente - Representa una cuota individual del plan de pago.

Feature: 003-integracion-incidentes-liquidaciones
Date: 2026-06-30
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class CuotaIncidente:
    """
    Entidad que representa una cuota individual del plan de pago.

    Attributes:
        id_cuota: Identificador único de la cuota
        id_plan_pago: Referencia al plan de pago
        numero_cuota: Número de la cuota (1, 2, 3...)
        valor_cuota: Valor de esta cuota
        id_liquidacion: Liquidación asociada (NULL = pendiente)
        estado_pago: Estado de la cuota (Pendiente, Asociada, Pagada)
        created_at: Fecha de creación
    """

    id_cuota: Optional[int] = None
    id_plan_pago: int = 0
    numero_cuota: int = 0
    valor_cuota: int = 0
    id_liquidacion: Optional[int] = None
    estado_pago: str = "Pendiente"
    created_at: Optional[str] = None

    def __post_init__(self):
        """Validaciones post inicialización."""
        self._validar_numero_cuota()
        self._validar_valor_cuota()

    def _validar_numero_cuota(self):
        """Valida que el número de cuota sea mayor a 0."""
        if self.numero_cuota < 1:
            raise ValueError("El número de cuota debe ser mayor a 0")

    def _validar_valor_cuota(self):
        """Valida que el valor de la cuota sea mayor a 0."""
        if self.valor_cuota <= 0:
            raise ValueError("El valor de la cuota debe ser mayor a 0")

    @classmethod
    def crear(
        cls, id_plan_pago: int, numero_cuota: int, valor_cuota: int
    ) -> "CuotaIncidente":
        """
        Factory method para crear una nueva cuota.

        Args:
            id_plan_pago: ID del plan de pago
            numero_cuota: Número de la cuota
            valor_cuota: Valor de la cuota

        Returns:
            Nueva instancia de CuotaIncidente
        """
        return cls(
            id_plan_pago=id_plan_pago,
            numero_cuota=numero_cuota,
            valor_cuota=valor_cuota,
            estado_pago="Pendiente",
            created_at=datetime.now().isoformat(),
        )

    def esta_pendiente(self) -> bool:
        """Verifica si la cuota está pendiente."""
        return self.estado_pago == "Pendiente"

    def esta_asociada(self) -> bool:
        """Verifica si la cuota está asociada a una liquidación."""
        return self.estado_pago == "Asociada"

    def esta_pagada(self) -> bool:
        """Verifica si la cuota está pagada."""
        return self.estado_pago == "Pagada"

    def puede_asociarse(self) -> bool:
        """Verifica si la cuota puede asociarse a una liquidación."""
        return self.esta_pendiente()

    def puede_desasociarse(self) -> bool:
        """Verifica si la cuota puede desasociarse de una liquidación."""
        return self.esta_asociada()

    def asociar_a_liquidacion(self, id_liquidacion: int) -> None:
        """
        Asocia la cuota a una liquidación.

        Args:
            id_liquidacion: ID de la liquidación
        """
        if not self.puede_asociarse():
            raise ValueError(
                "La cuota no puede asociarse (estado actual: {self.estado_pago})"
            )
        self.id_liquidacion = id_liquidacion
        self.estado_pago = "Asociada"

    def desasociar_de_liquidacion(self) -> None:
        """Desasocia la cuota de la liquidación."""
        if not self.puede_desasociarse():
            raise ValueError(
                "La cuota no puede desasociarse (estado actual: {self.estado_pago})"
            )
        self.id_liquidacion = None
        self.estado_pago = "Pendiente"

    def marcar_como_pagada(self) -> None:
        """Marca la cuota como pagada."""
        if not self.esta_asociada():
            raise ValueError("Solo se pueden marcar como pagadas las cuotas asociadas")
        self.estado_pago = "Pagada"

    def revertir_pago(self) -> None:
        """Revierte el estado de pago de la cuota."""
        if not self.esta_pagada():
            raise ValueError("Solo se pueden revertir cuotas pagadas")
        self.estado_pago = "Asociada"

    def to_dict(self) -> dict:
        """Convierte la entidad a diccionario."""
        return {
            "id_cuota": self.id_cuota,
            "id_plan_pago": self.id_plan_pago,
            "numero_cuota": self.numero_cuota,
            "valor_cuota": self.valor_cuota,
            "id_liquidacion": self.id_liquidacion,
            "estado_pago": self.estado_pago,
            "created_at": self.created_at,
        }
