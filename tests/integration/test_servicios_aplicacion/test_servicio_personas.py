"""
Tests de integración para ServicioPersonas.

Verifica la lógica de negocio del servicio de personas incluyendo
gestión de roles múltiples, validaciones, filtros y operaciones CRUD completas.
"""
import pytest
import sqlite3

from tests.integration.test_database_manager import TestDatabaseManager
from src.aplicacion.servicios.servicio_personas import ServicioPersonas


@pytest.fixture
def db_manager(tmp_path):
    """Crea un TestDatabaseManager con BD temporal y esquema completo."""
    db_file = tmp_path / "test_servicio_personas.db"
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
        
        # Tabla PERSONAS
        conn.execute("""
            CREATE TABLE IF NOT EXISTS PERSONAS (
                ID_PERSONA INTEGER PRIMARY KEY AUTOINCREMENT,
                TIPO_DOCUMENTO TEXT NOT NULL,
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
        
        # Tabla ASESORES
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ASESORES (
                ID_ASESOR INTEGER PRIMARY KEY AUTOINCREMENT,
                ID_PERSONA INTEGER NOT NULL,
                ID_USUARIO INTEGER,
                FECHA_INGRESO TEXT,
                COMISION_PORCENTAJE_ARRIENDO INTEGER DEFAULT 0,
                COMISION_PORCENTAJE_VENTA INTEGER DEFAULT 0,
                ESTADO INTEGER DEFAULT 1,
                MOTIVO_INACTIVACION TEXT,
                ESTADO_REGISTRO INTEGER DEFAULT 1,
                CREATED_AT TEXT,
                CREATED_BY TEXT,
                UPDATED_AT TEXT,
                UPDATED_BY TEXT,
                FOREIGN KEY (ID_PERSONA) REFERENCES PERSONAS(ID_PERSONA)
            )
        """)
        
        # Tabla PROPIETARIOS
        conn.execute("""
            CREATE TABLE IF NOT EXISTS PROPIETARIOS (
                ID_PROPIETARIO INTEGER PRIMARY KEY AUTOINCREMENT,
                ID_PERSONA INTEGER NOT NULL,
                BANCO_PROPIETARIO TEXT,
                NUMERO_CUENTA_PROPIETARIO TEXT,
                TIPO_CUENTA TEXT,
                OBSERVACIONES_PROPIETARIO TEXT,
                ESTADO_PROPIETARIO INTEGER DEFAULT 1,
                FECHA_INGRESO_PROPIETARIO TEXT,
                MOTIVO_INACTIVACION TEXT,
                CREATED_AT TEXT,
                CREATED_BY TEXT,
                UPDATED_AT TEXT,
                UPDATED_BY TEXT,
                FOREIGN KEY (ID_PERSONA) REFERENCES PERSONAS(ID_PERSONA)
            )
        """)
        
        # Tabla ARRENDATARIOS
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ARRENDATARIOS (
                ID_ARRENDATARIO INTEGER PRIMARY KEY AUTOINCREMENT,
                ID_PERSONA INTEGER NOT NULL,
                DIRECCION_REFERENCIA TEXT,
                CODIGO_APROBACION_SEGURO TEXT,
                ID_SEGURO INTEGER,
                FECHA_INGRESO_ARRENDATARIO TEXT,
                ESTADO_ARRENDATARIO INTEGER DEFAULT 1,
                MOTIVO_INACTIVACION TEXT,
                ESTADO_REGISTRO INTEGER DEFAULT 1,
                CREATED_AT TEXT,
                CREATED_BY TEXT,
                UPDATED_AT TEXT,
                UPDATED_BY TEXT,
                FOREIGN KEY (ID_PERSONA) REFERENCES PERSONAS(ID_PERSONA)
            )
        """)
        
        # Tabla CODEUDORES
        conn.execute("""
            CREATE TABLE IF NOT EXISTS CODEUDORES (
                ID_CODEUDOR INTEGER PRIMARY KEY AUTOINCREMENT,
                ID_PERSONA INTEGER NOT NULL,
                FECHA_INGRESO_CODEUDOR TEXT,
                ESTADO_REGISTRO INTEGER DEFAULT 1,
                CREATED_AT TEXT,
                CREATED_BY TEXT,
                UPDATED_AT TEXT,
                UPDATED_BY TEXT,
                FOREIGN KEY (ID_PERSONA) REFERENCES PERSONAS(ID_PERSONA)
            )
        """)
        
        # Tabla PROVEEDORES
        conn.execute("""
            CREATE TABLE IF NOT EXISTS PROVEEDORES (
                ID_PROVEEDOR INTEGER PRIMARY KEY AUTOINCREMENT,
                ID_PERSONA INTEGER NOT NULL,
                ESPECIALIDAD TEXT,
                OBSERVACIONES TEXT,
                ESTADO_REGISTRO INTEGER DEFAULT 1,
                CREATED_AT TEXT,
                CREATED_BY TEXT,
                UPDATED_AT TEXT,
                UPDATED_BY TEXT,
                FOREIGN KEY (ID_PERSONA) REFERENCES PERSONAS(ID_PERSONA)
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
    return ServicioPersonas(db_manager)


class TestServicioPersonas:
    """Tests de integración para ServicioPersonas."""
    
    def test_crear_persona_sin_roles(self, servicio):
        """Test: Crear una persona sin asignar roles."""
        datos = {
            "tipo_documento": "CC",
            "numero_documento": "1234567890",
            "nombre_completo": "Juan Pérez",
            "telefono_principal": "3001234567",
            "correo_electronico": "juan@example.com"
        }
        
        persona_con_roles = servicio.crear_persona_con_roles(
            datos_persona=datos,
            roles=[],
            usuario_sistema="TEST_USER"
        )
        
        assert persona_con_roles.persona.id_persona is not None
        assert persona_con_roles.persona.numero_documento == "1234567890"
        assert persona_con_roles.persona.nombre_completo == "Juan Pérez"
        assert len(persona_con_roles.roles) == 0
    
    def test_crear_persona_con_un_rol(self, servicio):
        """Test: Crear una persona con un solo rol (Propietario)."""
        datos = {
            "tipo_documento": "CC",
            "numero_documento": "9876543210",
            "nombre_completo": "María González",
            "telefono_principal": "3109876543"
        }
        
        persona_con_roles = servicio.crear_persona_con_roles(
            datos_persona=datos,
            roles=["Propietario"],
            usuario_sistema="TEST_USER"
        )
        
        assert persona_con_roles.persona.id_persona is not None
        assert "Propietario" in persona_con_roles.roles
        assert len(persona_con_roles.roles) == 1
    
    def test_crear_persona_con_multiples_roles(self, servicio):
        """Test: Crear una persona con múltiples roles."""
        datos = {
            "tipo_documento": "CC",
            "numero_documento": "5555555555",
            "nombre_completo": "Carlos Rodríguez",
            "telefono_principal": "3205555555"
        }
        
        persona_con_roles = servicio.crear_persona_con_roles(
            datos_persona=datos,
            roles=["Propietario", "Asesor"],
            datos_extras={
                "Asesor": {
                    "comision_porcentaje_arriendo": 12,
                    "comision_porcentaje_venta": 4
                }
            },
            usuario_sistema="TEST_USER"
        )
        
        assert persona_con_roles.persona.id_persona is not None
        assert "Propietario" in persona_con_roles.roles
        assert "Asesor" in persona_con_roles.roles
        assert len(persona_con_roles.roles) == 2
        
        # Verificar datos extra del asesor
        assert "Asesor" in persona_con_roles.datos_roles
        asesor = persona_con_roles.datos_roles["Asesor"]
        assert asesor.comision_porcentaje_arriendo == 12
        assert asesor.comision_porcentaje_venta == 4
    
    def test_actualizar_datos_basicos_persona(self, servicio):
        """Test: Actualizar datos básicos de una persona."""
        # Crear persona
        datos = {
            "tipo_documento": "CC",
            "numero_documento": "1111111111",
            "nombre_completo": "Pedro López",
            "telefono_principal": "3001111111"
        }
        
        persona_con_roles = servicio.crear_persona_con_roles(
            datos_persona=datos,
            roles=["Arrendatario"],
            usuario_sistema="TEST_USER"
        )
        
        # Actualizar
        datos_actualizados = {
            "telefono_principal": "3009999999",
            "correo_electronico": "pedro.nuevo@example.com",
            "direccion_principal": "Calle 100 #50-20"
        }
        
        persona_actualizada = servicio.actualizar_persona(
            id_persona=persona_con_roles.persona.id_persona,
            datos=datos_actualizados,
            usuario_sistema="TEST_UPDATER"
        )
        
        assert persona_actualizada.persona.telefono_principal == "3009999999"
        assert persona_actualizada.persona.correo_electronico == "pedro.nuevo@example.com"
        assert persona_actualizada.persona.direccion_principal == "Calle 100 #50-20"
    
    def test_buscar_por_documento(self, servicio):
        """Test: Buscar persona por número de documento."""
        datos = {
            "tipo_documento": "CC",
            "numero_documento": "2222222222",
            "nombre_completo": "Ana Martínez",
            "telefono_principal": "3002222222"
        }
        
        servicio.crear_persona_con_roles(
            datos_persona=datos,
            roles=["Propietario"],
            usuario_sistema="TEST_USER"
        )
        
        persona_encontrada = servicio.buscar_por_documento("2222222222")
        
        assert persona_encontrada is not None
        assert persona_encontrada.persona.numero_documento == "2222222222"
        assert persona_encontrada.persona.nombre_completo == "Ana Martínez"
    
    def test_asignar_rol_a_persona_existente(self, servicio):
        """Test: Asignar un nuevo rol a una persona existente."""
        # Crear persona con un rol
        datos = {
            "tipo_documento": "CC",
            "numero_documento": "3333333333",
            "nombre_completo": "Luis Hernández",
            "telefono_principal": "3003333333"
        }
        
        persona_con_roles = servicio.crear_persona_con_roles(
            datos_persona=datos,
            roles=["Propietario"],
            usuario_sistema="TEST_USER"
        )
        
        # Asignar nuevo rol
        servicio.asignar_rol(
            id_persona=persona_con_roles.persona.id_persona,
            nombre_rol="Arrendatario",
            usuario_sistema="TEST_USER"
        )
        
        # Verificar
        persona_actualizada = servicio.obtener_persona_completa(
            persona_con_roles.persona.id_persona
        )
        
        assert "Propietario" in persona_actualizada.roles
        assert "Arrendatario" in persona_actualizada.roles
        assert len(persona_actualizada.roles) == 2
    
    def test_asignar_rol_con_datos_extra(self, servicio):
        """Test: Asignar rol con datos adicionales (Asesor con comisiones)."""
        # Crear persona
        datos = {
            "tipo_documento": "CC",
            "numero_documento": "4444444444",
            "nombre_completo": "Sandra Ramírez",
            "telefono_principal": "3004444444"
        }
        
        persona_con_roles = servicio.crear_persona_con_roles(
            datos_persona=datos,
            roles=[],
            usuario_sistema="TEST_USER"
        )
        
        # Asignar rol Asesor con datos extra
        servicio.asignar_rol(
            id_persona=persona_con_roles.persona.id_persona,
            nombre_rol="Asesor",
            datos_extra={
                "comision_porcentaje_arriendo": 15,
                "comision_porcentaje_venta": 5
            },
            usuario_sistema="TEST_USER"
        )
        
        # Verificar
        persona_actualizada = servicio.obtener_persona_completa(
            persona_con_roles.persona.id_persona
        )
        
        assert "Asesor" in persona_actualizada.roles
        asesor = persona_actualizada.datos_roles["Asesor"]
        assert asesor.comision_porcentaje_arriendo == 15
        assert asesor.comision_porcentaje_venta == 5
    
    def test_remover_rol_de_persona(self, servicio):
        """Test: Remover un rol de una persona con múltiples roles."""
        # Crear persona con múltiples roles
        datos = {
            "tipo_documento": "CC",
            "numero_documento": "6666666666",
            "nombre_completo": "Jorge Vargas",
            "telefono_principal": "3006666666"
        }
        
        persona_con_roles = servicio.crear_persona_con_roles(
            datos_persona=datos,
            roles=["Propietario", "Asesor", "Arrendatario"],
            usuario_sistema="TEST_USER"
        )
        
        # Remover un rol
        servicio.remover_rol(
            id_persona=persona_con_roles.persona.id_persona,
            nombre_rol="Arrendatario"
        )
        
        # Verificar
        persona_actualizada = servicio.obtener_persona_completa(
            persona_con_roles.persona.id_persona
        )
        
        assert "Propietario" in persona_actualizada.roles
        assert "Asesor" in persona_actualizada.roles
        assert "Arrendatario" not in persona_actualizada.roles
        assert len(persona_actualizada.roles) == 2
    
    def test_no_permite_remover_ultimo_rol(self, servicio):
        """Test: No se permite remover el último rol de una persona."""
        # Crear persona con un solo rol
        datos = {
            "tipo_documento": "CC",
            "numero_documento": "7777777777",
            "nombre_completo": "Diana Castro",
            "telefono_principal": "3007777777"
        }
        
        persona_con_roles = servicio.crear_persona_con_roles(
            datos_persona=datos,
            roles=["Propietario"],
            usuario_sistema="TEST_USER"
        )
        
        # Intentar remover el único rol
        with pytest.raises(ValueError, match="No se puede remover el último rol"):
            servicio.remover_rol(
                id_persona=persona_con_roles.persona.id_persona,
                nombre_rol="Propietario"
            )
    
    def test_listar_todas_las_personas(self, servicio):
        """Test: Listar todas las personas activas."""
        # Crear varias personas
        for i in range(3):
            datos = {
                "tipo_documento": "CC",
                "numero_documento": f"800000000{i}",
                "nombre_completo": f"Persona{i} Test",
                "telefono_principal": f"30080000{i}"
            }
            servicio.crear_persona_con_roles(
                datos_persona=datos,
                roles=["Propietario"],
                usuario_sistema="TEST_USER"
            )
        
        personas = servicio.listar_personas()
        
        assert len(personas) >= 3
    
    def test_listar_personas_por_rol(self, servicio):
        """Test: Filtrar personas por rol específico."""
        # Crear personas con diferentes roles
        servicio.crear_persona_con_roles(
            datos_persona={
                "tipo_documento": "CC",
                "numero_documento": "9000000001",
                "nombre_completo": "Propietario1 Test",
                "telefono_principal": "3009000001"
            },
            roles=["Propietario"],
            usuario_sistema="TEST_USER"
        )
        
        servicio.crear_persona_con_roles(
            datos_persona={
                "tipo_documento": "CC",
                "numero_documento": "9000000002",
                "nombre_completo": "Asesor1 Test",
                "telefono_principal": "3009000002"
            },
            roles=["Asesor"],
            usuario_sistema="TEST_USER"
        )
        
        # Filtrar por Asesor
        asesores = servicio.listar_personas(filtro_rol="Asesor")
        
        assert len(asesores) >= 1
        assert all("Asesor" in p.roles for p in asesores)
    
    def test_buscar_personas_por_nombre(self, servicio):
        """Test: Buscar personas por nombre o apellido."""
        datos = {
            "tipo_documento": "CC",
            "numero_documento": "9100000001",
            "nombre_completo": "Búsqueda Especial",
            "telefono_principal": "3009100001"
        }
        
        servicio.crear_persona_con_roles(
            datos_persona=datos,
            roles=["Propietario"],
            usuario_sistema="TEST_USER"
        )
        
        # Buscar por nombre
        resultados = servicio.listar_personas(busqueda="Búsqueda")
        
        assert len(resultados) >= 1
        assert any("Búsqueda" in p.persona.nombre_completo for p in resultados)
    
    def test_listar_solo_personas_activas(self, servicio):
        """Test: Listar solo personas activas (excluir inactivas)."""
        # Crear persona activa
        persona1 = servicio.crear_persona_con_roles(
            datos_persona={
                "tipo_documento": "CC",
                "numero_documento": "9200000001",
                "nombre_completo": "Activo Test",
                "telefono_principal": "3009200001"
            },
            roles=["Propietario"],
            usuario_sistema="TEST_USER"
        )
        
        # Crear persona y desactivarla
        persona2 = servicio.crear_persona_con_roles(
            datos_persona={
                "tipo_documento": "CC",
                "numero_documento": "9200000002",
                "nombre_completo": "Inactivo Test",
                "telefono_principal": "3009200002"
            },
            roles=["Propietario"],
            usuario_sistema="TEST_USER"
        )
        
        servicio.desactivar_persona(
            id_persona=persona2.persona.id_persona,
            motivo="Test de inactivación",
            usuario_sistema="TEST_USER"
        )
        
        # Listar solo activas
        activas = servicio.listar_personas(solo_activos=True)
        
        assert any(p.persona.id_persona == persona1.persona.id_persona for p in activas)
        assert not any(p.persona.id_persona == persona2.persona.id_persona for p in activas)
    
    def test_desactivar_persona(self, servicio):
        """Test: Desactivar persona (soft delete)."""
        persona = servicio.crear_persona_con_roles(
            datos_persona={
                "tipo_documento": "CC",
                "numero_documento": "9300000001",
                "nombre_completo": "Desactivar Test",
                "telefono_principal": "3009300001"
            },
            roles=["Propietario"],
            usuario_sistema="TEST_USER"
        )
        
        resultado = servicio.desactivar_persona(
            id_persona=persona.persona.id_persona,
            motivo="Ya no es cliente",
            usuario_sistema="TEST_ADMIN"
        )
        
        assert resultado is True
        
        # Verificar que está inactiva
        persona_actualizada = servicio.obtener_persona_completa(persona.persona.id_persona)
        assert persona_actualizada.persona.estado_registro == 0
        assert persona_actualizada.persona.motivo_inactivacion == "Ya no es cliente"
    
    def test_activar_persona(self, servicio):
        """Test: Reactivar una persona inactiva."""
        # Crear y desactivar persona
        persona = servicio.crear_persona_con_roles(
            datos_persona={
                "tipo_documento": "CC",
                "numero_documento": "9400000001",
                "nombre_completo": "Reactivar Test",
                "telefono_principal": "3009400001"
            },
            roles=["Propietario"],
            usuario_sistema="TEST_USER"
        )
        
        servicio.desactivar_persona(
            id_persona=persona.persona.id_persona,
            motivo="Test",
            usuario_sistema="TEST_USER"
        )
        
        # Reactivar
        resultado = servicio.activar_persona(
            id_persona=persona.persona.id_persona,
            usuario_sistema="TEST_ADMIN"
        )
        
        assert resultado is True
        
        # Verificar que está activa
        persona_actualizada = servicio.obtener_persona_completa(persona.persona.id_persona)
        assert persona_actualizada.persona.estado_registro == 1
    
    def test_personas_inactivas_no_aparecen_en_listado(self, servicio):
        """Test: Las personas inactivas no aparecen en el listado por defecto."""
        # Crear persona y desactivarla
        persona = servicio.crear_persona_con_roles(
            datos_persona={
                "tipo_documento": "CC",
                "numero_documento": "9500000001",
                "nombre_completo": "NoListar Test",
                "telefono_principal": "3009500001"
            },
            roles=["Propietario"],
            usuario_sistema="TEST_USER"
        )
        
        servicio.desactivar_persona(
            id_persona=persona.persona.id_persona,
            motivo="Test",
            usuario_sistema="TEST_USER"
        )
        
        # Listar (por defecto solo activas)
        personas = servicio.listar_personas()
        
        assert not any(p.persona.id_persona == persona.persona.id_persona for p in personas)
    
    def test_no_permite_documento_duplicado(self, servicio):
        """Test: No se permite crear persona con documento duplicado."""
        datos = {
            "tipo_documento": "CC",
            "numero_documento": "9600000001",
            "nombre_completo": "Duplicado Test",
            "telefono_principal": "3009600001"
        }
        
        # Crear primera persona
        servicio.crear_persona_con_roles(
            datos_persona=datos,
            roles=["Propietario"],
            usuario_sistema="TEST_USER"
        )
        
        # Intentar crear segunda persona con mismo documento
        with pytest.raises(Exception):  # Puede ser ValueError o sqlite3.IntegrityError
            servicio.crear_persona_con_roles(
                datos_persona=datos,
                roles=["Arrendatario"],
                usuario_sistema="TEST_USER"
            )
    
    def test_obtener_persona_completa_con_roles(self, servicio):
        """Test: Obtener persona completa incluye todos los datos de roles."""
        # Crear persona con múltiples roles
        persona = servicio.crear_persona_con_roles(
            datos_persona={
                "tipo_documento": "CC",
                "numero_documento": "9700000001",
                "nombre_completo": "Completo Test",
                "telefono_principal": "3009700001",
                "correo_electronico": "completo@test.com"
            },
            roles=["Propietario", "Asesor"],
            datos_extras={
                "Asesor": {
                    "comision_arrendamiento": 10.0,
                    "comision_venta": 3.0
                }
            },
            usuario_sistema="TEST_USER"
        )
        
        # Obtener persona completa
        persona_completa = servicio.obtener_persona_completa(persona.persona.id_persona)
        
        # Verificar DTO PersonaConRoles
        assert persona_completa is not None
        assert persona_completa.nombre_completo == "Completo Test"
        assert persona_completa.numero_documento == "9700000001"
        assert persona_completa.telefono_principal == "3009700001"
        assert persona_completa.correo_principal == "completo@test.com"
        assert persona_completa.esta_activa is True
        assert len(persona_completa.roles) == 2
        assert "Propietario" in persona_completa.roles
        assert "Asesor" in persona_completa.roles
