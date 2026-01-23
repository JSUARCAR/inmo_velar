"""
Tests de Integración: Repositorio LiquidacionAsesor
Verifica operaciones CRUD y constraints en SQLite.
"""

import pytest
import os
import tempfile
from src.infraestructura.persistencia.database import DatabaseManager
from src.infraestructura.repositorios.repositorio_liquidacion_asesor_sqlite import RepositorioLiquidacionAsesorSQLite
from src.dominio.entidades.liquidacion_asesor import LiquidacionAsesor


@pytest.fixture
def db_manager():
    """Crea base de datos temporal para tests."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    manager = DatabaseManager(path)
    manager.inicializar_base_datos()
    
    yield manager
    
    manager.cerrar_conexion()
    os.unlink(path)


@pytest.fixture
def repositorio(db_manager):
    """Crea repositorio con base de datos temporal."""
    return RepositorioLiquidacionAsesorSQLite(db_manager)


@pytest.fixture
def liquidacion_ejemplo():
    """Liquidación de ejemplo para tests."""
    return LiquidacionAsesor(
        id_liquidacion_asesor=None,
        id_contrato_a=100,
        id_asesor=5,
        periodo_liquidacion="2024-12",
        canon_arrendamiento_liquidado=1500000,
        porcentaje_comision=500,
        comision_bruta=75000,
        total_descuentos=0,
        valor_neto_asesor=75000,
        estado_liquidacion="Pendiente",
        created_by="test"
    )


class TestRepositorioLiquidacionCRUD:
    """Tests de operaciones CRUD básicas."""
    
    def test_crear_liquidacion(self, repositorio, liquidacion_ejemplo):
        """Test: Crear liquidación y obtener ID."""
        id_creado = repositorio.crear(liquidacion_ejemplo)
        
        assert id_creado is not None
        assert id_creado > 0
    
    def test_obtener_por_id(self, repositorio, liquidacion_ejemplo):
        """Test: Obtener liquidación por ID."""
        id_creado = repositorio.crear(liquidacion_ejemplo)
        
        liq = repositorio.obtener_por_id(id_creado)
        
        assert liq is not None
        assert liq.id_liquidacion_asesor == id_creado
        assert liq.periodo_liquidacion == "2024-12"
        assert liq.porcentaje_comision == 500
    
    def test_actualizar_liquidacion(self, repositorio, liquidacion_ejemplo):
        """Test: Actualizar liquidación existente."""
        id_creado = repositorio.crear(liquidacion_ejemplo)
        
        liq = repositorio.obtener_por_id(id_creado)
        liq.porcentaje_comision = 600
        liq.comision_bruta = 90000
        liq.valor_neto_asesor = 90000
        
        repositorio.actualizar(liq)
        
        liq_actualizada = repositorio.obtener_por_id(id_creado)
        assert liq_actualizada.porcentaje_comision == 600
        assert liq_actualizada.comision_bruta == 90000
    
    def test_listar_todas(self, repositorio, liquidacion_ejemplo):
        """Test: Listar todas las liquidaciones."""
        repositorio.crear(liquidacion_ejemplo)
        
        liquidacion_ejemplo.periodo_liquidacion = "2024-11"
        repositorio.crear(liquidacion_ejemplo)
        
        lista = repositorio.listar_todas()
        
        assert len(lista) >= 2


class TestRepositorioLiquidacionConstraints:
    """Tests de constraints y validaciones de BD."""
    
    def test_unique_constraint_contrato_periodo(self, repositorio, liquidacion_ejemplo):
        """Test: UNIQUE constraint debe fallar en duplicado contrato+período."""
        repositorio.crear(liquidacion_ejemplo)
        
        # Intentar crear otra con mismo contrato+período
        with pytest.raises(ValueError, match="ya existe"):
            repositorio.crear(liquidacion_ejemplo)
    
    def test_diferentes_periodos_ok(self, repositorio, liquidacion_ejemplo):
        """Test: Mismo contrato, diferente período es válido."""
        repositorio.crear(liquidacion_ejemplo)
        
        liquidacion_ejemplo.periodo_liquidacion = "2024-11"
        id_2 = repositorio.crear(liquidacion_ejemplo)
        
        assert id_2 is not None


class TestRepositorioLiquidacionConsultas:
    """Tests de consultas especializadas."""
    
    def test_listar_por_asesor(self, repositorio, liquidacion_ejemplo):
        """Test: Consultar liquidaciones por asesor."""
        repositorio.crear(liquidacion_ejemplo)
        
        liquidacion_ejemplo.periodo_liquidacion = "2024-11"
        repositorio.crear(liquidacion_ejemplo)
        
        lista = repositorio.listar_por_asesor(5)
        
        assert len(lista) == 2
        for liq in lista:
            assert liq.id_asesor == 5
    
    def test_listar_por_periodo(self, repositorio, liquidacion_ejemplo):
        """Test: Consultar liquidaciones por período."""
        repositorio.crear(liquidacion_ejemplo)
        
        lista = repositorio.listar_por_periodo("2024-12")
        
        assert len(lista) >= 1
        assert lista[0].periodo_liquidacion == "2024-12"
    
    def test_listar_por_estado(self, repositorio, liquidacion_ejemplo):
        """Test: Consultar liquidaciones por estado."""
        repositorio.crear(liquidacion_ejemplo)
        
        lista = repositorio.listar_por_estado("Pendiente")
        
        assert len(lista) >= 1
        assert all(liq.estado_liquidacion == "Pendiente" for liq in lista)


class TestRepositorioLiquidacionAnulacion:
    """Tests de anulación de liquidaciones."""
    
    def test_anular_cambia_estado(self, repositorio, liquidacion_ejemplo):
        """Test: Anular liquidación cambia estado a Anulada."""
        id_creado = repositorio.crear(liquidacion_ejemplo)
        
        liq = repositorio.obtener_por_id(id_creado)
        liq.estado_liquidacion = "Anulada"
        liq.observaciones_liquidacion = "Anulada por test"
        
        repositorio.actualizar(liq)
        
        liq_anulada = repositorio.obtener_por_id(id_creado)
        assert liq_anulada.estado_liquidacion == "Anulada"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
