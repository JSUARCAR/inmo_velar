import pytest
from unittest.mock import MagicMock
from src.aplicacion.servicios.servicio_reportes import ServicioReportes

@pytest.mark.asyncio
async def test_obtener_datos_reporte_mandato_enrutado():
    servicio = ServicioReportes()
    servicio.repo_reportes.obtener_reporte_contratos_mandato = MagicMock(return_value=([{"ID_CONTRATO_M": 1}], 1))
    
    data, headers, total = await servicio.obtener_datos_reporte("contratos_mandato", filtros={"busqueda": "Prueba"})
    
    servicio.repo_reportes.obtener_reporte_contratos_mandato.assert_called_once_with(busqueda="Prueba", page=1, limit=20)
    assert total == 1
    assert data == [{"ID_CONTRATO_M": 1}]
    assert headers == ["ID_CONTRATO_M"]

@pytest.mark.asyncio
async def test_obtener_datos_reporte_arrendamiento_enrutado():
    servicio = ServicioReportes()
    servicio.repo_reportes.obtener_reporte_contratos_arrendamiento = MagicMock(return_value=([{"ID_CONTRATO_A": 1}], 1))
    
    data, headers, total = await servicio.obtener_datos_reporte("contratos_arrendamiento", filtros={"busqueda": "Prueba"})
    
    servicio.repo_reportes.obtener_reporte_contratos_arrendamiento.assert_called_once_with(busqueda="Prueba", page=1, limit=20)
    assert total == 1
