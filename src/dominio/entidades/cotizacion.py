from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Cotizacion:
    id_cotizacion: Optional[int] = None
    id_incidente: int = 0
    id_proveedor: int = 0
    valor_materiales: int = 0
    valor_mano_obra: int = 0
    valor_total: int = 0
    descripcion_trabajo: Optional[str] = None
    dias_estimados: int = 1
    fecha_cotizacion: datetime = field(default_factory=datetime.now)
    estado_cotizacion: str = "Pendiente"  # Pendiente, Aprobada, Rechazada
    created_at: datetime = field(default_factory=datetime.now)
    created_by: Optional[str] = None

    # Propiedades de negocio
    nombre_proveedor: Optional[str] = None  # Se llenará al consultar

    def calcular_total(self) -> int:
        self.valor_total = self.valor_materiales + self.valor_mano_obra
        return self.valor_total
