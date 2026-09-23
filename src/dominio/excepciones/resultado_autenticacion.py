"""
Resultado de Autenticación

Contiene la estructura de éxito y re-exporta las excepciones relacionadas a la autenticación.
"""

from typing import Any

from src.dominio.excepciones.excepciones_base import (
    ErrorAutenticacion,
    ErrorCredencialesInvalidas,
    ErrorUsuarioInactivo,
    ErrorRecurso,
    ErrorPoliticaIntentos,
)


class ExitoAutenticacion:
    """
    Representa el resultado exitoso de una autenticación.
    """

    def __init__(self, usuario: Any, sesion: Any):
        """
        Args:
            usuario: El usuario autenticado.
            sesion: La sesión generada.
        """
        self.usuario = usuario
        self.sesion = sesion


__all__ = [
    "ExitoAutenticacion",
    "ErrorAutenticacion",
    "ErrorCredencialesInvalidas",
    "ErrorUsuarioInactivo",
    "ErrorRecurso",
    "ErrorPoliticaIntentos",
]
