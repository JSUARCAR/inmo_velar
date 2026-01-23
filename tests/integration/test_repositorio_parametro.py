"""
Tests de integración para RepositorioParametroSQLite.
Usa la base de datos real con datos de prueba prefijados.
"""

import pytest
from datetime import datetime

from src.infraestructura.persistencia.database import db_manager
from src.infraestructura.persistencia.repositorio_parametro_sqlite import RepositorioParametroSQLite
from src.dominio.entidades.parametro_sistema import ParametroSistema


# Prefijo para identificar datos de prueba
TEST_PREFIX = "TEST_INTEG_"


@pytest.fixture
def repositorio():
    """Crea instancia del repositorio."""
    return RepositorioParametroSQLite(db_manager)


@pytest.fixture
def setup_test_data():
    """Configura datos de prueba y los limpia después."""
    # Insertar datos de prueba
    with db_manager.obtener_conexion() as conn:
        conn.executemany("""
            INSERT OR REPLACE INTO PARAMETROS_SISTEMA 
            (NOMBRE_PARAMETRO, VALOR_PARAMETRO, TIPO_DATO, DESCRIPCION, CATEGORIA, MODIFICABLE)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [
            (f"{TEST_PREFIX}COMISION", "800", "INTEGER", "Test comisión", "COMISIONES", 1),
            (f"{TEST_PREFIX}IMPUESTO", "4", "INTEGER", "Test impuesto", "IMPUESTOS", 0),
            (f"{TEST_PREFIX}ALERTA", "30", "INTEGER", "Test alerta", "ALERTAS", 1),
        ])
        conn.commit()
    
    yield
    
    # Cleanup
    with db_manager.obtener_conexion() as conn:
        conn.execute(f"DELETE FROM PARAMETROS_SISTEMA WHERE NOMBRE_PARAMETRO LIKE '{TEST_PREFIX}%'")
        conn.commit()


class TestRepositorioParametroSQLite:
    """Tests de integración para el repositorio de parámetros."""
    
    def test_obtener_por_nombre(self, repositorio, setup_test_data):
        """Test: Obtener parámetro por nombre."""
        parametro = repositorio.obtener_por_nombre(f"{TEST_PREFIX}COMISION")
        
        assert parametro is not None
        assert parametro.valor_parametro == "800"
        assert parametro.categoria == "COMISIONES"
    
    def test_obtener_por_nombre_no_existe(self, repositorio, setup_test_data):
        """Test: Obtener parámetro por nombre inexistente retorna None."""
        parametro = repositorio.obtener_por_nombre("NO_EXISTE_XYZ_999")
        
        assert parametro is None
    
    def test_listar_todos(self, repositorio, setup_test_data):
        """Test: Listar todos los parámetros incluye datos de prueba."""
        parametros = repositorio.listar_todos()
        
        nombres = [p.nombre_parametro for p in parametros]
        assert any(TEST_PREFIX in n for n in nombres)
    
    def test_listar_categorias(self, repositorio, setup_test_data):
        """Test: Listar categorías únicas."""
        categorias = repositorio.listar_categorias()
        
        assert "COMISIONES" in categorias
        assert "IMPUESTOS" in categorias
        assert "ALERTAS" in categorias
    
    def test_actualizar_parametro_modificable(self, repositorio, setup_test_data):
        """Test: Actualizar parámetro modificable."""
        parametro = repositorio.obtener_por_nombre(f"{TEST_PREFIX}COMISION")
        parametro.valor_parametro = "900"
        
        resultado = repositorio.actualizar(parametro, "test_user")
        
        assert resultado is True
        
        # Verificar
        actualizado = repositorio.obtener_por_id(parametro.id_parametro)
        assert actualizado.valor_parametro == "900"
    
    def test_actualizar_parametro_no_modificable(self, repositorio, setup_test_data):
        """Test: Actualizar parámetro no modificable lanza PermissionError."""
        parametro = repositorio.obtener_por_nombre(f"{TEST_PREFIX}IMPUESTO")
        parametro.valor_parametro = "5"
        
        with pytest.raises(PermissionError) as exc_info:
            repositorio.actualizar(parametro, "test_user")
        
        assert "no es modificable" in str(exc_info.value)
    
    def test_crear_parametro(self, repositorio, setup_test_data):
        """Test: Crear nuevo parámetro."""
        nuevo = ParametroSistema(
            nombre_parametro=f"{TEST_PREFIX}NUEVO",
            valor_parametro="test_value",
            tipo_dato="TEXT",
            descripcion="Parámetro de prueba",
            categoria="PRUEBAS",
            modificable=1
        )
        
        creado = repositorio.crear(nuevo, "test_user")
        
        assert creado.id_parametro is not None
        
        # Cleanup adicional para este test
        with db_manager.obtener_conexion() as conn:
            conn.execute(f"DELETE FROM PARAMETROS_SISTEMA WHERE NOMBRE_PARAMETRO = '{TEST_PREFIX}NUEVO'")
            conn.commit()
