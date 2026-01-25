"""
Interface (Protocol): Repositorio de Personas

Define operaciones específicas para el repositorio de Persona.
"""

from typing import List, Optional, Protocol

from src.dominio.entidades.persona import Persona


class IRepositorioPersona(Protocol):
    """
    Protocol para el repositorio de Personas.

    Incluye operaciones CRUD + métodos especializados.
    """

    # ---- CRUD Base ----

    def obtener_por_id(self, id: int) -> Optional[Persona]:
        """Obtiene una persona por ID."""
        ...

    def obtener_todos(
        self,
        filtro_rol: Optional[str] = None,
        solo_activos: bool = True,
        busqueda: Optional[str] = None,
        fecha_inicio: Optional[str] = None,
        fecha_fin: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Persona]:
        """Obtiene personas con filtros y paginación."""
        ...

    def contar_todos(
        self,
        filtro_rol: Optional[str] = None,
        solo_activos: bool = True,
        busqueda: Optional[str] = None,
        fecha_inicio: Optional[str] = None,
        fecha_fin: Optional[str] = None
    ) -> int:
        """Cuenta total de personas con filtros."""
        ...

    def agregar(self, persona: Persona, usuario_sistema: str) -> Persona:
        """Agrega una nueva persona."""
        ...

    def actualizar(self, persona: Persona, usuario_sistema: str) -> bool:
        """Actualiza una persona existente."""
        ...

    def inactivar(self, id_persona: int, motivo: str, usuario_sistema: str) -> bool:
        """Inactiva una persona."""
        ...

    # ---- Operaciones Especializadas ----

    def obtener_por_documento(
        self, numero_documento: str
    ) -> Optional[Persona]:
        """Busca una persona por su documento."""
        ...

    def obtener_por_email(self, email: str) -> Optional[Persona]:
        """Busca una persona por email."""
        ...

    def buscar_por_nombre(self, termino_busqueda: str, limite: int = 20) -> List[Persona]:
        """
        Búsqueda fuzzy por nombre.

        Args:
            termino_busqueda: Texto a buscar
            limite: Número máximo de resultados

        Returns:
            Lista de personas que coinciden
        """
        ...
