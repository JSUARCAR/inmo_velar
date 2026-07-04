"""
Value Object: EstadoCumplimiento
Representa el estado de cumplimiento de obligaciones financieras de un contrato.
Inmutable y con validación estricta.
"""

from dataclasses import dataclass
from datetime import date
from typing import Final, Optional

ESTADO_AL_DIA: Final = "AL_DIA"
ESTADO_PENDIENTE: Final = "PENDIENTE"
ESTADO_VENCIDO: Final = "VENCIDO"

ESTADOS_VALIDOS = frozenset({ESTADO_AL_DIA, ESTADO_PENDIENTE, ESTADO_VENCIDO})


@dataclass(frozen=True)
class EstadoCumplimiento:
    """
    Estado de cumplimiento financiero de un contrato.
    Se evalúa mensualmente y se reinicia automáticamente al inicio de cada período.

    States:
        - AL_DIA: Pago o recaudo registrado dentro del período corresponding
        - PENDIENTE: Sin registro de pago o recaudo en el período still evaluando
        - VENCIDO: Fecha límite superada sin registro de pago o recaudo

    Attributes:
        estado: Estado actual (AL_DIA | PENDIENTE | VENCIDO)
        tipo_contrato: Tipo de contrato (Mandato | Arrendamiento)
        id_contrato: ID del contrato
        periodo: Período evaluasii n formato YYYY-MM
        fecha_registro: Fecha del registro de pago (opcional)
        dias_vencido: Días vencidos (solo para VENCIDO)
        fecha_limite: Fecha límite para pagar (calculada)
    """

    estado: str
    tipo_contrato: str
    id_contrato: int
    periodo: str
    fecha_registro: Optional[str] = None
    dias_vencido: Optional[int] = None
    fecha_limite: Optional[str] = None

    def __post_init__(self) -> None:
        """Validaciones de invariantes."""
        if self.estado not in ESTADOS_VALIDOS:
            raise ValueError(f"Estado inválido: {self.estado}. Use: {ESTADOS_VALIDOS}")
        if self.tipo_contrato not in ("Mandato", "Arrendamiento"):
            raise ValueError(
                f"Tipo contrato inválido: {self.tipo_contrato}. Use: Mandato | Arrendamiento"
            )
        if len(self.periodo) != 7 or self.periodo[4] != "-":
            raise ValueError(
                f"Formato de período inválido: {self.periodo}. Use YYYY-MM"
            )

    @property
    def es_al_dia(self) -> bool:
        """Retorna True si el contrato está al día."""
        return self.estado == ESTADO_AL_DIA

    @property
    def es_pendiente(self) -> bool:
        """Retorna True si el pago está pendiente."""
        return self.estado == ESTADO_PENDIENTE

    @property
    def es_vencido(self) -> bool:
        """Retorna True si el pago está vencido."""
        return self.estado == ESTADO_VENCIDO

    @property
    def color(self) -> str:
        """Retorna el color del semáforo para UI."""
        return {
            ESTADO_AL_DIA: "green",
            ESTADO_PENDIENTE: "yellow",
            ESTADO_VENCIDO: "red",
        }[self.estado]

    @property
    def icono(self) -> str:
        """Retorna el ícone para UI."""
        return {
            ESTADO_AL_DIA: "check_circle",
            ESTADO_PENDIENTE: "schedule",
            ESTADO_VENCIDO: "warning",
        }[self.estado]

    @property
    def label(self) -> str:
        """Retorna label legible para UI."""
        return {
            ESTADO_AL_DIA: "Al día",
            ESTADO_PENDIENTE: "Pendiente",
            ESTADO_VENCIDO: "Vencido",
        }[self.estado]

    def __str__(self) -> str:
        return f"{self.estado} ({self.periodo})"

    def __repr__(self) -> str:
        return (
            f"EstadoCumplimiento(estado={self.estado!r}, "
            f"tipo={self.tipo_contrato!r}, id={self.id_contrato}, "
            f"periodo={self.periodo!r})"
        )


def crear_estado_al_dia(
    tipo_contrato: str,
    id_contrato: int,
    periodo: str,
    fecha_registro: Optional[str] = None,
) -> EstadoCumplimiento:
    """Factory para estado AL_DIA."""
    return EstadoCumplimiento(
        estado=ESTADO_AL_DIA,
        tipo_contrato=tipo_contrato,
        id_contrato=id_contrato,
        periodo=periodo,
        fecha_registro=fecha_registro,
    )


def crear_estado_pendiente(
    tipo_contrato: str,
    id_contrato: int,
    periodo: str,
    fecha_limite: Optional[str] = None,
) -> EstadoCumplimiento:
    """Factory para estado PENDIENTE."""
    return EstadoCumplimiento(
        estado=ESTADO_PENDIENTE,
        tipo_contrato=tipo_contrato,
        id_contrato=id_contrato,
        periodo=periodo,
        fecha_limite=fecha_limite,
    )


def crear_estado_vencido(
    tipo_contrato: str,
    id_contrato: int,
    periodo: str,
    dias_vencido: int,
    fecha_limite: Optional[str] = None,
) -> EstadoCumplimiento:
    """Factory para estado VENCIDO."""
    return EstadoCumplimiento(
        estado=ESTADO_VENCIDO,
        tipo_contrato=tipo_contrato,
        id_contrato=id_contrato,
        periodo=periodo,
        dias_vencido=dias_vencido,
        fecha_limite=fecha_limite,
    )


def obtener_periodo_actual() -> str:
    """Retorna el período actual en formato YYYY-MM."""
    hoy = date.today()
    return f"{hoy.year}-{hoy.month:02d}"
