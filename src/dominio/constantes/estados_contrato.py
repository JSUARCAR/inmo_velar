"""
Constantes: Estados de Contrato

Define los posibles estados de un contrato de arrendamiento.
"""

from enum import Enum


class EstadoContrato(str, Enum):
    """
    Estados del ciclo de life de un contrato.

    - BORRADOR: Contrato en preparación, no firmado
    - ACTIVO: Contrato vigente y en ejecución
    - SUSPENDIDO: Temporalmente suspendido
    - FINALIZADO: Terminado normalmente
    - CANCELADO: Cancelado antes de tiempo
    - RENOVADO: Fue renovado (genera nuevo contrato)
    """

    BORRADOR = "BORRADOR"
    ACTIVO = "ACTIVO"
    SUSPENDIDO = "SUSPENDIDO"
    FINALIZADO = "FINALIZADO"
    CANCELADO = "CANCELADO"
    RENOVADO = "RENOVADO"

    def es_activo(self) -> bool:
        """Retorna True si el estado permite operaciones activas."""
        return self in [EstadoContrato.ACTIVO, EstadoContrato.SUSPENDIDO]
