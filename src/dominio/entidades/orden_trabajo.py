from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class OrdenTrabajo:
    id_orden: Optional[int] = None
    id_incidente: int = 0
    id_proveedor: int = 0
    fecha_creacion: datetime = field(default_factory=datetime.now)
    fecha_inicio_estimada: Optional[datetime] = None
    fecha_fin_estimada: Optional[datetime] = None
    estado: str = "Pendiente"  # Pendiente, En Progreso, Completada, Cancelada
    costo_mano_obra: int = 0
    costo_materiales: int = 0
    descripcion_trabajo: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
