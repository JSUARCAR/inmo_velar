"""
Constantes: Roles del Sistema

Define los roles de usuario en la aplicación.
"""

from enum import Enum


class RolSistema(str, Enum):
    """
    Roles de usuario para control de acceso.
    
    - ADMINISTRADOR: Acceso completo al sistema
    - COORDINADOR: Gestión de asesores y operaciones
    - ASESOR: Gestión de propiedades y contratos
    - CONTADOR: Acceso a módulos financieros
    - CONSULTA: Solo lectura
    """
    
    ADMINISTRADOR = "ADMINISTRADOR"
    COORDINADOR = "COORDINADOR"
    ASESOR = "ASESOR"
    CONTADOR = "CONTADOR"
    CONSULTA = "CONSULTA"
    
    def puede_editar(self) -> bool:
        """Retorna True si el rol puede modificar datos."""
        return self in [
            RolSistema.ADMINISTRADOR,
            RolSistema.COORDINADOR,
            RolSistema.ASESOR,
            RolSistema.CONTADOR
        ]
