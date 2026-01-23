"""
Entidad: Usuario

Mapeo exacto de la tabla USUARIOS.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

@dataclass
class Usuario:
    """
    Entidad: Usuario
    Tabla: USUARIOS
    
    Columnas:
    - ID_USUARIO (PK)
    - NOMBRE_USUARIO
    - CONTRASENA_HASH
    - ROL
    - ESTADO_USUARIO
    - ULTIMO_ACCESO
    - FECHA_CREACION
    - CREATED_BY
    - UPDATED_AT
    - UPDATED_BY
    
    Atributos eliminados (Fantasmas):
    - sal (no existe columna SALT)
    - email (no existe columna EMAIL)
    - id_persona (no existe FK directa en USUARIOS, la relación está en PERSONAS o ASESORES?)
      (Verifiqué PERSONAS: ID_PERSONA pk. ASESORES tiene ID_USUARIO)
    """
    
    id_usuario: Optional[int] = None
    
    nombre_usuario: str = ""
    contrasena_hash: str = ""  # Nota: Sin tilde para evitar problemas, aunque BD es CONTRASENA_HASH
    rol: str = ""
    
    estado_usuario: bool = True  # Estado activo del usuario
    ultimo_acceso: Optional[str] = None
    fecha_creacion: Optional[str] = field(default_factory=lambda: datetime.now().isoformat())
    
    created_by: Optional[str] = None
    updated_at: Optional[str] = None
    updated_by: Optional[str] = None

    def es_activo(self) -> bool:
        """Retorna True si el usuario está activo."""
        return self.estado_usuario
