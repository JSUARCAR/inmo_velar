"""
Entidad: Municipio

Mapeo exacto de la tabla MUNICIPIOS.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

@dataclass
class Municipio:
    """
    Entidad: Municipio
    Tabla: MUNICIPIOS
    
    Columnas:
    - ID_MUNICIPIO (PK)
    - NOMBRE_MUNICIPIO
    - DEPARTAMENTO
    - ESTADO_REGISTRO (1=Activo, 0=Inactivo)
    - CREATED_AT
    - CREATED_BY
    """
    
    # Identidad
    id_municipio: Optional[int] = None
    
    # Datos
    nombre_municipio: str = ""
    departamento: str = ""
    
    # Control
    estado_registro: Optional[int] = 1
    created_at: Optional[str] = field(default_factory=lambda: datetime.now().isoformat())
    created_by: Optional[str] = None
    
    def __post_init__(self) -> None:
        # Validaciones básicas de tipos si es necesario
        pass
        
    def nombre_completo(self) -> str:
        return f"{self.nombre_municipio} - {self.departamento}"
