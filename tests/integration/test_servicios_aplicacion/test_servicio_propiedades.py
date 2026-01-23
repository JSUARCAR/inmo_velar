"""
Tests de integración para ServicioPropiedades.

Verifica la lógica de negocio del servicio de propiedades incluyendo
validaciones, filtros y operaciones CRUD completas.
"""
import pytest
import sqlite3

from tests.integration.test_database_manager import TestDatabaseManager
from src.aplicacion.servicios.servicio_propiedades import ServicioPropiedades


@pytest.fixture
def db_manager(tmp_path):
    """Crea un TestDatabaseManager con BD temporal y esquema completo."""
    db_file = tmp_path / "test_servicio_propiedades.db"
    db_manager = TestDatabaseManager(str(db_file))
    
    # Crear tablas necesarias
    with db_manager.obtener_conexion() as conn:
        # Tabla MUNICIPIOS
        conn.execute("""
            CREATE TABLE IF NOT EXISTS MUNICIPIOS (
                ID_MUNICIPIO INTEGER PRIMARY KEY AUTOINCREMENT,
                NOMBRE_MUNICIPIO TEXT NOT NULL
            )
        """)
        conn.execute("INSERT INTO MUNICIPIOS (NOMBRE_MUNICIPIO) VALUES ('Bogotá')")
        conn.execute("INSERT INTO MUNICIPIOS (NOMBRE_MUNICIPIO) VALUES ('Medellín')")
        
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
    
    # Cleanup
    db_manager.cerrar_todas_conexiones()
    if db_file.exists():
        db_file.unlink()


@pytest.fixture
def servicio(db_manager):
    """Crea una instancia del servicio."""
    return ServicioPropiedades(db_manager)


class TestServicioPropiedades:
    """Tests de integración para ServicioPropiedades."""
    
    def test_crear_propiedad_basica(self, servicio):
        """Test: Crear una propiedad con datos básicos."""
        datos = {
            "matricula_inmobiliaria": "MAT-001-2024",
            "id_municipio": 1,
            "direccion_propiedad": "Calle 123 #45-67",
            "tipo_propiedad": "Apartamento",
            "area_m2": 85.5
        }
        
        propiedad = servicio.crear_propiedad(datos, "TEST_USER")
        
        assert propiedad.id_propiedad is not None
        assert propiedad.matricula_inmobiliaria == "MAT-001-2024"
        assert propiedad.tipo_propiedad == "Apartamento"
        assert propiedad.area_m2 == 85.5
    
    def test_crear_propiedad_completa(self, servicio):
        """Test: Crear una propiedad con todos los datos."""
        datos = {
            "matricula_inmobiliaria": "MAT-002-2024",
            "id_municipio": 1,
            "direccion_propiedad": "Carrera 50 #100-20",
            "tipo_propiedad": "Casa",
            "area_m2": 120.5,
            "habitaciones": 3,
            "bano": 2,
            "parqueadero": 1,
            "estrato": 4,
            "valor_administracion": 200000,
            "canon_arrendamiento_estimado": 2000000,
            "valor_venta_propiedad": 350000000,
            "comision_venta_propiedad": 10500000,
            "observaciones_propiedad": "Excelente estado"
        }
        
        propiedad = servicio.crear_propiedad(datos, "TEST_USER")
        
        assert propiedad.habitaciones == 3
        assert propiedad.bano == 2
        assert propiedad.estrato == 4
        assert propiedad.canon_arrendamiento_estimado == 2000000
    
    def test_no_permite_matricula_duplicada(self, servicio):
        """Test: No se permite crear propiedad con matrícula duplicada."""
        datos = {
            "matricula_inmobiliaria": "MAT-DUP",
            "id_municipio": 1,
            "direccion_propiedad": "Calle 1",
            "tipo_propiedad": "Apartamento",
            "area_m2": 50
        }
        
        servicio.crear_propiedad(datos, "TEST_USER")
        
        with pytest.raises(ValueError, match="Ya existe una propiedad con matrícula"):
            servicio.crear_propiedad(datos, "TEST_USER")
    
    def test_validar_tipo_propiedad_invalido(self, servicio):
        """Test: Validar que el tipo de propiedad sea válido."""
        datos = {
            "matricula_inmobiliaria": "MAT-003",
            "id_municipio": 1,
            "direccion_propiedad": "Calle 1",
            "tipo_propiedad": "TipoInvalido",
            "area_m2": 50
        }
        
        with pytest.raises(ValueError, match="Tipo de propiedad inválido"):
            servicio.crear_propiedad(datos, "TEST_USER")
    
    def test_validar_area_positiva(self, servicio):
        """Test: El área debe ser mayor a 0."""
        datos = {
            "matricula_inmobiliaria": "MAT-004",
            "id_municipio": 1,
            "direccion_propiedad": "Calle 1",
            "tipo_propiedad": "Apartamento",
            "area_m2": 0
        }
        
        with pytest.raises(ValueError, match="El área debe ser mayor a 0"):
            servicio.crear_propiedad(datos, "TEST_USER")
    
    def test_validar_estrato_valido(self, servicio):
        """Test: El estrato debe estar entre 1 y 6."""
        datos = {
            "matricula_inmobiliaria": "MAT-005",
            "id_municipio": 1,
            "direccion_propiedad": "Calle 1",
            "tipo_propiedad": "Apartamento",
            "area_m2": 50,
            "estrato": 7
        }
        
        with pytest.raises(ValueError, match="El estrato debe estar entre 1 y 6"):
            servicio.crear_propiedad(datos, "TEST_USER")
    
    def test_listar_propiedades_todas(self, servicio):
        """Test: Listar todas las propiedades."""
        # Crear varias propiedades
        for i in range(3):
            datos = {
                "matricula_inmobiliaria": f"MAT-LIST-{i}",
                "id_municipio": 1,
                "direccion_propiedad": f"Calle {i}",
                "tipo_propiedad": "Apartamento",
                "area_m2": 50 + i
            }
            servicio.crear_propiedad(datos, "TEST_USER")
        
        propiedades = servicio.listar_propiedades()
        
        assert len(propiedades) >= 3
    
    def test_listar_propiedades_por_tipo(self, servicio):
        """Test: Filtrar propiedades por tipo."""
        # Crear propiedades de diferentes tipos
        servicio.crear_propiedad({
            "matricula_inmobiliaria": "MAT-TIPO-1",
            "id_municipio": 1,
            "direccion_propiedad": "Calle 1",
            "tipo_propiedad": "Casa",
            "area_m2": 100
        }, "TEST_USER")
        
        servicio.crear_propiedad({
            "matricula_inmobiliaria": "MAT-TIPO-2",
            "id_municipio": 1,
            "direccion_propiedad": "Calle 2",
            "tipo_propiedad": "Apartamento",
            "area_m2": 50
        }, "TEST_USER")
        
        casas = servicio.listar_propiedades(filtro_tipo="Casa")
        
        assert len(casas) >= 1
        assert all(p.tipo_propiedad == "Casa" for p in casas)
    
    def test_listar_propiedades_disponibles(self, servicio):
        """Test: Filtrar propiedades disponibles."""
        # Crear propiedad disponible
        prop1 = servicio.crear_propiedad({
            "matricula_inmobiliaria": "MAT-DISP-1",
            "id_municipio": 1,
            "direccion_propiedad": "Calle 1",
            "tipo_propiedad": "Apartamento",
            "area_m2": 50,
            "disponibilidad_propiedad": 1
        }, "TEST_USER")
        
        # Crear propiedad no disponible
        prop2 = servicio.crear_propiedad({
            "matricula_inmobiliaria": "MAT-DISP-2",
            "id_municipio": 1,
            "direccion_propiedad": "Calle 2",
            "tipo_propiedad": "Casa",
            "area_m2": 100
        }, "TEST_USER")
        
        servicio.cambiar_disponibilidad(prop2.id_propiedad, 0, "TEST_USER")
        
        disponibles = servicio.listar_propiedades(filtro_disponibilidad=1)
        
        assert any(p.id_propiedad == prop1.id_propiedad for p in disponibles)
        assert not any(p.id_propiedad == prop2.id_propiedad for p in disponibles)
    
    def test_buscar_por_matricula(self, servicio):
        """Test: Buscar propiedad por matrícula."""
        datos = {
            "matricula_inmobiliaria": "MAT-BUSCAR",
            "id_municipio": 1,
            "direccion_propiedad": "Calle Test",
            "tipo_propiedad": "Apartamento",
            "area_m2": 50
        }
        
        servicio.crear_propiedad(datos, "TEST_USER")
        
        propiedad = servicio.buscar_por_matricula("MAT-BUSCAR")
        
        assert propiedad is not None
        assert propiedad.matricula_inmobiliaria == "MAT-BUSCAR"
    
    def test_actualizar_propiedad(self, servicio):
        """Test: Actualizar datos de una propiedad."""
        # Crear propiedad
        propiedad = servicio.crear_propiedad({
            "matricula_inmobiliaria": "MAT-UPDATE",
            "id_municipio": 1,
            "direccion_propiedad": "Dirección Original",
            "tipo_propiedad": "Apartamento",
            "area_m2": 50,
            "canon_arrendamiento_estimado": 1000000
        }, "TEST_USER")
        
        # Actualizar
        datos_actualizados = {
            "direccion_propiedad": "Dirección Actualizada",
            "canon_arrendamiento_estimado": 1500000,
            "habitaciones": 3
        }
        
        propiedad_actualizada = servicio.actualizar_propiedad(
            propiedad.id_propiedad,
            datos_actualizados,
            "TEST_UPDATER"
        )
        
        assert propiedad_actualizada.direccion_propiedad == "Dirección Actualizada"
        assert propiedad_actualizada.canon_arrendamiento_estimado == 1500000
        assert propiedad_actualizada.habitaciones == 3
    
    def test_cambiar_disponibilidad(self, servicio):
        """Test: Cambiar disponibilidad de propiedad."""
        propiedad = servicio.crear_propiedad({
            "matricula_inmobiliaria": "MAT-CAMBIO",
            "id_municipio": 1,
            "direccion_propiedad": "Calle Test",
            "tipo_propiedad": "Apartamento",
            "area_m2": 50,
            "disponibilidad_propiedad": 1
        }, "TEST_USER")
        
        # Cambiar a no disponible
        resultado = servicio.cambiar_disponibilidad(propiedad.id_propiedad, 0, "TEST_USER")
        
        assert resultado is True
        
        # Verificar cambio
        propiedad_actualizada = servicio.obtener_propiedad(propiedad.id_propiedad)
        assert propiedad_actualizada.disponibilidad_propiedad == 0
    
    def test_desactivar_propiedad(self, servicio):
        """Test: Desactivar propiedad (soft delete)."""
        propiedad = servicio.crear_propiedad({
            "matricula_inmobiliaria": "MAT-DESACT",
            "id_municipio": 1,
            "direccion_propiedad": "Calle Test",
            "tipo_propiedad": "Apartamento",
            "area_m2": 50
        }, "TEST_USER")
        
        resultado = servicio.desactivar_propiedad(
            propiedad.id_propiedad,
            "Vendida",
            "TEST_ADMIN"
        )
        
        assert resultado is True
        
        # Verificar que no aparece en listado activo
        activas = servicio.listar_propiedades(solo_activas=True)
        assert not any(p.id_propiedad == propiedad.id_propiedad for p in activas)
    
    def test_obtener_tipos_propiedad(self, servicio):
        """Test: Obtener catálogo de tipos de propiedad."""
        tipos = servicio.obtener_tipos_propiedad()
        
        assert "Casa" in tipos
        assert "Apartamento" in tipos
        assert "Local Comercial" in tipos
        assert len(tipos) > 0
    
    def test_obtener_municipios_disponibles(self, servicio):
        """Test: Obtener lista de municipios."""
        municipios = servicio.obtener_municipios_disponibles()
        
        assert len(municipios) >= 2
        assert any(m["nombre"] == "Bogotá" for m in municipios)
        assert any(m["nombre"] == "Medellín" for m in municipios)
