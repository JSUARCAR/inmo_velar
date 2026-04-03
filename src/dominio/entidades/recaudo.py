"""
Entidad de Dominio: Recaudo
Representa un pago recibido del inquilino a la inmobiliaria.
Un recaudo puede cubrir múltiples conceptos (Canon, Administración, Mora, etc.)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from src.dominio.constantes.recaudo import MetodoPago, EstadoRecaudo
from src.dominio.value_objects.audit_info import AuditInfo


@dataclass
class Recaudo:
    """
    Entidad que representa un pago recibido del inquilino.

    Business Rules:
    - Valor total debe ser > 0
    - Referencia bancaria es obligatoria para métodos electrónicos
    - NO se permiten pagos parciales (debe cubrir el monto completo del concepto)
    - SÍ se permiten pagos anticipados (múltiples meses)
    """

    # Identificación
    id_recaudo: Optional[int] = None
    id_contrato_a: int = 0  # FK a CONTRATOS_ARRENDAMIENTOS

    # Detalles del Pago
    fecha_pago: str = ""  # Fecha en que se recibió el dinero (YYYY-MM-DD)
    valor_total: int = 0  # Monto total recibido en pesos colombianos
    metodo_pago: MetodoPago = MetodoPago.EFECTIVO
    referencia_bancaria: Optional[str] = None  # Obligatoria si metodo_pago != Efectivo

    # Estado
    estado_recaudo: EstadoRecaudo = EstadoRecaudo.PENDIENTE

    # Observaciones
    observaciones: Optional[str] = None

    # Auditoría
    created_at: Optional[str] = field(
        default_factory=lambda: datetime.now().isoformat()
    )
    created_by: Optional[str] = None
    updated_at: Optional[str] = None
    updated_by: Optional[str] = None

    def __post_init__(self) -> None:
        """Validaciones de reglas de negocio."""
        # Normalizar string → Enum si viene de la BD
        if isinstance(self.metodo_pago, str):
            self.metodo_pago = MetodoPago(self.metodo_pago)

        if isinstance(self.estado_recaudo, str):
            self.estado_recaudo = EstadoRecaudo(self.estado_recaudo)

        if self.valor_total <= 0:
            raise ValueError("El valor del recaudo debe ser mayor a cero")

        if MetodoPago.requiere_referencia(self.metodo_pago) and not self.referencia_bancaria:
            raise ValueError(
                "La referencia bancaria es obligatoria para pagos electrónicos"
            )

    @property
    def esta_aplicado(self) -> bool:
        """Verifica si el recaudo ya fue aplicado a la cuenta del inquilino."""
        return self.estado_recaudo == EstadoRecaudo.APLICADO

    @property
    def esta_reversado(self) -> bool:
        """Verifica si el recaudo fue anulado."""
        return self.estado_recaudo == EstadoRecaudo.REVERSADO

    def cambiar_estado(self, nuevo_estado: EstadoRecaudo, usuario: str) -> "Recaudo":
        """
        Crea una nueva instancia con el estado cambiado.

        Args:
            nuevo_estado: Estado destino del recaudo
            usuario: Usuario que realiza la operación

        Returns:
            Nueva instancia de Recaudo con el estado actualizado

        Raises:
            ValueError: Si la transición de estado no es válida
        """
        if nuevo_estado == EstadoRecaudo.APLICADO and not self.estado_recaudo.puede_aplicarse():
            raise ValueError(
                f"Solo se pueden aplicar pagos en estado Pendiente. "
                f"Estado actual: {self.estado_recaudo.value}"
            )

        if nuevo_estado == EstadoRecaudo.REVERSADO and not self.estado_recaudo.puede_reversarse():
            raise ValueError(
                f"Solo se pueden reversar pagos en estado Aplicado. "
                f"Estado actual: {self.estado_recaudo.value}"
            )

        return Recaudo(
            id_recaudo=self.id_recaudo,
            id_contrato_a=self.id_contrato_a,
            fecha_pago=self.fecha_pago,
            valor_total=self.valor_total,
            metodo_pago=self.metodo_pago,
            referencia_bancaria=self.referencia_bancaria,
            estado_recaudo=nuevo_estado,
            observaciones=self.observaciones,
            created_at=self.created_at,
            created_by=self.created_by,
            updated_at=datetime.now().isoformat(),
            updated_by=usuario,
        )
