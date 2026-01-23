"""
Tests de integración para RepositorioPropiedadSQLite.

Verifica la interacción con la base de datos SQLite para operaciones CRUD
de la entidad Propiedad.
"""
import pytest
import sqlite3
from pathlib import Path

from tests.integration.test_database_manager import TestDatabaseManager
from src.infraestructura.persistencia.repositorio_propiedad_sqlite import RepositorioPropiedadSQLite
from src.dominio.entidades.propiedad import Propiedad


@pytest.fixture
def db_manager(tmp_path):
    """Crea un TestDatabaseManager con BD temporal."""
    db_file = tmp_path / "test_propiedad.db"
    db_manager = TestDatabaseManager(str(db_file))
    
    # Crear tablas necesarias
    with db_manager.obtener_conexion() as conn:
        # Tabla MUNICIPIOS (para FK)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS MUNICIPIOS (
                ID_MUNICIPIO INTEGER PRIMARY KEY AUTOINCREMENT,
                NOMBRE_MUNICIPIO TEXT NOT NULL
            )
        """)
        conn.execute("INSERT INTO MUNICIPIOS (NOMBRE_MUNICIPIO) VALUES ('Bogotá')")
        
        # Tabla PROPIEDADES
        conn.execute("""
            CREATE TABLE IF NOT EXISTS PROPIEDADES (
                ID_PROPIEDAD INTEGER PRIMARY KEY AUTOINCREMENT,
                MATRICULA_INMOBILIARIA TEXT NOT NULL UNIQUE,
                ID_MUNICIPIO INTEGER NOT NULL,
                DIRECCION_PROPIEDAD TEXT NOT NULL,
                TIPO_PROPIEDAD TEXT NOT NULL,
                DISPONIBILIDAD_PROPIEDAD INTEGER DEFAULT 1,
                AREA_M2 REAL,
                HABITACIONES INTEGER,
                BANO INTEGER,
                PARQUEADERO INTEGER,
                ESTRATO INTEGER,
                VALOR_ADMINISTRACION INTEGER,
                CANON_ARRENDAMIENTO_ESTIMADO INTEGER,
                VALOR_VENTA_PROPIEDAD INTEGER,
                COMISION_VENTA_PROPIEDAD INTEGER,
                OBSERVACIONES_PROPIEDAD TEXT,
                FECHA_INGRESO_PROPIEDAD TEXT,
                ESTADO_REGISTRO INTEGER DEFAULT 1,
                MOTIVO_INACTIVACION TEXT,
                CREATED_AT TEXT,
                CREATED_BY TEXT,
                UPDATED_AT TEXT,
                UPDATED_BY TEXT,
                FOREIGN KEY (ID_MUNICIPIO) REFERENCES MUNICIPIOS(ID_MUNICIPIO)
            )
        """)
        conn.commit()
    
    yield db_manager
    
    # Cleanup - cerrar conexión antes de eliminar archivo
    db_manager.cerrar_todas_conexiones()
    if db_file.exists():
        db_file.unlink()


@pytest.fixture
def repositorio(db_manager):
    """Crea una instancia del repositorio."""
    return RepositorioPropiedadSQLite(db_manager)


class TestRepositorioPropiedad:
    """Tests de integración para RepositorioPropiedadSQLite."""
    
    def test_crear_propiedad_basica(self, repositorio):
        """Test: Crear una propiedad con datos básicos."""
        propiedad = Propiedad(
            matricula_inmobiliaria="MAT-001-2024",
            id_municipio=1,
            direccion_propiedad="Calle 123 #45-67",
            tipo_propiedad="Apartamento"
        )
        
        propiedad_creada = repositorio.crear(propiedad, "TEST_USER")
        
        assert propiedad_creada.id_propiedad is not None
        assert propiedad_creada.id_propiedad > 0
        assert propiedad_creada.matricula_inmobiliaria == "MAT-001-2024"
        assert propiedad_creada.tipo_propiedad == "Apartamento"
    
    def test_crear_propiedad_completa(self, repositorio):
        """Test: Crear una propiedad con todos los datos."""
        propiedad = Propiedad(
            matricula_inmobiliaria="MAT-002-2024",
            id_municipio=1,
            direccion_propiedad="Carrera 50 #100-20",
            tipo_propiedad="Casa",
            disponibilidad_propiedad=1,
            area_m2=120.5,
            habitaciones=3,
            bano=2,
            parqueadero=1,
            estrato=4,
            valor_administracion=200000,
            canon_arrendamiento_estimado=2000000,
            valor_venta_propiedad=350000000,
            comision_venta_propiedad=10500000,
            observaciones_propiedad="Propiedad en excelente estado"
        )
        
        propiedad_creada = repositorio.crear(propiedad, "TEST_USER")
        
        assert propiedad_creada.id_propiedad is not None
        assert propiedad_creada.area_m2 == 120.5
        assert propiedad_creada.habitaciones == 3
        assert propiedad_creada.bano == 2
        assert propiedad_creada.parqueadero == 1
        assert propiedad_creada.estrato == 4
        assert propiedad_creada.canon_arrendamiento_estimado == 2000000
    
    def test_obtener_por_id(self, repositorio):
        """Test: Obtener una propiedad por su ID."""
        # Crear propiedad
        propiedad = Propiedad(
            matricula_inmobiliaria="MAT-003-2024",
            id_municipio=1,
            direccion_propiedad="Avenida 68 #50-30",
            tipo_propiedad="Apartamento"
        )
        propiedad_creada = repositorio.crear(propiedad, "TEST_USER")
        
        # Obtener por ID
        propiedad_obtenida = repositorio.obtener_por_id(propiedad_creada.id_propiedad)
        
        assert propiedad_obtenida is not None
        assert propiedad_obtenida.id_propiedad == propiedad_creada.id_propiedad
        assert propiedad_obtenida.matricula_inmobiliaria == "MAT-003-2024"
    
    def test_obtener_por_id_no_existe(self, repositorio):
        """Test: Obtener propiedad con ID inexistente retorna None."""
        propiedad = repositorio.obtener_por_id(99999)
        
        assert propiedad is None
    
    def test_obtener_por_matricula(self, repositorio):
        """Test: Obtener una propiedad por su matrícula."""
        # Crear propiedad
        propiedad = Propiedad(
            matricula_inmobiliaria="MAT-004-2024",
            id_municipio=1,
            direccion_propiedad="Calle 80 #10-20",
            tipo_propiedad="Local Comercial"
        )
        repositorio.crear(propiedad, "TEST_USER")
        
        # Obtener por matrícula
        propiedad_obtenida = repositorio.obtener_por_matricula("MAT-004-2024")
        
        assert propiedad_obtenida is not None
        assert propiedad_obtenida.matricula_inmobiliaria == "MAT-004-2024"
        assert propiedad_obtenida.tipo_propiedad == "Local Comercial"
    
    def test_obtener_por_matricula_no_existe(self, repositorio):
        """Test: Obtener propiedad con matrícula inexistente retorna None."""
        propiedad = repositorio.obtener_por_matricula("MAT-INEXISTENTE")
        
        assert propiedad is None
    
    def test_listar_disponibles(self, repositorio):
        """Test: Listar todas las propiedades disponibles."""
        # Crear varias propiedades
        prop1 = Propiedad(
            matricula_inmobiliaria="MAT-005-2024",
            id_municipio=1,
            direccion_propiedad="Calle 1",
            tipo_propiedad="Apartamento",
            disponibilidad_propiedad=1
        )
        prop2 = Propiedad(
            matricula_inmobiliaria="MAT-006-2024",
            id_municipio=1,
            direccion_propiedad="Calle 2",
            tipo_propiedad="Casa",
            disponibilidad_propiedad=1
        )
        prop3 = Propiedad(
            matricula_inmobiliaria="MAT-007-2024",
            id_municipio=1,
            direccion_propiedad="Calle 3",
            tipo_propiedad="Apartamento"
        )
        
        repositorio.crear(prop1, "TEST_USER")
        repositorio.crear(prop2, "TEST_USER")
        prop3_creada = repositorio.crear(prop3, "TEST_USER")
        
        # Cambiar disponibilidad de prop3 a no disponible
        prop3_creada.disponibilidad_propiedad = 0
        repositorio.actualizar(prop3_creada, "TEST_USER")
        
        # Listar disponibles
        disponibles = repositorio.listar_disponibles()
        
        assert len(disponibles) == 2
        assert all(p.disponibilidad_propiedad == 1 for p in disponibles)
        assert all(p.estado_registro == 1 for p in disponibles)
    
    def test_actualizar_propiedad(self, repositorio):
        """Test: Actualizar datos de una propiedad."""
        # Crear propiedad
        propiedad = Propiedad(
            matricula_inmobiliaria="MAT-008-2024",
            id_municipio=1,
            direccion_propiedad="Dirección Original",
            tipo_propiedad="Apartamento",
            canon_arrendamiento_estimado=1000000
        )
        propiedad_creada = repositorio.crear(propiedad, "TEST_USER")
        
        # Actualizar
        propiedad_creada.direccion_propiedad = "Dirección Actualizada"
        propiedad_creada.canon_arrendamiento_estimado = 1500000
        propiedad_creada.habitaciones = 3
        
        resultado = repositorio.actualizar(propiedad_creada, "TEST_UPDATER")
        
        assert resultado is True
        
        # Verificar cambios
        propiedad_verificada = repositorio.obtener_por_id(propiedad_creada.id_propiedad)
        assert propiedad_verificada.direccion_propiedad == "Dirección Actualizada"
        assert propiedad_verificada.canon_arrendamiento_estimado == 1500000
        assert propiedad_verificada.habitaciones == 3
    
    def test_cambiar_disponibilidad(self, repositorio):
        """Test: Cambiar disponibilidad de una propiedad."""
        # Crear propiedad disponible
        propiedad = Propiedad(
            matricula_inmobiliaria="MAT-009-2024",
            id_municipio=1,
            direccion_propiedad="Calle Test",
            tipo_propiedad="Apartamento",
            disponibilidad_propiedad=1
        )
        propiedad_creada = repositorio.crear(propiedad, "TEST_USER")
        
        # Cambiar a no disponible
        propiedad_creada.disponibilidad_propiedad = 0
        repositorio.actualizar(propiedad_creada, "TEST_USER")
        
        # Verificar que no aparece en disponibles
        disponibles = repositorio.listar_disponibles()
        assert not any(p.id_propiedad == propiedad_creada.id_propiedad for p in disponibles)
    
    def test_matricula_unica(self, repositorio):
        """Test: No se permite duplicar matrícula inmobiliaria."""
        # Crear primera propiedad
        prop1 = Propiedad(
            matricula_inmobiliaria="MAT-DUPLICADA",
            id_municipio=1,
            direccion_propiedad="Calle 1",
            tipo_propiedad="Apartamento"
        )
        repositorio.crear(prop1, "TEST_USER")
        
        # Intentar crear segunda propiedad con misma matrícula
        prop2 = Propiedad(
            matricula_inmobiliaria="MAT-DUPLICADA",
            id_municipio=1,
            direccion_propiedad="Calle 2",
            tipo_propiedad="Casa"
        )
        
        with pytest.raises(sqlite3.IntegrityError):
            repositorio.crear(prop2, "TEST_USER")
    
    def test_diferentes_tipos_propiedad(self, repositorio):
        """Test: Crear propiedades de diferentes tipos."""
        tipos = ["Apartamento", "Casa", "Local Comercial", "Bodega", "Oficina"]
        
        for i, tipo in enumerate(tipos):
            propiedad = Propiedad(
                matricula_inmobiliaria=f"MAT-TIPO-{i}",
                id_municipio=1,
                direccion_propiedad=f"Dirección {i}",
                tipo_propiedad=tipo
            )
            propiedad_creada = repositorio.crear(propiedad, "TEST_USER")
            assert propiedad_creada.tipo_propiedad == tipo
