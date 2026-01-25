"""
Entidad de Dominio: Contrato de Mandato
Representa el acuerdo entre Propietario y la Inmobiliaria para administrar una propiedad.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class ContratoMandato:
    """
    Entidad que representa un Contrato de Mandato (Administración).

    Business Rules:
    - Solo puede haber 1 contrato de mandato activo por propiedad
    - El canon debe estar entre 70.000.000 y 200.000.000
    - La comisión no puede superar el 100% (10000 = 100.00%)
    """

    # Identificadores
    id_contrato_m: Optional[int] = None
    id_propiedad: int = 0
    id_propietario: int = 0
    id_asesor: int = 0

    # Fechas
    fecha_inicio_contrato_m: str = ""  # ISO format: YYYY-MM-DD
    fecha_fin_contrato_m: str = ""
    duracion_contrato_m: int = 0  # Meses

    # Condiciones Económicas
    canon_mandato: int = 0  # Valor estimado de arriendo
    comision_porcentaje_contrato_m: int = 0  # Base 10000 (ej: 800 = 8%)
    iva_contrato_m: int = 1900  # Base 10000 (1900 = 19%)

    # Estado
    estado_contrato_m: str = "Activo"  # Activo, Finalizado, Cancelado
    motivo_cancelacion: Optional[str] = None

    # Alertas
    alerta_vencimiento_contrato_m: bool = True  # True = Activa, False = Inactiva
    fecha_renovacion_contrato_m: Optional[str] = None

    # Auditoría
    created_at: Optional[str] = field(default_factory=lambda: datetime.now().isoformat())
    created_by: Optional[str] = None
    updated_at: Optional[str] = None
    updated_by: Optional[str] = None

    @property
    def esta_activo(self) -> bool:
        """Indica si el contrato está activo."""
        return self.estado_contrato_m == "Activo"

    @property
    def comision_porcentaje_decimal(self) -> float:
        """Retorna la comisión en formato decimal (ej: 8.5%)."""
        return self.comision_porcentaje_contrato_m / 100.0

    @property
    def iva_porcentaje_decimal(self) -> float:
        """Retorna el IVA en formato decimal (ej: 19%)."""
        return self.iva_contrato_m / 100.0
