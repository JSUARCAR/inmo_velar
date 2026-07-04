"""
Paquete de servicios de aplicacion con carga diferida (lazy loading).
Evita importaciones circulares y fallos masivos en cascada.
"""

__all__ = [
    "ServicioAutenticacion",
    "ServicioTerceros",
    "ServicioDashboard",
    "ServicioPersonas",
    "PersonaConRoles",
    "ServicioPropiedades",
    "ServicioRecibosPublicos",
    "ServicioConfiguracion",
]


def __getattr__(name):
    if name == "ServicioAutenticacion":
        from src.aplicacion.servicios.servicio_autenticacion import (
            ServicioAutenticacion,
        )

        return ServicioAutenticacion
    elif name == "ServicioTerceros":
        from src.aplicacion.servicios.servicio_terceros import ServicioTerceros

        return ServicioTerceros
    elif name == "ServicioDashboard":
        from src.aplicacion.servicios.servicio_dashboard import ServicioDashboard

        return ServicioDashboard
    elif name == "ServicioPersonas":
        from src.aplicacion.servicios.servicio_personas import ServicioPersonas

        return ServicioPersonas
    elif name == "PersonaConRoles":
        from src.aplicacion.servicios.servicio_personas import PersonaConRoles

        return PersonaConRoles
    elif name == "ServicioPropiedades":
        from src.aplicacion.servicios.servicio_propiedades import ServicioPropiedades

        return ServicioPropiedades
    elif name == "ServicioRecibosPublicos":
        from src.aplicacion.servicios.servicio_recibos_publicos import (
            ServicioRecibosPublicos,
        )

        return ServicioRecibosPublicos
    elif name == "ServicioConfiguracion":
        from src.aplicacion.servicios.servicio_configuracion import (
            ServicioConfiguracion,
        )

        return ServicioConfiguracion
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
