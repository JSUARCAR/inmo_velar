"""
Entidad PlanPagoIncidente - Define el plan de pago para un incidente.

Feature: 003-integracion-incidentes-liquidaciones
Date: 2026-06-30
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class PlanPagoIncidente:
    """
    Entidad que representa un plan de pago para un incidente.

    Attributes:
        id_plan_pago: Identificador único del plan
        id_incidente: Referencia al incidente
        num_cuotas: Número de cuotas del plan
        valor_cuota: Valor de cada cuota
        total_plan: Valor total del plan (num_cuotas * valor_cuota)
        estado: Estado del plan (Activo, Completado, Cancelado)
        creado_por: Usuario que creó el plan
        created_at: Fecha de creación
        updated_at: Última actualización
    """

    id_plan_pago: Optional[int] = None
    id_incidente: int = 0
    num_cuotas: int = 0
    valor_cuota: int = 0
    total_plan: int = 0
    estado: str = "Activo"
    creado_por: str = ""
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def __post_init__(self):
        """Validaciones post inicialización."""
        self._validar_num_cuotas()
        self._validar_valor_cuota()
        self._calcular_total()

    def _validar_num_cuotas(self):
        """Valida que el número de cuotas sea mayor a 0."""
        if self.num_cuotas < 1:
            raise ValueError("El número de cuotas debe ser mayor a 0")

    def _validar_valor_cuota(self):
        """Valida que el valor de la cuota sea mayor a 0."""
        if self.valor_cuota <= 0:
            raise ValueError("El valor de la cuota debe ser mayor a 0")

    def _calcular_total(self):
        """Calcula el total del plan basado en cuotas y valor."""
        if self.num_cuotas > 0 and self.valor_cuota > 0:
            self.total_plan = self.num_cuotas * self.valor_cuota

    @classmethod
    def crear(
        cls, id_incidente: int, num_cuotas: int, valor_cuota: int, creado_por: str
    ) -> "PlanPagoIncidente":
        """
        Factory method para crear un nuevo plan de pago.

        Args:
            id_incidente: ID del incidente
            num_cuotas: Número de cuotas
            valor_cuota: Valor por cuota
            creado_por: Usuario que crea el plan

        Returns:
            Nueva instancia de PlanPagoIncidente
        """
        return cls(
            id_incidente=id_incidente,
            num_cuotas=num_cuotas,
            valor_cuota=valor_cuota,
            total_plan=num_cuotas * valor_cuota,
            estado="Activo",
            creado_por=creado_por,
            created_at=datetime.now().isoformat(),
        )

    def esta_activo(self) -> bool:
        """Verifica si el plan está activo."""
        return self.estado == "Activo"

    def puede_modificarse(self) -> bool:
        """
        Verifica si el plan puede modificarse.
        Solo se puede modificar si está activo.
        """
        return self.esta_activo()

    def cancelar(self) -> None:
        """Cancela el plan de pago."""
        if not self.puede_modificarse():
            raise ValueError("El plan no puede ser cancelado")
        self.estado = "Cancelado"
        self.updated_at = datetime.now().isoformat()

    def completar(self) -> None:
        """Marca el plan como completado."""
        if not self.esta_activo():
            raise ValueError("Solo se pueden completar planes activos")
        self.estado = "Completado"
        self.updated_at = datetime.now().isoformat()

    def to_dict(self) -> dict:
        """Convierte la entidad a diccionario."""
        return {
            "id_plan_pago": self.id_plan_pago,
            "id_incidente": self.id_incidente,
            "num_cuotas": self.num_cuotas,
            "valor_cuota": self.valor_cuota,
            "total_plan": self.total_plan,
            "estado": self.estado,
            "creado_por": self.creado_por,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
