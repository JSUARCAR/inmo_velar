"""
Entidad: Persona

Mapeo exacto de la tabla PERSONAS.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Persona:
    """
    Entidad: Persona
    Tabla: PERSONAS

    Columnas:
    - ID_PERSONA (PK)
    - TIPO_DOCUMENTO
    - NUMERO_DOCUMENTO
    - NOMBRE_COMPLETO (Único campo de nombre)
    - TELEFONO_PRINCIPAL
    - CORREO_ELECTRONICO
    - DIRECCION_PRINCIPAL
    - ESTADO_REGISTRO
    - MOTIVO_INACTIVACION
    - CREATED_AT, CREATED_BY, UPDATED_AT, UPDATED_BY

    Atributos eliminados (Fantasmas):
    - nombre, apellidos (BD usa NOMBRE_COMPLETO)
    - fecha_nacimiento, genero (No existen en BD)
    """

    id_persona: Optional[int] = None

    tipo_documento: Optional[str] = None
    numero_documento: str = ""
    nombre_completo: str = ""

    telefono_principal: Optional[str] = None
    correo_electronico: Optional[str] = None
    direccion_principal: Optional[str] = None

    estado_registro: Optional[bool] = True
    motivo_inactivacion: Optional[str] = None

    created_at: Optional[str] = field(default_factory=lambda: datetime.now().isoformat())
    created_by: Optional[str] = None
    updated_at: Optional[str] = None
    updated_by: Optional[str] = None
