"""
Tests de integración para ServicioConfiguracion.
Usa la base de datos real con datos de prueba prefijados.
"""

import pytest
import hashlib

from src.infraestructura.persistencia.database import db_manager
from src.aplicacion.servicios.servicio_configuracion import ServicioConfiguracion


# Prefijo para identificar datos de prueba
TEST_PREFIX = "TEST_INTEG_"


@pytest.fixture
def servicio():
    """Crea instancia del servicio."""
    return ServicioConfiguracion(db_manager)


@pytest.fixture
def setup_test_usuario():
    """Crea usuario de prueba y lo elimina después."""
    hash_pass = hashlib.sha256("test123".encode()).hexdigest()
    
    with db_manager.obtener_conexion() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO USUARIOS (NOMBRE_USUARIO, CONTRASENA_HASH, ROL, ESTADO_USUARIO)
            VALUES (?, ?, ?, ?)
        """, (f"{TEST_PREFIX}usuario", hash_pass, "Asesor", 1))
        conn.commit()
    
    yield
    
    # Cleanup
    with db_manager.obtener_conexion() as conn:
        conn.execute(f"DELETE FROM USUARIOS WHERE NOMBRE_USUARIO LIKE '{TEST_PREFIX}%'")
        conn.commit()


@pytest.fixture
def setup_test_ipc():
    """Crea IPC de prueba y lo elimina después."""
    # Usamos un año muy futuro para no interferir con datos reales
    with db_manager.obtener_conexion() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO IPC (ANIO, VALOR_IPC, FECHA_PUBLICACION)
            VALUES (?, ?, ?)
        """, (2999, 850, "2999-01-15"))
        conn.commit()
    
    yield
    
    # Cleanup
    with db_manager.obtener_conexion() as conn:
        conn.execute("DELETE FROM IPC WHERE ANIO = 2999")
        conn.commit()


@pytest.fixture
def setup_test_parametros():
    """Crea parámetros de prueba."""
    with db_manager.obtener_conexion() as conn:
        conn.executemany("""
            INSERT OR REPLACE INTO PARAMETROS_SISTEMA 
            (NOMBRE_PARAMETRO, VALOR_PARAMETRO, TIPO_DATO, CATEGORIA, MODIFICABLE)
            VALUES (?, ?, ?, ?, ?)
        """, [
            (f"{TEST_PREFIX}PARAM_MOD", "100", "INTEGER", "PRUEBAS", 1),
            (f"{TEST_PREFIX}PARAM_FIJO", "999", "INTEGER", "PRUEBAS", 0),
        ])
        conn.commit()
    
    yield
    
    with db_manager.obtener_conexion() as conn:
        conn.execute(f"DELETE FROM PARAMETROS_SISTEMA WHERE NOMBRE_PARAMETRO LIKE '{TEST_PREFIX}%'")
        conn.commit()


class TestServicioConfiguracionUsuarios:
    """Tests de integración para gestión de usuarios."""
    
    def test_listar_usuarios(self, servicio, setup_test_usuario):
        """Test: Listar usuarios incluye el de prueba."""
        usuarios = servicio.listar_usuarios(incluir_inactivos=True)
        
        nombres = [u.nombre_usuario for u in usuarios]
        assert any(TEST_PREFIX in n for n in nombres)
    
    def test_crear_usuario(self, servicio):
        """Test: Crear nuevo usuario."""
        try:
            usuario = servicio.crear_usuario(
                nombre_usuario=f"{TEST_PREFIX}nuevo",
                contrasena="password123",
                rol="Asesor",
                usuario_sistema="admin"
            )
            
            assert usuario.id_usuario is not None
            assert usuario.rol == "Asesor"
        finally:
            # Cleanup
            with db_manager.obtener_conexion() as conn:
                conn.execute(f"DELETE FROM USUARIOS WHERE NOMBRE_USUARIO = '{TEST_PREFIX}nuevo'")
                conn.commit()
    
    def test_crear_usuario_contrasena_corta(self, servicio):
        """Test: Contraseña corta lanza ValueError."""
        with pytest.raises(ValueError) as exc_info:
            servicio.crear_usuario(
                nombre_usuario=f"{TEST_PREFIX}short",
                contrasena="123",
                rol="Asesor",
                usuario_sistema="admin"
            )
        
        assert "6 caracteres" in str(exc_info.value)
    
    def test_crear_usuario_rol_invalido(self, servicio):
        """Test: Rol inválido lanza ValueError."""
        with pytest.raises(ValueError) as exc_info:
            servicio.crear_usuario(
                nombre_usuario=f"{TEST_PREFIX}bad_rol",
                contrasena="password123",
                rol="Gerente",
                usuario_sistema="admin"
            )
        
        assert "Rol inválido" in str(exc_info.value)


class TestServicioConfiguracionIPC:
    """Tests de integración para gestión de IPC."""
    
    def test_listar_ipc(self, servicio, setup_test_ipc):
        """Test: Listar valores IPC incluye el de prueba."""
        lista = servicio.listar_ipc()
        
        anios = [i.anio for i in lista]
        assert 2999 in anios
    
    def test_agregar_ipc(self, servicio):
        """Test: Agregar nuevo IPC."""
        try:
            ipc = servicio.agregar_ipc(
                anio=2998,
                valor_ipc=900,
                usuario_sistema="admin"
            )
            
            assert ipc.id_ipc is not None
            assert ipc.valor_ipc == 900
        finally:
            # Cleanup
            with db_manager.obtener_conexion() as conn:
                conn.execute("DELETE FROM IPC WHERE ANIO = 2998")
                conn.commit()
    
    def test_actualizar_ipc(self, servicio, setup_test_ipc):
        """Test: Actualizar valor IPC."""
        ipc = servicio.obtener_ipc_por_anio(2999)
        
        resultado = servicio.actualizar_ipc(
            id_ipc=ipc.id_ipc,
            valor_ipc=875,
            usuario_sistema="admin"
        )
        
        assert resultado is True


class TestServicioConfiguracionParametros:
    """Tests de integración para gestión de parámetros."""
    
    def test_listar_parametros(self, servicio, setup_test_parametros):
        """Test: Listar todos los parámetros incluye los de prueba."""
        parametros = servicio.listar_parametros()
        
        nombres = [p.nombre_parametro for p in parametros]
        assert any(TEST_PREFIX in n for n in nombres)
    
    def test_obtener_parametro(self, servicio, setup_test_parametros):
        """Test: Obtener parámetro por nombre."""
        parametro = servicio.obtener_parametro(f"{TEST_PREFIX}PARAM_MOD")
        
        assert parametro is not None
        assert parametro.valor_parametro == "100"
    
    def test_obtener_valor_parametro(self, servicio, setup_test_parametros):
        """Test: Obtener valor de parámetro convertido."""
        valor = servicio.obtener_valor_parametro(f"{TEST_PREFIX}PARAM_MOD")
        
        assert valor == 100
    
    def test_obtener_valor_parametro_no_existe(self, servicio):
        """Test: Obtener valor de parámetro inexistente retorna default."""
        valor = servicio.obtener_valor_parametro("NO_EXISTE_XYZ_999", default=50)
        
        assert valor == 50
    
    def test_actualizar_parametro_modificable(self, servicio, setup_test_parametros):
        """Test: Actualizar parámetro modificable."""
        parametro = servicio.obtener_parametro(f"{TEST_PREFIX}PARAM_MOD")
        
        resultado = servicio.actualizar_parametro(
            id_parametro=parametro.id_parametro,
            nuevo_valor="200",
            usuario_sistema="admin"
        )
        
        assert resultado is True
    
    def test_actualizar_parametro_no_modificable(self, servicio, setup_test_parametros):
        """Test: Actualizar parámetro no modificable lanza PermissionError."""
        parametro = servicio.obtener_parametro(f"{TEST_PREFIX}PARAM_FIJO")
        
        with pytest.raises(PermissionError):
            servicio.actualizar_parametro(
                id_parametro=parametro.id_parametro,
                nuevo_valor="1000",
                usuario_sistema="admin"
            )
