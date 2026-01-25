"""
Excepciones Base del Dominio

Define la jerarquía de excepciones de negocio.
"""

from datetime import datetime
from typing import Optional


class ExcepcionDominio(Exception):
    """
    Excepción base para todos los errores de dominio.

    Todas las excepciones de negocio deben heredar de esta clase.
    """

    def __init__(self, mensaje: str, codigo: Optional[str] = None):
        """
        Args:
            mensaje: Descripción del error
            codigo: Código de error opcional para catalogación
        """
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.codigo = codigo
        self.timestamp = datetime.now()

    def __str__(self) -> str:
        if self.codigo:
            return f"[{self.codigo}] {self.mensaje}"
        return self.mensaje


class ErrorValidacion(ExcepcionDominio):
    """
    Excepción para errores de validación de datos.

    Se lanza cuando una entidad o VO no cumple sus invariantes.
    """

    def __init__(self, mensaje: str, campo: Optional[str] = None):
        super().__init__(mensaje, "VAL_ERROR")
        self.campo = campo


class EntidadNoEncontrada(ExcepcionDominio):
    """
    Excepción cuando no se encuentra una entidad por su ID.
    """

    def __init__(self, tipo_entidad: str, id_entidad: int):
        mensaje = f"{tipo_entidad} con ID {id_entidad} no encontrada"
        super().__init__(mensaje, "NOT_FOUND")
        self.tipo_entidad = tipo_entidad
        self.id_entidad = id_entidad


class EntidadDuplicada(ExcepcionDominio):
    """
    Excepción cuando se intenta crear una entidad que ya existe.
    """

    def __init__(self, tipo_entidad: str, campo: str, valor: str):
        mensaje = f"{tipo_entidad} con {campo}='{valor}' ya existe"
        super().__init__(mensaje, "DUPLICATE")
        self.tipo_entidad = tipo_entidad
        self.campo = campo
        self.valor = valor


class OperacionNoPermitida(ExcepcionDominio):
    """
    Excepción cuando una operación no está permitida según reglas de negocio.
    """

    def __init__(self, mensaje: str):
        super().__init__(mensaje, "NOT_ALLOWED")


class ErrorAutenticacion(ExcepcionDominio):
    """
    Excepción para fallos en el proceso de autenticación.
    """

    def __init__(self, mensaje: str = "Credenciales inválidas"):
        super().__init__(mensaje, "AUTH_ERROR")


class SesionInvalida(ExcepcionDominio):
    """
    Excepción para tokens de sesión expirados o no encontrados.
    """

    def __init__(self, mensaje: str = "Sesión inválida o expirada"):
        super().__init__(mensaje, "SESSION_ERROR")
