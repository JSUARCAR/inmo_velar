from typing import Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class BonificacionAsesor:
    """Entidad que representa una bonificación/ingreso adicional para un asesor."""
    id_bonificacion_asesor: Optional[int] = None
    id_liquidacion_asesor: Optional[int] = None
    tipo_bonificacion: str = ""
    descripcion_bonificacion: str = ""
    valor_bonificacion: int = 0
    fecha_registro: Optional[str] = None
    created_by: Optional[str] = None
