"""
Entidad de Dominio: Desocupación
Representa el proceso de terminación de un contrato de arrendamiento.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class Desocupacion:
    """
    Entidad que representa un proceso de desocupación de inmueble.
    
    Business Rules:
    - Solo puede iniciarse para contratos en estado 'Activo'
    - Requiere fecha programada de entrega
    - Al finalizar, el contrato debe cambiar a estado 'Finalizado'
    """
    
    # Identificadores
    id_desocupacion: Optional[int] = None
    id_contrato: int = 0
    
    # Fechas
    fecha_solicitud: str = field(default_factory=lambda: datetime.now().date().isoformat())
    fecha_programada: str = ""  # Fecha estimada de entrega
    fecha_real: Optional[str] = None  # Fecha real de entrega (cuando se completa)
    
    # Estado
    estado: str = "En Proceso"  # "En Proceso", "Completada", "Cancelada"
    
    # Información adicional
    observaciones: Optional[str] = None
    
    # Auditoría
    created_at: Optional[str] = field(default_factory=lambda: datetime.now().isoformat())
    created_by: Optional[str] = None
    updated_at: Optional[str] = None
    updated_by: Optional[str] = None
    
    # Helper fields (populated by joins, not stored in DB)
    direccion_propiedad: Optional[str] = None
    nombre_inquilino: Optional[str] = None
    progreso_porcentaje: int = 0  # Calculado: tareas completadas / total
    
    @property
    def esta_en_proceso(self) -> bool:
        return self.estado == "En Proceso"
    
    @property
    def esta_completada(self) -> bool:
        return self.estado == "Completada"


@dataclass
class TareaDesocupacion:
    """
    Entidad que representa una tarea individual del checklist de desocupación.
    """
    
    # Identificadores
    id_tarea: Optional[int] = None
    id_desocupacion: int = 0
    
    # Datos de la tarea
    descripcion: str = ""
    orden: int = 0  # Orden de presentación (1-8)
    completada: bool = False
    fecha_completada: Optional[str] = None
    responsable: Optional[str] = None
    observaciones: Optional[str] = None
    
    def completar(self, usuario: str, observaciones: Optional[str] = None):
        """Marca la tarea como completada."""
        self.completada = True
        self.fecha_completada = datetime.now().isoformat()
        self.responsable = usuario
        if observaciones:
            self.observaciones = observaciones
