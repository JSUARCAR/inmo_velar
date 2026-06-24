import pytest
from unittest.mock import patch, MagicMock
from src.infraestructura.persistencia.repositorio_reportes import RepositorioReportes

def test_obtener_reporte_contratos_mandato_llama_paginacion():
    repo = RepositorioReportes()
    with patch.object(repo, '_ejecutar_query_paginada', return_value=([], 0)) as mock_ejecutar:
        result = repo.obtener_reporte_contratos_mandato(busqueda="Juan", page=1, limit=20)
        assert mock_ejecutar.called
        args = mock_ejecutar.call_args[0]
        assert "PROPIEDADES" in args[0]
        assert "PROPIETARIOS" in args[0]
        assert result == ([], 0)

def test_obtener_reporte_contratos_arrendamiento_llama_paginacion():
    repo = RepositorioReportes()
    with patch.object(repo, '_ejecutar_query_paginada', return_value=([], 0)) as mock_ejecutar:
        result = repo.obtener_reporte_contratos_arrendamiento(busqueda="Pedro", page=1, limit=20)
        assert mock_ejecutar.called
        args = mock_ejecutar.call_args[0]
        assert "ARRENDATARIOS" in args[0]
        assert "CODEUDORES" in args[0]
        assert result == ([], 0)
