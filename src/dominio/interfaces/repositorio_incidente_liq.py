"""
Interface Repository: IncidenteLiquidacion
Define el contrato para operaciones de relaciones incidente-liquidación.

Feature: 003-integracion-incidentes-liquidaciones
Date: 2026-06-30
"""

from typing import List, Optional, Protocol

from ..entidades.incidente_liquidacion import IncidenteLiquidacion


class RepositorioIncidenteLiquidacion(Protocol):
    """
    Interface para operaciones de relaciones incidente-liquidación.

    Methods:
        crear: Crea una nueva relación
        obtener_por_id: Obtiene una relación por su ID
        obtener_por_incidente: Obtiene relaciones de un incidente
        obtener_por_liquidacion: Obtiene relaciones de una liquidación
        eliminar: Elimina una relación
        calcular_total_descuentos: Calcula total de descuentos para una liquidación
    """

    def crear(self, relacion: IncidenteLiquidacion) -> IncidenteLiquidacion:
        """
        Crea una nueva relación.

        Args:
            relacion: Relación a crear

        Returns:
            Relación creada con ID asignado
        """
        ...

    def obtener_por_id(self, id_relacion: int) -> Optional[IncidenteLiquidacion]:
        """
        Obtiene una relación por su ID.

        Args:
            id_relacion: ID de la relación

        Returns:
            Relación encontrada o None
        """
        ...

    def obtener_por_incidente(self, id_incidente: int) -> List[IncidenteLiquidacion]:
        """
        Obtiene todas las relaciones de un incidente.

        Args:
            id_incidente: ID del incidente

        Returns:
            Lista de relaciones del incidente
        """
        ...

    def obtener_por_liquidacion(
        self, id_liquidacion: int
    ) -> List[IncidenteLiquidacion]:
        """
        Obtiene todas las relaciones de una liquidación.

        Args:
            id_liquidacion: ID de la liquidación

        Returns:
            Lista de relaciones de la liquidación
        """
        ...

    def eliminar(self, id_relacion: int) -> bool:
        """
        Elimina una relación.

        Args:
            id_relacion: ID de la relación a eliminar

        Returns:
            True si se eliminó correctamente
        """
        ...

    def calcular_total_descuentos(self, id_liquidacion: int) -> int:
        """
        Calcula el total de descuentos para una liquidación.

        Args:
            id_liquidacion: ID de la liquidación

        Returns:
            Total de descuentos
        """
        ...
