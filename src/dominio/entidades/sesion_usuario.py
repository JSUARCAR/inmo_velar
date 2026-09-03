"""
Entidad: SesionUsuario

Mapeo exacto de la tabla SESIONES_USUARIO.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class SesionUsuario:
    """
    Entidad: SesionUsuario
    Tabla: SESIONES_USUARIO

    Columnas:
    - ID_SESION (PK)
    - ID_USUARIO
    - FECHA_INICIO
    - FECHA_FIN
    - TOKEN_SESION

    Atributos eliminados (Fantasmas):
    - ip_origen
    - user_agent
    - expira_en
    - activa (calculado, no almacenado)
    """

    id_sesion: Optional[int] = None
    id_usuario: int = 0

    fecha_inicio: Optional[str] = None
    fecha_fin: Optional[str] = None
    token_sesion: Optional[str] = None

    def esta_activa(self) -> bool:
        """Determina si la sesión está activa validando la expiración absoluta de fecha_fin."""
        if not self.fecha_fin:
            return False
        try:
            from datetime import datetime
            return datetime.fromisoformat(self.fecha_fin) > datetime.now()
        except ValueError:
            return False
