"""
Entidad de Dominio: Recaudo
Representa un pago recibido del inquilino a la inmobiliaria.
Un recaudo puede cubrir múltiples conceptos (Canon, Administración, Mora, etc.)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


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
    metodo_pago: str = ""  # 'Efectivo', 'Transferencia', 'PSE', 'Consignación'
    referencia_bancaria: Optional[str] = None  # Obligatoria si metodo_pago != 'Efectivo'

    # Estado
    estado_recaudo: str = "Pendiente"  # 'Pendiente', 'Aplicado', 'Reversado'

    # Observaciones
    observaciones: Optional[str] = None

    # Auditoría
    created_at: Optional[str] = field(default_factory=lambda: datetime.now().isoformat())
    created_by: Optional[str] = None
    updated_at: Optional[str] = None
    updated_by: Optional[str] = None

    def __post_init__(self):
        """Validaciones de reglas de negocio"""
        if self.valor_total <= 0:
            raise ValueError("El valor del recaudo debe ser mayor a cero")

        if self.metodo_pago not in ["Efectivo", "Transferencia", "PSE", "Consignación"]:
            raise ValueError(f"Método de pago inválido: {self.metodo_pago}")

        if self.metodo_pago != "Efectivo" and not self.referencia_bancaria:
            raise ValueError("La referencia bancaria es obligatoria para pagos electrónicos")

    @property
    def esta_aplicado(self) -> bool:
        """Verifica si el recaudo ya fue aplicado a la cuenta del inquilino"""
        return self.estado_recaudo == "Aplicado"

    @property
    def esta_reversado(self) -> bool:
        """Verifica si el recaudo fue anulado"""
        return self.estado_recaudo == "Reversado"
