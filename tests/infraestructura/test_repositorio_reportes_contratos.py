import pytest
from tests.integration.test_database_manager import TestDatabaseManager
from src.infraestructura.persistencia.repositorio_reportes import RepositorioReportes

@pytest.fixture
def db_manager(tmp_path):
    """Crea un TestDatabaseManager con BD temporal y esquema simplificado para reportes."""
    db_file = tmp_path / "test_reportes_contratos.db"
    db_manager = TestDatabaseManager(str(db_file))
    
    with db_manager.obtener_conexion() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS PERSONAS (
                ID_PERSONA INTEGER PRIMARY KEY AUTOINCREMENT,
                TIPO_DOCUMENTO TEXT,
                NUMERO_DOCUMENTO TEXT,
                NOMBRE_COMPLETO TEXT,
                TELEFONO_PRINCIPAL TEXT,
                CORREO_ELECTRONICO TEXT,
                DIRECCION_PRINCIPAL TEXT,
                ESTADO_REGISTRO INTEGER DEFAULT 1
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS PROPIEDADES (
                ID_PROPIEDAD INTEGER PRIMARY KEY AUTOINCREMENT,
                DIRECCION_PROPIEDAD TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS PROPIETARIOS (
                ID_PROPIETARIO INTEGER PRIMARY KEY AUTOINCREMENT,
                ID_PERSONA INTEGER
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ASESORES (
                ID_ASESOR INTEGER PRIMARY KEY AUTOINCREMENT,
                ID_PERSONA INTEGER
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ARRENDATARIOS (
                ID_ARRENDATARIO INTEGER PRIMARY KEY AUTOINCREMENT,
                ID_PERSONA INTEGER,
                NOMBRE_HABITANTE TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS CODEUDORES (
                ID_CODEUDOR INTEGER PRIMARY KEY AUTOINCREMENT,
                ID_PERSONA INTEGER
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS CONTRATOS_MANDATOS (
                ID_CONTRATO_M INTEGER PRIMARY KEY AUTOINCREMENT,
                ID_PROPIEDAD INTEGER,
                ID_PROPIETARIO INTEGER,
                ID_ASESOR INTEGER,
                ESTADO_CONTRATO_M TEXT,
                FECHA_INICIO_CONTRATO_M TEXT,
                FECHA_FIN_CONTRATO_M TEXT,
                DURACION_CONTRATO_M INTEGER,
                CANON_MANDATO REAL,
                COMISION_PORCENTAJE_CONTRATO_M REAL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS CONTRATOS_ARRENDAMIENTOS (
                ID_CONTRATO_A INTEGER PRIMARY KEY AUTOINCREMENT,
                ID_PROPIEDAD INTEGER,
                ID_ARRENDATARIO INTEGER,
                ID_CODEUDOR INTEGER,
                ESTADO_CONTRATO_A TEXT,
                FECHA_INICIO_CONTRATO_A TEXT,
                FECHA_FIN_CONTRATO_A TEXT,
                DURACION_CONTRATO_A INTEGER,
                CANON_ARRENDAMIENTO REAL,
                DEPOSITO REAL
            )
        """)
        conn.commit()
    
    yield db_manager
    
    db_manager.cerrar_todas_conexiones()
    if db_file.exists():
        db_file.unlink()

@pytest.fixture
def repo(db_manager):
    repo = RepositorioReportes()
    repo.db = db_manager
    return repo

def test_obtener_reporte_contratos_mandato_sin_busqueda(repo):
    """Prueba de integración real contra DB temporal que verifica la sintaxis SQL."""
    # La DB está vacía, debe retornar([], 0) y no fallar en sintaxis
    resultados, total = repo.obtener_reporte_contratos_mandato(busqueda=None, page=1, limit=20)
    assert resultados == []
    assert total == 0

def test_obtener_reporte_contratos_mandato_con_busqueda(repo):
    """Prueba de integración real verificando que la búsqueda dinámica funcione (edge case)."""
    resultados, total = repo.obtener_reporte_contratos_mandato(busqueda="Juan", page=1, limit=20)
    assert resultados == []
    assert total == 0

def test_obtener_reporte_contratos_arrendamiento_sin_busqueda(repo):
    """Prueba de integración real verificando sintaxis SQL y LEFT JOINs sin búsqueda."""
    resultados, total = repo.obtener_reporte_contratos_arrendamiento(busqueda=None, page=1, limit=20)
    assert resultados == []
    assert total == 0

def test_obtener_reporte_contratos_arrendamiento_con_busqueda(repo):
    """Prueba de integración real verificando que la búsqueda dinámica funcione."""
    resultados, total = repo.obtener_reporte_contratos_arrendamiento(busqueda="Pedro", page=1, limit=20)
    assert resultados == []
    assert total == 0
