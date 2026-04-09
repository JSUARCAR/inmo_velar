from typing import List, Optional, Protocol

from ..entidades.incidente import Incidente


class RepositorioIncidentesBase(Protocol):
    """Interface base para operaciones CRUD de incidentes."""

    def obtener_por_id(self, id_incidente: int) -> Optional[Incidente]: ...

    def listar(
        self, id_propiedad: Optional[int] = None, estado: Optional[str] = None
    ) -> List[Incidente]: ...

    def guardar(self, incidente: Incidente) -> int: ...

    def actualizar(self, incidente: Incidente) -> None: ...

    def eliminar(self, id_incidente: int) -> None: ...
