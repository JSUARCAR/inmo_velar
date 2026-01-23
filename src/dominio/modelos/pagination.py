"""
Modelos de dominio para paginación.

Define estructuras de datos para resultados paginados y parámetros de paginación.

Autor: InmoVelar Dev Team
Fecha: 2025-12-29
"""

from dataclasses import dataclass
from typing import Generic, TypeVar, List, Optional
import math

T = TypeVar('T')


@dataclass
class PaginationParams:
    """
    Parámetros de paginación para queries.
    
    Attributes:
        page: Número de página (1-indexed)
        page_size: Items por página
        sort_by: Campo para ordenar (opcional)
        sort_desc: Ordenar descendente (default: False)
    """
    page: int = 1
    page_size: int = 25
    sort_by: Optional[str] = None
    sort_desc: bool = False
    
    def __post_init__(self):
        """Validaciones."""
        if self.page < 1:
            raise ValueError("page debe ser >= 1")
        if self.page_size < 1:
            raise ValueError("page_size debe ser >= 1")
        if self.page_size > 100:
            raise ValueError("page_size debe ser <= 100")
    
    @property
    def offset(self) -> int:
        """Calcula offset para SQL LIMIT/OFFSET."""
        return (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        """Retorna limit para SQL."""
        return self.page_size
    
    def to_dict(self) -> dict:
        """Serializa a diccionario."""
        return {
            'page': self.page,
            'page_size': self.page_size,
            'sort_by': self.sort_by,
            'sort_desc': self.sort_desc
        }


@dataclass
class PaginatedResult(Generic[T]):
    """
    Resultado paginado genérico.
    
    Attributes:
        items: Lista de items de la página actual
        total: Total de items (sin paginar)
        page: Página actual
        page_size: Tamaño de página
        total_pages: Total de páginas calculado
    """
    items: List[T]
    total: int
    page: int
    page_size: int
    
    @property
    def total_pages(self) -> int:
        """Calcula total de páginas."""
        if self.total == 0:
            return 1
        return math.ceil(self.total / self.page_size)
    
    @property
    def has_prev(self) -> bool:
        """Indica si hay página anterior."""
        return self.page > 1
    
    @property
    def has_next(self) -> bool:
        """Indica si hay página siguiente."""
        return self.page < self.total_pages
    
    @property
    def prev_page(self) -> Optional[int]:
        """Número de página anterior."""
        return self.page - 1 if self.has_prev else None
    
    @property
    def next_page(self) -> Optional[int]:
        """Número de página siguiente."""
        return self.page + 1 if self.has_next else None
    
    @property
    def start_index(self) -> int:
        """Índice del primer item en la página (1-indexed)."""
        if self.total == 0:
            return 0
        return (self.page - 1) * self.page_size + 1
    
    @property
    def end_index(self) -> int:
        """Índice del último item en la página (1-indexed)."""
        if self.total == 0:
            return 0
        end = self.page * self.page_size
        return min(end, self.total)
    
    @property
    def is_empty(self) -> bool:
        """Indica si no hay resultados."""
        return len(self.items) == 0
    
    def to_dict(self) -> dict:
        """
        Serializa a diccionario (sin items).
        Útil para metadata de API.
        """
        return {
            'total': self.total,
            'page': self.page,
            'page_size': self.page_size,
            'total_pages': self.total_pages,
            'has_prev': self.has_prev,
            'has_next': self.has_next,
            'start_index': self.start_index,
            'end_index': self.end_index
        }
    
    def __repr__(self) -> str:
        """Representación string."""
        return (
            f"PaginatedResult("
            f"items={len(self.items)}, "
            f"page={self.page}/{self.total_pages}, "
            f"total={self.total})"
        )


def create_empty_result(page: int = 1, page_size: int = 25) -> PaginatedResult:
    """
    Crea resultado paginado vacío.
    
    Args:
        page: Número de página
        page_size: Tamaño de página
        
    Returns:
        PaginatedResult vacío
    """
    return PaginatedResult(
        items=[],
        total=0,
        page=page,
        page_size=page_size
    )
