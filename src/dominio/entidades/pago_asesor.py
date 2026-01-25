"""
Entidad de Dominio: PagoAsesor
Representa un pago realizado o programado a un asesor.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class PagoAsesor:
    """
    Entidad que representa un pago a un asesor inmobiliario.

    Business Rules:
    - valor_pago debe ser > 0
    - referencia_pago debe ser única
    - Estados permitidos: Pendiente, Programado, Pagado, Rechazado, Anulado
    - Medios de pago: Transferencia, Cheque, Efectivo, PSE
    - Si estado = Rechazado, debe tener motivo_rechazo
    - Si estado = Pagado, debe tener fecha_pago y comprobante
    """

    # Identificación
    id_pago_asesor: Optional[int] = None
    id_liquidacion_asesor: int = 0  # FK a LIQUIDACIONES_ASESORES
    id_asesor: int = 0  # FK a ASESORES

    # Detalles del Pago
    valor_pago: int = 0
    fecha_pago: Optional[str] = None  # Fecha efectiva del pago
    fecha_programada: str = ""  # Fecha programada para el pago
    medio_pago: Optional[str] = None  # Transferencia, Cheque, Efectivo, PSE
    referencia_pago: Optional[str] = None  # UNIQUE

    # Estado y Control
    estado_pago: str = "Pendiente"  # Pendiente, Programado, Pagado, Rechazado, Anulado
    motivo_rechazo: Optional[str] = None
    comprobante_pago: Optional[str] = None
    observaciones_pago: Optional[str] = None
    fecha_confirmacion: Optional[str] = None

    # Auditoría
    created_at: Optional[str] = field(default_factory=lambda: datetime.now().isoformat())
    created_by: Optional[str] = None
    updated_at: Optional[str] = None
    updated_by: Optional[str] = None

    # Estados y medios permitidos
    ESTADOS_PAGO = ["Pendiente", "Programado", "Pagado", "Rechazado", "Anulado"]
    MEDIOS_PAGO = ["Transferencia", "Cheque", "Efectivo", "PSE"]

    def __post_init__(self):
        """Validaciones de reglas de negocio"""
        if self.valor_pago <= 0:
            raise ValueError("El valor del pago debe ser mayor a cero")

        if self.estado_pago not in self.ESTADOS_PAGO:
            raise ValueError(
                f"Estado de pago inválido: {self.estado_pago}. "
                f"Debe ser uno de: {', '.join(self.ESTADOS_PAGO)}"
            )

        if self.medio_pago and self.medio_pago not in self.MEDIOS_PAGO:
            raise ValueError(
                f"Medio de pago inválido: {self.medio_pago}. "
                f"Debe ser uno de: {', '.join(self.MEDIOS_PAGO)}"
            )

    # ==================== Propiedades de Negocio ====================

    @property
    def esta_pendiente(self) -> bool:
        """Verifica si el pago está pendiente"""
        return self.estado_pago == "Pendiente"

    @property
    def esta_programado(self) -> bool:
        """Verifica si el pago está programado"""
        return self.estado_pago == "Programado"

    @property
    def esta_pagado(self) -> bool:
        """Verifica si el pago fue efectuado"""
        return self.estado_pago == "Pagado"

    @property
    def esta_rechazado(self) -> bool:
        """Verifica si el pago fue rechazado"""
        return self.estado_pago == "Rechazado"

    @property
    def esta_anulado(self) -> bool:
        """Verifica si el pago fue anulado"""
        return self.estado_pago == "Anulado"

    @property
    def puede_pagarse(self) -> bool:
        """Verifica si el pago puede ser marcado como pagado"""
        return self.esta_pendiente or self.esta_programado

    @property
    def puede_rechazarse(self) -> bool:
        """Verifica si el pago puede ser rechazado"""
        return self.esta_pendiente or self.esta_programado

    @property
    def puede_anularse(self) -> bool:
        """Verifica si el pago puede ser anulado"""
        # No se puede anular un pago ya efectuado
        return not self.esta_pagado and not self.esta_anulado

    # ==================== Métodos de Acción ====================

    def programar(self, fecha_programada: str, usuario: str) -> None:
        """
        Marca el pago como programado.

        Args:
            fecha_programada: Fecha programada para el pago
            usuario: Usuario que programa

        Raises:
            ValueError: Si el pago no está pendiente
        """
        if not self.esta_pendiente:
            raise ValueError("Solo se pueden programar pagos pendientes")

        self.estado_pago = "Programado"
        self.fecha_programada = fecha_programada
        self.updated_at = datetime.now().isoformat()
        self.updated_by = usuario

    def marcar_como_pagado(self, fecha_pago: str, comprobante: str, usuario: str) -> None:
        """
        Marca el pago como efectuado.

        Args:
            fecha_pago: Fecha efectiva del pago
            comprobante: Número o referencia del comprobante
            usuario: Usuario que registra el pago

        Raises:
            ValueError: Si el pago no puede ser pagado
        """
        if not self.puede_pagarse:
            raise ValueError(f"No se puede marcar como pagado un pago en estado {self.estado_pago}")

        if not comprobante or comprobante.strip() == "":
            raise ValueError("Debe especificar un comprobante de pago")

        self.estado_pago = "Pagado"
        self.fecha_pago = fecha_pago
        self.comprobante_pago = comprobante
        self.fecha_confirmacion = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        self.updated_by = usuario

    def rechazar(self, motivo: str, usuario: str) -> None:
        """
        Rechaza el pago.

        Args:
            motivo: Motivo del rechazo
            usuario: Usuario que rechaza

        Raises:
            ValueError: Si el pago no puede ser rechazado
        """
        if not self.puede_rechazarse:
            raise ValueError(f"No se puede rechazar un pago en estado {self.estado_pago}")

        if not motivo or motivo.strip() == "":
            raise ValueError("Debe especificar un motivo para el rechazo")

        self.estado_pago = "Rechazado"
        self.motivo_rechazo = motivo
        self.updated_at = datetime.now().isoformat()
        self.updated_by = usuario

    def anular(self, usuario: str) -> None:
        """
        Anula el pago.

        Args:
            usuario: Usuario que anula

        Raises:
            ValueError: Si el pago no puede ser anulado
        """
        if not self.puede_anularse:
            raise ValueError("No se puede anular un pago ya efectuado")

        self.estado_pago = "Anulado"
        self.updated_at = datetime.now().isoformat()
        self.updated_by = usuario
