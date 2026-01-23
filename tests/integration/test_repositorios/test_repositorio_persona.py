"""
Tests de integración para RepositorioPersonaSQLite.

Verifica la interacción con la base de datos SQLite para operaciones CRUD
de la entidad Persona.
"""
import pytest
import sqlite3
from pathlib import Path
from datetime import datetime

from tests.integration.test_database_manager import TestDatabaseManager
from src.infraestructura.persistencia.repositorio_persona_sqlite import RepositorioPersonaSQLite
from src.dominio.entidades.persona import Persona


@pytest.fixture
def db_manager(tmp_path):
    """Crea un TestDatabaseManager con BD temporal."""
    db_file = tmp_path / "test_persona.db"
    db_manager = TestDatabaseManager(str(db_file))
    
    # Crear tabla PERSONAS
    with db_manager.obtener_conexion() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS PERSONAS (
                ID_PERSONA INTEGER PRIMARY KEY AUTOINCREMENT,
                TIPO_DOCUMENTO TEXT,
                NUMERO_DOCUMENTO TEXT NOT NULL UNIQUE,
                NOMBRE_COMPLETO TEXT NOT NULL,
                TELEFONO_PRINCIPAL TEXT,
                CORREO_ELECTRONICO TEXT,
                DIRECCION_PRINCIPAL TEXT,
                ESTADO_REGISTRO INTEGER DEFAULT 1,
                MOTIVO_INACTIVACION TEXT,
                CREATED_AT TEXT,
                CREATED_BY TEXT,
                UPDATED_AT TEXT,
                UPDATED_BY TEXT
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
    return RepositorioPersonaSQLite(db_manager)


class TestRepositorioPersona:
    """Tests de integración para RepositorioPersonaSQLite."""
    
    def test_crear_persona_basica(self, repositorio):
        """Test: Crear una persona con datos básicos."""
        persona = Persona(
            tipo_documento="CC",
            numero_documento="1234567890",
            nombre_completo="Juan Pérez García"
        )
        
        persona_creada = repositorio.crear(persona, "TEST_USER")
        
        assert persona_creada.id_persona is not None
        assert persona_creada.id_persona > 0
        assert persona_creada.numero_documento == "1234567890"
        assert persona_creada.nombre_completo == "Juan Pérez García"
    
    def test_crear_persona_completa(self, repositorio):
        """Test: Crear una persona con todos los datos."""
        persona = Persona(
            tipo_documento="CC",
            numero_documento="9876543210",
            nombre_completo="María López Rodríguez",
            telefono_principal="3001234567",
            correo_electronico="maria@example.com",
            direccion_principal="Calle 123 #45-67"
        )
        
        persona_creada = repositorio.crear(persona, "TEST_USER")
        
        assert persona_creada.id_persona is not None
        assert persona_creada.telefono_principal == "3001234567"
        assert persona_creada.correo_electronico == "maria@example.com"
        assert persona_creada.direccion_principal == "Calle 123 #45-67"
    
    def test_obtener_por_id(self, repositorio):
        """Test: Obtener una persona por su ID."""
        # Crear persona
        persona = Persona(
            numero_documento="1111111111",
            nombre_completo="Test Usuario"
        )
        persona_creada = repositorio.crear(persona, "TEST_USER")
        
        # Obtener por ID
        persona_obtenida = repositorio.obtener_por_id(persona_creada.id_persona)
        
        assert persona_obtenida is not None
        assert persona_obtenida.id_persona == persona_creada.id_persona
        assert persona_obtenida.numero_documento == "1111111111"
        assert persona_obtenida.nombre_completo == "Test Usuario"
    
    def test_obtener_por_id_no_existe(self, repositorio):
        """Test: Obtener persona con ID inexistente retorna None."""
        persona = repositorio.obtener_por_id(99999)
        
        assert persona is None
    
    def test_obtener_por_documento(self, repositorio):
        """Test: Obtener una persona por su número de documento."""
        # Crear persona
        persona = Persona(
            numero_documento="2222222222",
            nombre_completo="Test Documento"
        )
        repositorio.crear(persona, "TEST_USER")
        
        # Obtener por documento
        persona_obtenida = repositorio.obtener_por_documento("2222222222")
        
        assert persona_obtenida is not None
        assert persona_obtenida.numero_documento == "2222222222"
        assert persona_obtenida.nombre_completo == "Test Documento"
    
    def test_obtener_por_documento_no_existe(self, repositorio):
        """Test: Obtener persona con documento inexistente retorna None."""
        persona = repositorio.obtener_por_documento("9999999999")
        
        assert persona is None
    
    def test_listar_activos(self, repositorio):
        """Test: Listar todas las personas activas."""
        # Crear varias personas
        persona1 = Persona(numero_documento="3333333333", nombre_completo="Persona 1")
        persona2 = Persona(numero_documento="4444444444", nombre_completo="Persona 2")
        persona3 = Persona(numero_documento="5555555555", nombre_completo="Persona 3")
        
        repositorio.crear(persona1, "TEST_USER")
        repositorio.crear(persona2, "TEST_USER")
        persona3_creada = repositorio.crear(persona3, "TEST_USER")
        
        # Inactivar persona3
        repositorio.inactivar(persona3_creada.id_persona, "Test", "TEST_USER")
        
        # Listar activos
        activos = repositorio.listar_activos()
        
        assert len(activos) == 2
        assert all(p.estado_registro == 1 for p in activos)
    
    def test_actualizar_persona(self, repositorio):
        """Test: Actualizar datos de una persona."""
        # Crear persona
        persona = Persona(
            numero_documento="6666666666",
            nombre_completo="Nombre Original",
            telefono_principal="3001111111"
        )
        persona_creada = repositorio.crear(persona, "TEST_USER")
        
        # Actualizar
        persona_creada.nombre_completo = "Nombre Actualizado"
        persona_creada.telefono_principal = "3002222222"
        persona_creada.correo_electronico = "nuevo@example.com"
        
        resultado = repositorio.actualizar(persona_creada, "TEST_UPDATER")
        
        assert resultado is True
        
        # Verificar cambios
        persona_verificada = repositorio.obtener_por_id(persona_creada.id_persona)
        assert persona_verificada.nombre_completo == "Nombre Actualizado"
        assert persona_verificada.telefono_principal == "3002222222"
        assert persona_verificada.correo_electronico == "nuevo@example.com"
    
    def test_inactivar_persona(self, repositorio):
        """Test: Inactivar una persona (soft delete)."""
        # Crear persona
        persona = Persona(
            numero_documento="7777777777",
            nombre_completo="Persona a Inactivar"
        )
        persona_creada = repositorio.crear(persona, "TEST_USER")
        
        # Inactivar
        resultado = repositorio.inactivar(
            persona_creada.id_persona,
            "Duplicado",
            "TEST_ADMIN"
        )
        
        assert resultado is True
        
        # Verificar inactivación
        persona_verificada = repositorio.obtener_por_id(persona_creada.id_persona)
        assert persona_verificada.estado_registro == 0
        assert persona_verificada.motivo_inactivacion == "Duplicado"
        
        # Verificar que no aparece en listado de activos
        activos = repositorio.listar_activos()
        assert not any(p.id_persona == persona_creada.id_persona for p in activos)
    
    def test_documento_unico(self, repositorio, db_manager):
        """Test: No se permite duplicar número de documento."""
        # Crear primera persona
        persona1 = Persona(
            numero_documento="8888888888",
            nombre_completo="Primera Persona"
        )
        repositorio.crear(persona1, "TEST_USER")
        
        # Intentar crear segunda persona con mismo documento
        persona2 = Persona(
            numero_documento="8888888888",
            nombre_completo="Segunda Persona"
        )
        
        with pytest.raises(sqlite3.IntegrityError):
            repositorio.crear(persona2, "TEST_USER")
