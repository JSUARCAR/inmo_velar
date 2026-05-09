"""
Interface (Puerto): Repositorio de Recaudos.
Definición del contrato para persistencia de pagos.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Generic, List, Optional, TypeVar

from src.dominio.constantes.recaudo import EstadoRecaudo
from src.dominio.entidades.recaudo import Recaudo
from src.dominio.entidades.recaudo_concepto import RecaudoConcepto

T = TypeVar("T")


@dataclass(frozen=True)
class FiltrosRecaudo:
    """Filtros tipados para consultas de recaudos."""
    estado: Optional[EstadoRecaudo] = None
    fecha_desde: Optional[str] = None
    fecha_hasta: Optional[str] = None
    id_contrato: Optional[int] = None
    busqueda: Optional[str] = None
    sort_by: str = "fecha_pago"
    sort_order: str = "desc"
    page: int = 1
    page_size: int = 25

    @property
    def offset(self) -> int:
        """Calcula el offset para la paginación."""
        return (self.page - 1) * self.page_size


@dataclass
class ResultadoPaginado(Generic[T]):
    """Resultado paginado genérico."""
    items: List[T] = field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 25

    @property
    def total_pages(self) -> int:
        """Calcula el total de páginas."""
        if self.page_size <= 0:
            return 0
        return (self.total + self.page_size - 1) // self.page_size


class IRepositorioRecaudo(ABC):
    """Puerto abstracto para repositorio de recaudos."""

    @abstractmethod
    def obtener_por_id(self, id_recaudo: int) -> Optional[Recaudo]:
        """Obtiene un recaudo por su ID."""
        raise NotImplementedError

    @abstractmethod
    def listar_por_contrato(self, id_contrato_a: int) -> List[Recaudo]:
        """Lista todos los recaudos de un contrato."""
        raise NotImplementedError

    @abstractmethod
    def listar_paginado(
        self,
        limit: int,
        offset: int,
        estado: Optional[str] = None,
        fecha_desde: Optional[str] = None,
        fecha_hasta: Optional[str] = None,
        busqueda: Optional[str] = None,
        sort_by: str = "fecha_pago",
        sort_order: str = "desc",
    ) -> List[Dict[str, Any]]:
        """Lista recaudos paginados con filtros y ordenamiento."""
        raise NotImplementedError

    @abstractmethod
    def contar_con_filtros(
        self,
        estado: Optional[str] = None,
        fecha_desde: Optional[str] = None,
        fecha_hasta: Optional[str] = None,
        busqueda: Optional[str] = None,
    ) -> int:
        """Cuenta total de recaudos con filtros aplicados."""
        raise NotImplementedError

    @abstractmethod
    def crear(
        self,
        recaudo: Recaudo,
        conceptos: List[RecaudoConcepto],
        usuario_sistema: str,
    ) -> Recaudo:
        """Crea un recaudo con sus conceptos asociados."""
        raise NotImplementedError

    @abstractmethod
    def actualizar(
        self,
        recaudo: Recaudo,
        usuario_sistema: str,
        conceptos: Optional[List[RecaudoConcepto]] = None,
    ) -> None:
        """Actualiza un recaudo existente y sus conceptos."""
        raise NotImplementedError

    @abstractmethod
    def cambiar_estado(
        self, id_recaudo: int, nuevo_estado: str, usuario_sistema: str
    ) -> None:
        """Cambia el estado de un recaudo."""
        raise NotImplementedError

    @abstractmethod
    def eliminar(self, id_recaudo: int, usuario_sistema: str) -> None:
        """Elimina un recaudo y sus conceptos."""
        raise NotImplementedError

    @abstractmethod
    def obtener_conceptos_por_recaudo(
        self, id_recaudo: int
    ) -> List[RecaudoConcepto]:
        """Obtiene los conceptos de un recaudo."""
        raise NotImplementedError

    @abstractmethod
    def obtener_ids_contratos_con_recaudo(self, periodo: str) -> List[int]:
        """Retorna IDs de contratos con recaudo en el período."""
        raise NotImplementedError

    @abstractmethod
    def crear_masivo(
        self,
        recaudos_y_conceptos: List[tuple[Recaudo, List[RecaudoConcepto]]],
        usuario_sistema: str,
    ) -> int:
        """Crea múltiples recaudos en una transacción."""
        raise NotImplementedError
