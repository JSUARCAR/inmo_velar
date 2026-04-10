from typing import Any, Dict, List, Optional, Protocol as Protocol

from ..entidades.incidente import Incidente


class RepositorioIncidentes(Protocol):
    """
    Interface completa para operaciones de Incidentes.
    Combina operaciones base, cotizaciones e historial.

    Nota: Para mejor adherencia a Interface Segregation Principle,
    considere usar las interfaces separadas:
    - RepositorioIncidentesBase (operaciones core)
    - RepositorioCotizaciones
    - RepositorioHistorialIncidentes
    """

    def obtener_por_id(self, id_incidente: int) -> Optional[Incidente]: ...

    def listar(
        self, id_propiedad: Optional[int] = None, estado: Optional[str] = None
    ) -> List[Incidente]: ...

    def listar_con_filtros(
        self,
        busqueda: Optional[str] = None,
        id_propiedad: Optional[int] = None,
        prioridad: Optional[str] = None,
        fecha_desde: Optional[str] = None,
        fecha_hasta: Optional[str] = None,
        id_proveedor: Optional[int] = None,
        dias_min: Optional[int] = None,
        estado: Optional[str] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> Dict[str, Any]: ...

    def guardar(self, incidente: Incidente) -> int: ...

    def actualizar(self, incidente: Incidente) -> None: ...

    def eliminar(self, id_incidente: int) -> None: ...

    def guardar_cotizacion(self, cotizacion) -> int: ...

    def obtener_cotizaciones(self, id_incidente: int) -> List: ...

    def actualizar_cotizacion(self, cotizacion) -> None: ...

    def guardar_historial(self, historial) -> int: ...

    def obtener_historial(self, id_incidente: int) -> List: ...
