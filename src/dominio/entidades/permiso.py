"""
Entidades de dominio para el sistema de permisos.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Permiso:
    """
    Entidad: Permiso del Sistema

    Representa un permiso específico para acceder a un módulo con una acción determinada.
    """

    id_permiso: Optional[int] = None
    modulo: str = ""
    ruta: str = ""
    accion: str = ""  # VER, CREAR, EDITAR, ELIMINAR
    descripcion: Optional[str] = None
    categoria: Optional[str] = None
    created_at: Optional[str] = None

    def __str__(self) -> str:
        return f"{self.modulo} - {self.accion}"


@dataclass
class RolPermiso:
    """
    Entidad: Asignación de Permiso a Rol

    Representa la relación entre un rol y los permisos que tiene asignados.
    """

    id_rol_permiso: Optional[int] = None
    rol: str = ""
    id_permiso: int = 0
    activo: bool = True
    created_by: Optional[str] = None
    created_at: Optional[str] = None
    updated_by: Optional[str] = None
    updated_at: Optional[str] = None

    def __str__(self) -> str:
        return f"{self.rol} - Permiso ID: {self.id_permiso}"
