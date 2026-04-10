from typing import Protocol, List

from ..entidades.historial_incidente import HistorialIncidente


class RepositorioHistorialIncidentes(Protocol):
    def guardar(self, historial: HistorialIncidente) -> int: ...

    def obtener_por_incidente(self, id_incidente: int) -> List[HistorialIncidente]: ...

    def obtener_por_id(self, id_historial: int) -> HistorialIncidente: ...
