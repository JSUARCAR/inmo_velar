"""
Excepciones específicas para el dominio de Propiedad Horizontal.
"""


class PropiedadHorizontalError(Exception):
    """Error base para el dominio de PH."""

    message: str = ""


class PropiedadSinContratoError(PropiedadHorizontalError):
    """La propiedad no tiene un contrato de mandato activo."""

    def __init__(self, id_propiedad: int):
        self.message = f"La propiedad con ID {id_propiedad} no tiene un contrato de mandato activo."
        super().__init__(self.message)


class AdministracionNoConfiguradaError(PropiedadHorizontalError):
    """La propiedad no tiene el valor de administración configurado."""

    def __init__(self, id_propiedad: int):
        self.message = f"La propiedad con ID {id_propiedad} no tiene el valor de administración configurado."
        super().__init__(self.message)
