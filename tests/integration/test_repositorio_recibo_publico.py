
import pytest
import sqlite3
from src.infraestructura.persistencia.database import DatabaseManager
from src.infraestructura.repositorios.repositorio_recibo_publico_sqlite import RepositorioReciboPublicoSQLite
from src.dominio.entidades.recibo_publico import ReciboPublico

# Schema mínimo para pruebas
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS PROPIEDADES (
    ID_PROPIEDAD INTEGER PRIMARY KEY AUTOINCREMENT,
    MATRICULA TEXT,
    DIRECCION TEXT,
    CREATED_BY TEXT,
    UPDATED_BY TEXT
);

CREATE TABLE IF NOT EXISTS RECIBOS_PUBLICOS (
    ID_RECIBO_PUBLICO INTEGER PRIMARY KEY AUTOINCREMENT,
    ID_PROPIEDAD INTEGER NOT NULL,
    PERIODO_RECIBO TEXT NOT NULL,
    TIPO_SERVICIO TEXT NOT NULL,
    VALOR_RECIBO INTEGER NOT NULL,
    FECHA_VENCIMIENTO TEXT,
    FECHA_PAGO TEXT,
    COMPROBANTE TEXT,
    ESTADO TEXT DEFAULT 'Pendiente',
    CREATED_AT TEXT DEFAULT (datetime('now', 'localtime')),
    CREATED_BY TEXT,
    UPDATED_AT TEXT,
    UPDATED_BY TEXT,
    FOREIGN KEY(ID_PROPIEDAD) REFERENCES PROPIEDADES(ID_PROPIEDAD),
    UNIQUE(ID_PROPIEDAD, PERIODO_RECIBO, TIPO_SERVICIO)
);
"""

@pytest.fixture
def db_manager(tmp_path):
    """Fixture para gestor de BD con archivo temporal"""
    db_file = tmp_path / "test_recibos.db"
    
    # Sobreescribir path en singleton (cuidado con paralelismo, pero pytest corre single safe por defecto)
    manager = DatabaseManager()
    manager.database_path = db_file
    manager._connection_pool = {}
    
    # Inicializar schema
    manager.ejecutar_script(SCHEMA_SQL)
    
    # Crear propiedad de prueba
    manager.ejecutar_script("INSERT INTO PROPIEDADES (ID_PROPIEDAD, MATRICULA) VALUES (1, 'MAT-001')")
    
    yield manager
    
    manager.cerrar_todas_conexiones()

@pytest.fixture
def repo_recibos(db_manager):
    return RepositorioReciboPublicoSQLite(db_manager)

class TestRepositorioReciboPublicoSQLite:
    
    def test_crear_recibo(self, repo_recibos):
        recibo = ReciboPublico(
            id_propiedad=1,
            periodo_recibo="2025-01",
            tipo_servicio="Agua",
            valor_recibo=50000,
            fecha_vencimiento="2025-01-30"
        )
        
        creado = repo_recibos.crear(recibo, "admin")
        
        assert creado.id_recibo_publico is not None
        assert creado.id_recibo_publico > 0
        
        # Verificar en BD
        recuperado = repo_recibos.obtener_por_id(creado.id_recibo_publico)
        assert recuperado is not None
        assert recuperado.tipo_servicio == "Agua"
        assert recuperado.valor_recibo == 50000
        
    def test_constraint_unique(self, repo_recibos):
        """No debe permitir dos recibos del mismo servicio/periodo/propiedad"""
        recibo1 = ReciboPublico(
            id_propiedad=1,
            periodo_recibo="2025-01",
            tipo_servicio="Luz",
            valor_recibo=100
        )
        repo_recibos.crear(recibo1, "admin")
        
        recibo2 = ReciboPublico(
            id_propiedad=1,
            periodo_recibo="2025-01",
            tipo_servicio="Luz",
            valor_recibo=200
        )
        
        with pytest.raises(ValueError, match="Ya existe un recibo de Luz"):
            repo_recibos.crear(recibo2, "admin")
            
    def test_actualizar_recibo(self, repo_recibos):
        recibo = ReciboPublico(
            id_propiedad=1,
            periodo_recibo="2025-02",
            tipo_servicio="Gas",
            valor_recibo=30000
        )
        creado = repo_recibos.crear(recibo, "admin")
        
        creado.valor_recibo = 35000
        creado.estado = "Pagado"
        
        actualizado = repo_recibos.actualizar(creado, "admin")
        
        assert actualizado.valor_recibo == 35000
        assert actualizado.estado == "Pagado"
        assert actualizado.updated_by == "admin"
        
    def test_listar_por_propiedad(self, repo_recibos):
        # Crear varios recibos
        r1 = ReciboPublico(id_propiedad=1, periodo_recibo="2025-01", tipo_servicio="Agua", valor_recibo=100)
        r2 = ReciboPublico(id_propiedad=1, periodo_recibo="2025-02", tipo_servicio="Agua", valor_recibo=100)
        repo_recibos.crear(r1, "admin")
        repo_recibos.crear(r2, "admin")
        
        lista = repo_recibos.listar_por_propiedad(1)
        assert len(lista) == 2
        
        # Filtro por periodo
        lista_feb = repo_recibos.listar_por_propiedad(1, periodo_inicio="2025-02")
        assert len(lista_feb) == 1
        assert lista_feb[0].periodo_recibo == "2025-02"

    def test_listar_vencidos(self, repo_recibos):
        # Recibo vencido
        r1 = ReciboPublico(
            id_propiedad=1, 
            periodo_recibo="2024-01", 
            tipo_servicio="Internet", 
            valor_recibo=100,
            fecha_vencimiento="2024-01-01",
            estado="Pendiente"
        )
        repo_recibos.crear(r1, "admin")
        
        # Recibo no vencido
        r2 = ReciboPublico(
            id_propiedad=1, 
            periodo_recibo="2026-01", 
            tipo_servicio="Internet", 
            valor_recibo=100,
            fecha_vencimiento="2026-01-01",
            estado="Pendiente"
        )
        repo_recibos.crear(r2, "admin")
        
        vencidos = repo_recibos.listar_vencidos()
        assert len(vencidos) >= 1
        fechas_vencidas = [r.fecha_vencimiento for r in vencidos]
        assert "2024-01-01" in fechas_vencidas
        assert "2026-01-01" not in fechas_vencidas
        
    def test_eliminar_soft_no_existe_fisica(self, repo_recibos):
        # Nota: El repositorio tiene eliminar físico DELETE, no soft delete según el código leído
        recibo = ReciboPublico(id_propiedad=1, periodo_recibo="2025-05", tipo_servicio="Aseo", valor_recibo=10)
        creado = repo_recibos.crear(recibo, "admin")
        
        id_r = creado.id_recibo_publico
        resultado = repo_recibos.eliminar(id_r)
        
        assert resultado is True
        assert repo_recibos.obtener_por_id(id_r) is None
