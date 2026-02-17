"""
Entidad de Dominio: Contrato de Arrendamiento
Representa el acuerdo de alquiler entre Inmobiliaria (en nombre del Propietario) y un Arrendatario.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class ContratoArrendamiento:
    """
    Entidad que representa un Contrato de Arrendamiento.

    Business Rules:
    - Requiere un Mandato activo previo sobrea la propiedad.
    - Máximo 1 Codeudor.
    - Canon entre límites permitidos.
    """

    # Identificadores
    id_contrato_a: Optional[int] = None
    id_propiedad: int = 0
    id_arrendatario: int = 0
    id_codeudor: Optional[int] = None  # Puede ser Null

    # Fechas
    fecha_inicio_contrato_a: str = ""
    fecha_fin_contrato_a: str = ""
    duracion_contrato_a: int = 0

    # Condiciones Económicas
    canon_arrendamiento: int = 0
    deposito: int = 0
    fecha_pago: Optional[str] = None

    # Estado
    estado_contrato_a: str = "Activo"  # Activo, Finalizado, Legal, Cancelado
    motivo_cancelacion: Optional[str] = None

    # Alertas e IPC
    alerta_vencimiento_contrato_a: bool = True
    alerta_ipc: bool = True
    fecha_renovacion_contrato_a: Optional[str] = None
    fecha_incremento_ipc: Optional[str] = None
    fecha_ultimo_incremento_ipc: Optional[str] = None

    # Auditoría
    created_at: Optional[str] = field(default_factory=lambda: datetime.now().isoformat())
    created_by: Optional[str] = None
    updated_at: Optional[str] = None
    updated_by: Optional[str] = None

    @property
    def esta_activo(self) -> bool:
        return self.estado_contrato_a == "Activo"
