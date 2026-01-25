from abc import ABC, abstractmethod
from typing import Optional

from src.dominio.entidades.orden_trabajo import OrdenTrabajo


class RepositorioOrdenTrabajo(ABC):

    @abstractmethod
    def guardar(self, orden: OrdenTrabajo) -> int:
        pass

    @abstractmethod
    def obtener_por_id(self, id_orden: int) -> Optional[OrdenTrabajo]:
        pass

    @abstractmethod
    def obtener_por_incidente(self, id_incidente: int) -> Optional[OrdenTrabajo]:
        pass

    @abstractmethod
    def actualizar(self, orden: OrdenTrabajo) -> None:
        pass
