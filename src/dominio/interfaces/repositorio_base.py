"""
Interface (Protocol): Repositorio Base Genérico

Define el contrato que deben cumplir todos los repositorios.
"""

from typing import Dict, Generic, List, Optional, Protocol, TypeVar

from src.dominio.modelos.pagination import PaginatedResult, PaginationParams

T = TypeVar("T")  # Tipo genérico para cualquier entidad


class IRepositorio(Protocol, Generic[T]):
    """
    Protocol genérico para operaciones CRUD.

    Cualquier clase que implemente estos métodos es compatible
    con este protocolo sin necesidad de herencia explícita (duck typing).
    """

    def obtener_por_id(self, id: int) -> Optional[T]:
        """
        Obtiene una entidad por su ID.

        Args:
            id: Identificador único

        Returns:
            La entidad o None si no existe
        """
        ...

    def obtener_todos(
        self, solo_activos: bool = True, limite: Optional[int] = None, offset: int = 0
    ) -> List[T]:
        """
        Obtiene todas las entidades.

        Args:
            solo_activos: Filtrar solo entidades activas
            limite: Número máximo de resultados (paginación)
            offset: Número de resultados a saltar

        Returns:
            Lista de entidades (puede estar vacía)
        """
        ...

    def agregar(self, entidad: T) -> T:
        """
        Agrega una nueva entidad.

        Args:
            entidad: Entidad a agregar

        Returns:
            La entidad con su ID asignado
        """
        ...

    def actualizar(self, entidad: T) -> T:
        """
        Actualiza una entidad existente.

        Args:
            entidad: Entidad a actualizar (debe tener ID)

        Returns:
            La entidad actualizada
        """
        ...

    def eliminar(self, id: int) -> bool:
        """
        Elimina una entidad (hard delete).

        Args:
            id: ID de la entidad

        Returns:
            True si se eliminó
        """
        ...

    def existe(self, id: int) -> bool:
        """
        Verifica si existe una entidad con el ID dado.

        Args:
            id: ID a verificar

        Returns:
            True si existe
        """
        ...

    def contar(self, solo_activos: bool = True) -> int:
        """
        Cuenta el número de entidades.

        Args:
            solo_activos: Solo contar entidades activas

        Returns:
            Número total de entidades
        """
        ...

    def obtener_paginado(
        self, params: PaginationParams, filtros: Optional[Dict] = None
    ) -> PaginatedResult[T]:
        """
        Obtiene entidades con paginación.

        Args:
            params: Parámetros de paginación
            filtros: Filtros adicionales opcionales

        Returns:
            Resultado paginado con items y metadata
        """
        ...
