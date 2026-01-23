"""
Paquete de servicios de aplicacion.
"""

from src.aplicacion.servicios.servicio_autenticacion import ServicioAutenticacion
from src.aplicacion.servicios.servicio_terceros import ServicioTerceros
from src.aplicacion.servicios.servicio_dashboard import ServicioDashboard
from src.aplicacion.servicios.servicio_personas import ServicioPersonas, PersonaConRoles
from src.aplicacion.servicios.servicio_propiedades import ServicioPropiedades
from src.aplicacion.servicios.servicio_recibos_publicos import ServicioRecibosPublicos
from src.aplicacion.servicios.servicio_configuracion import ServicioConfiguracion

__all__ = [
    'ServicioAutenticacion',
    'ServicioTerceros',
    'ServicioDashboard',
    'ServicioPersonas',
    'PersonaConRoles',
    'ServicioPropiedades',
    'ServicioRecibosPublicos',
    'ServicioConfiguracion',
]

