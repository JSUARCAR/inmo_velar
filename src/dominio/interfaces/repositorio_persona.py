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
        self, solo_activos: bool = True, limite: Optional[int] = None, offset: int = 0
    ) -> List[Persona]:
        """Obtiene todas las personas."""
        ...

    def agregar(self, persona: Persona) -> Persona:
        """Agrega una nueva persona."""
        ...

    def actualizar(self, persona: Persona) -> Persona:
        """Actualiza una persona existente."""
        ...

    def eliminar(self, id: int) -> bool:
        """Elimina una persona."""
        ...

    # ---- Operaciones Especializadas ----

    def obtener_por_documento(
        self, tipo_documento: str, numero_documento: str
    ) -> Optional[Persona]:
        """
        Busca una persona por su documento.

        Args:
            tipo_documento: Tipo (CC, NIT, etc.)
            numero_documento: Número del documento

        Returns:
            La persona o None
        """
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
