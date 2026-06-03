"""
Tests de integración para Filtros Específicos de RepositorioPersona.

Verifica la lógica de "Inactivos" y "Sin contrato" en RepositorioPersonaPostgres.
"""
import pytest
from tests.integration.test_database_manager import TestDatabaseManager
from src.infraestructura.persistencia.repositorio_persona_postgres import RepositorioPersonaPostgres
from src.dominio.entidades.persona import Persona

@pytest.fixture
def db_manager(tmp_path):
    """Crea un TestDatabaseManager con esquema completo para filtros."""
    db_file = tmp_path / "test_filtros_persona.db"
    db_manager = TestDatabaseManager(str(db_file))
    
    with db_manager.obtener_conexion() as conn:
        # PERSONAS
        conn.execute("""
            CREATE TABLE IF NOT EXISTS PERSONAS (
                ID_PERSONA INTEGER PRIMARY KEY AUTOINCREMENT,
                TIPO_DOCUMENTO TEXT, NUMERO_DOCUMENTO TEXT UNIQUE,
                NOMBRE_COMPLETO TEXT, ESTADO_REGISTRO INTEGER DEFAULT 1,
                CREATED_AT TEXT
            )
        """)
        # ROLES
        conn.execute("CREATE TABLE PROPIETARIOS (ID_PROPIETARIO INTEGER PRIMARY KEY, ID_PERSONA INTEGER UNIQUE)")
        conn.execute("CREATE TABLE ARRENDATARIOS (ID_ARRENDATARIO INTEGER PRIMARY KEY, ID_PERSONA INTEGER UNIQUE)")
        conn.execute("CREATE TABLE ASESORES (ID_ASESOR INTEGER PRIMARY KEY, ID_PERSONA INTEGER UNIQUE)")
        conn.execute("CREATE TABLE CODEUDORES (ID_CODEUDOR INTEGER PRIMARY KEY, ID_PERSONA INTEGER UNIQUE)")
        conn.execute("CREATE TABLE PROVEEDORES (ID_PROVEEDOR INTEGER PRIMARY KEY, ID_PERSONA INTEGER UNIQUE)")
        
        # CONTRATOS MANDATOS (ID_PROPIETARIO, ID_ASESOR)
        conn.execute("""
            CREATE TABLE CONTRATOS_MANDATOS (
                ID_CONTRATO_M INTEGER PRIMARY KEY,
                ID_PROPIEDAD INTEGER, ID_PROPIETARIO INTEGER, ID_ASESOR INTEGER
            )
        """)
        # CONTRATOS ARRENDAMIENTOS (ID_ARRENDATARIO, ID_CODEUDOR)
        conn.execute("""
            CREATE TABLE CONTRATOS_ARRENDAMIENTOS (
                ID_CONTRATO_A INTEGER PRIMARY KEY,
                ID_PROPIEDAD INTEGER, ID_ARRENDATARIO INTEGER, ID_CODEUDOR INTEGER
            )
        """)
        conn.commit()
    
    yield db_manager
    db_manager.cerrar_todas_conexiones()

@pytest.fixture
def repo(db_manager):
    return RepositorioPersonaPostgres(db_manager)

class TestFiltrosPersonaEspecificos:
    
    def test_filtro_inactivos(self, repo, db_manager):
        """Verifica que el toggle de inactivos funciona."""
        with db_manager.obtener_conexion() as conn:
            conn.execute("INSERT INTO PERSONAS (NUMERO_DOCUMENTO, NOMBRE_COMPLETO, ESTADO_REGISTRO) VALUES ('1', 'Activo', 1)")
            conn.execute("INSERT INTO PERSONAS (NUMERO_DOCUMENTO, NOMBRE_COMPLETO, ESTADO_REGISTRO) VALUES ('2', 'Inactivo', 0)")
            conn.commit()
        
        # Solo activos (default)
        activos = repo.obtener_todos(solo_activos=True)
        assert len(activos) == 1
        assert activos[0].nombre_completo == "Activo"
        
        # Incluir inactivos
        todos = repo.obtener_todos(solo_activos=False)
        assert len(todos) == 2
        assert any(p.nombre_completo == "Inactivo" for p in todos)

    def test_filtro_sin_contrato_basico(self, repo, db_manager):
        """Verifica filtro de personas sin ningún contrato asociado."""
        with db_manager.obtener_conexion() as conn:
            # Persona 1: Propietario con contrato
            conn.execute("INSERT INTO PERSONAS (ID_PERSONA, NUMERO_DOCUMENTO, NOMBRE_COMPLETO) VALUES (1, '10', 'Prop Con Contrato')")
            conn.execute("INSERT INTO PROPIETARIOS (ID_PROPIETARIO, ID_PERSONA) VALUES (101, 1)")
            conn.execute("INSERT INTO CONTRATOS_MANDATOS (ID_CONTRATO_M, ID_PROPIETARIO, ID_ASESOR) VALUES (1001, 101, 999)")
            
            # Persona 2: Arrendatario con contrato
            conn.execute("INSERT INTO PERSONAS (ID_PERSONA, NUMERO_DOCUMENTO, NOMBRE_COMPLETO) VALUES (2, '20', 'Arr Con Contrato')")
            conn.execute("INSERT INTO ARRENDATARIOS (ID_ARRENDATARIO, ID_PERSONA) VALUES (201, 2)")
            conn.execute("INSERT INTO CONTRATOS_ARRENDAMIENTOS (ID_CONTRATO_A, ID_ARRENDATARIO) VALUES (2001, 201)")
            
            # Persona 3: Persona sin contrato
            conn.execute("INSERT INTO PERSONAS (ID_PERSONA, NUMERO_DOCUMENTO, NOMBRE_COMPLETO) VALUES (3, '30', 'Sin Contrato')")
            
            conn.commit()
            
        sin_contrato = repo.obtener_todos(sin_contrato=True)
        assert len(sin_contrato) == 1
        assert sin_contrato[0].nombre_completo == "Sin Contrato"

    def test_filtro_sin_contrato_excluye_proveedores_puros(self, repo, db_manager):
        """Verifica que proveedores con ROL ÚNICO sean excluidos del filtro 'Sin contrato'."""
        with db_manager.obtener_conexion() as conn:
            # Persona 1: Proveedor puro (debe ser excluido de 'Sin contrato' ya que no se espera que tengan)
            conn.execute("INSERT INTO PERSONAS (ID_PERSONA, NUMERO_DOCUMENTO, NOMBRE_COMPLETO) VALUES (1, 'P1', 'Proveedor Puro')")
            conn.execute("INSERT INTO PROVEEDORES (ID_PROVEEDOR, ID_PERSONA) VALUES (1, 1)")
            
            # Persona 2: Proveedor Y Propietario (debe aparecer si no tiene contrato)
            conn.execute("INSERT INTO PERSONAS (ID_PERSONA, NUMERO_DOCUMENTO, NOMBRE_COMPLETO) VALUES (2, 'P2', 'Proveedor y Prop')")
            conn.execute("INSERT INTO PROVEEDORES (ID_PROVEEDOR, ID_PERSONA) VALUES (2, 2)")
            conn.execute("INSERT INTO PROPIETARIOS (ID_PROPIETARIO, ID_PERSONA) VALUES (2, 2)")
            
            # Persona 3: Persona normal sin nada
            conn.execute("INSERT INTO PERSONAS (ID_PERSONA, NUMERO_DOCUMENTO, NOMBRE_COMPLETO) VALUES (3, 'P3', 'Normal Sin Nada')")
            
            conn.commit()
            
        sin_contrato = repo.obtener_todos(sin_contrato=True)
        
        # Debe contener a 'Proveedor y Prop' (porque es prop sin contrato) 
        # y a 'Normal Sin Nada'.
        # 'Proveedor Puro' debe ser EXCLUIDO.
        nombres = [p.nombre_completo for p in sin_contrato]
        assert "Normal Sin Nada" in nombres
        assert "Proveedor y Prop" in nombres
        assert "Proveedor Puro" not in nombres
        assert len(sin_contrato) == 2
