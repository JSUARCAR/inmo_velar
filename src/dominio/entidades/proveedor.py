from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class Proveedor:
    id_proveedor: Optional[int] = None
    id_persona: int = 0  # FK a Personas
    especialidad: str = "Otros"
    calificacion: float = 5.0
    observaciones: Optional[str] = None
    estado_registro: int = 1
    created_at: datetime = field(default_factory=datetime.now)
    created_by: Optional[str] = None
    
    # Propiedades de negocio
    nombre_completo: Optional[str] = None  # Se llenará al consultar con join
    contacto: Optional[str] = None # Se llenará al consultar con join
