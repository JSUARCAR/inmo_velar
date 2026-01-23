"""
Tests para sistema de paginación.
"""

import pytest
from src.dominio.modelos.pagination import (
    PaginationParams,
    PaginatedResult,
    create_empty_result
)


class TestPaginationParams:
    """Tests para PaginationParams."""
    
    def test_default_values(self):
        """Test valores por defecto."""
        params = PaginationParams()
        
        assert params.page == 1
        assert params.page_size == 25
        assert params.sort_by is None
        assert params.sort_desc is False
    
    def test_custom_values(self):
        """Test valores customizados."""
        params = PaginationParams(
            page=3,
            page_size=50,
            sort_by='name',
            sort_desc=True
        )
        
        assert params.page == 3
        assert params.page_size == 50
        assert params.sort_by == 'name'
        assert params.sort_desc is True
    
    def test_offset_calculation(self):
        """Test cálculo de offset."""
        # Página 1
        params = PaginationParams(page=1, page_size=25)
        assert params.offset == 0
        
        # Página 2
        params = PaginationParams(page=2, page_size=25)
        assert params.offset == 25
        
        # Página 3 con page_size 50
        params = PaginationParams(page=3, page_size=50)
        assert params.offset == 100
    
    def test_limit_property(self):
        """Test propiedad limit."""
        params = PaginationParams(page_size=50)
        assert params.limit == 50
    
    def test_validation_page_min(self):
        """Test validación de página mínima."""
        with pytest.raises(ValueError, match="page debe ser >= 1"):
            PaginationParams(page=0)
    
    def test_validation_page_size_min(self):
        """Test validación de tamaño mínimo."""
        with pytest.raises(ValueError, match="page_size debe ser >= 1"):
            PaginationParams(page_size=0)
    
    def test_validation_page_size_max(self):
        """Test validación de tamaño máximo."""
        with pytest.raises(ValueError, match="page_size debe ser <= 100"):
            PaginationParams(page_size=101)
    
    def test_to_dict(self):
        """Test serialización a dict."""
        params = PaginationParams(page=2, page_size=50, sort_by='name')
        d = params.to_dict()
        
        assert d['page'] == 2
        assert d['page_size'] == 50
        assert d['sort_by'] == 'name'
        assert d['sort_desc'] is False


class TestPaginatedResult:
    """Tests para PaginatedResult."""
    
    def test_basic_properties(self):
        """Test propiedades básicas."""
        result = PaginatedResult(
            items=[1, 2, 3, 4, 5],
            total=50,
            page=1,
            page_size=5
        )
        
        assert len(result.items) == 5
        assert result.total == 50
        assert result.page == 1
        assert result.page_size == 5
    
    def test_total_pages_calculation(self):
        """Test cálculo de total de páginas."""
        # 50 items, 25 por página = 2 páginas
        result = PaginatedResult([], 50, 1, 25)
        assert result.total_pages == 2
        
        # 51 items, 25 por página = 3 páginas (ceil)
        result = PaginatedResult([], 51, 1, 25)
        assert result.total_pages == 3
        
        # 0 items = 1 página (mínimo)
        result = PaginatedResult([], 0, 1, 25)
        assert result.total_pages == 1
    
    def test_has_prev(self):
        """Test propiedad has_prev."""
        # Página 1 no tiene anterior
        result = PaginatedResult([], 100, 1, 25)
        assert result.has_prev is False
        
        # Página 2 sí tiene anterior
        result = PaginatedResult([], 100, 2, 25)
        assert result.has_prev is True
    
    def test_has_next(self):
        """Test propiedad has_next."""
        # Página 1 de 4 tiene siguiente
        result = PaginatedResult([], 100, 1, 25)
        assert result.has_next is True
        
        # Última página no tiene siguiente
        result = PaginatedResult([], 100, 4, 25)
        assert result.has_next is False
    
    def test_prev_page(self):
        """Test número de página anterior."""
        result = PaginatedResult([], 100, 1, 25)
        assert result.prev_page is None
        
        result = PaginatedResult([], 100, 3, 25)
        assert result.prev_page == 2
    
    def test_next_page(self):
        """Test número de página siguiente."""
        result = PaginatedResult([], 100, 4, 25)
        assert result.next_page is None
        
        result = PaginatedResult([], 100, 2, 25)
        assert result.next_page == 3
    
    def test_start_end_index(self):
        """Test índices de inicio y fin."""
        # Página 1 (items 1-25 de 100)
        result = PaginatedResult([], 100, 1, 25)
        assert result.start_index == 1
        assert result.end_index == 25
        
        # Página 2 (items 26-50 de 100)
        result = PaginatedResult([], 100, 2, 25)
        assert result.start_index == 26
        assert result.end_index == 50
        
        # Última página parcial (items 76-100 de 100)
        result = PaginatedResult([], 100, 4, 25)
        assert result.start_index == 76
        assert result.end_index == 100
        
        # Sin items
        result = PaginatedResult([], 0, 1, 25)
        assert result.start_index == 0
        assert result.end_index == 0
    
    def test_is_empty(self):
        """Test propiedad is_empty."""
        result = PaginatedResult([], 0, 1, 25)
        assert result.is_empty is True
        
        result = PaginatedResult([1, 2], 2, 1, 25)
        assert result.is_empty is False
    
    def test_to_dict(self):
        """Test serialización a dict."""
        result = PaginatedResult(
            items=[1, 2, 3],
            total=50,
            page=2,
            page_size=25
        )
        
        d = result.to_dict()
        
        # No incluye items
        assert 'items' not in d
        
        # Metadata
        assert d['total'] == 50
        assert d['page'] == 2
        assert d['page_size'] == 25
        assert d['total_pages'] == 2
        assert d['has_prev'] is True
        assert d['has_next'] is False
        assert d['start_index'] == 26
        assert d['end_index'] == 50
    
    def test_repr(self):
        """Test representación string."""
        result = PaginatedResult([1, 2, 3], 50, 2, 25)
        repr_str = repr(result)
        
        assert 'PaginatedResult' in repr_str
        assert 'items=3' in repr_str
        assert 'page=2/2' in repr_str
        assert 'total=50' in repr_str


class TestCreateEmptyResult:
    """Tests para helper create_empty_result."""
    
    def test_default_values(self):
        """Test valores por defecto."""
        result = create_empty_result()
        
        assert result.items == []
        assert result.total == 0
        assert result.page == 1
        assert result.page_size == 25
        assert result.is_empty is True
    
    def test_custom_values(self):
        """Test valores customizados."""
        result = create_empty_result(page=3, page_size=50)
        
        assert result.items == []
        assert result.total == 0
        assert result.page == 3
        assert result.page_size == 50


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
