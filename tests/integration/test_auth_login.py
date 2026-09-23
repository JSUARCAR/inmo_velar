import pytest
from src.dominio.repositorios.interfaces import RepositorioUsuario, RepositorioSesion
from src.aplicacion.servicios.servicio_autenticacion import ServicioAutenticacion
from src.infraestructura.persistencia.database import db_manager

@pytest.fixture
def auth_service():
    from src.infraestructura.persistencia.repositorio_usuario import RepositorioUsuario
    from src.infraestructura.persistencia.repositorio_sesion import RepositorioSesion
    
    return ServicioAutenticacion(
        repo_usuario=RepositorioUsuario(db_manager),
        repo_sesion=RepositorioSesion(db_manager)
    )

def test_login_valido_persiste_sesion(auth_service):
    """Test integration: login válido persiste sesión"""
    try:
        # Asume que hay un admin de prueba
        usuario = auth_service.autenticar("admin", "admin0123")
        assert usuario is not None
        
        sesion = auth_service.crear_sesion(usuario)
        assert sesion is not None
        assert sesion.token_sesion is not None
        
        # Validar sesion
        usuario_val = auth_service.validar_sesion(sesion.token_sesion)
        assert usuario_val.id_usuario == usuario.id_usuario
        
    except Exception as e:
        pytest.fail(f"Login failed: {e}")

def _crear_servicio(usuario):
    """Construye un ServicioAutenticacion con repositorios en memoria (sin I/O)."""
    from unittest.mock import MagicMock

    repo_usuario = MagicMock()
    repo_usuario.obtener_por_nombre.return_value = usuario
    repo_usuario.obtener_por_id.return_value = usuario
    repo_sesion = MagicMock()
    servicio = ServicioAutenticacion(repo_usuario=repo_usuario, repo_sesion=repo_sesion)
    return servicio, repo_usuario


def _usuario_legacy_sha256(nombre="legacy_user", hash_sha256=""):
    """Crea un usuario con hash SHA256 legacy almacenado (sin prefijo Bcrypt)."""
    from src.dominio.entidades.usuario import Usuario

    return Usuario(
        nombre_usuario=nombre,
        contrasena_hash=hash_sha256,
        rol="Admin",
        estado_usuario=True,
    )


def test_migracion_sha256_a_bcrypt_rehashea_y_persiste():
    """FR-010/U2: un hash SHA256 legacy valida la contraseña y tras autenticar
    se re-hashea a Bcrypt persistido sin alterar el desenlace exitoso."""
    import hashlib

    contraseña = "clave_legacy_123"
    hash_sha256 = hashlib.sha256(contraseña.encode("utf-8")).hexdigest()
    usuario = _usuario_legacy_sha256(hash_sha256=hash_sha256)
    servicio, repo_usuario = _crear_servicio(usuario)

    resultado = servicio.autenticar(usuario.nombre_usuario, contraseña)

    assert resultado is usuario
    assert resultado.contrasena_hash.startswith("$2b$")
    repo_usuario.actualizar.assert_called()


def test_migracion_sha256_no_alterea_desenlace_invalido():
    """FR-010/U2: con hash SHA256 legacy y contraseña incorrecta el desenlace
    es ErrorCredencialesInvalidas y NO se re-hashea ni se persiste."""
    import hashlib

    from src.dominio.excepciones.excepciones_base import ErrorCredencialesInvalidas

    contraseña = "clave_legacy_123"
    hash_sha256 = hashlib.sha256(contraseña.encode("utf-8")).hexdigest()
    usuario = _usuario_legacy_sha256(hash_sha256=hash_sha256)
    servicio, repo_usuario = _crear_servicio(usuario)

    with pytest.raises(ErrorCredencialesInvalidas):
        servicio.autenticar(usuario.nombre_usuario, "clave_incorrecta")

    repo_usuario.actualizar.assert_not_called()


@pytest.mark.asyncio
async def test_auth_login_persiste_sesion(auth_service):
    from src.presentacion_reflex.state.auth_state import _login_attempts
    _login_attempts.clear()
    from unittest.mock import patch, AsyncMock, PropertyMock
    from src.presentacion_reflex.state.auth_state import AuthState
    
    auth_state = AuthState()
    
    with patch("src.presentacion_reflex.state.auth_state.AuthState.session_token", new_callable=PropertyMock, return_value="token_valido") if hasattr(type(auth_state), 'session_token') and isinstance(getattr(type(auth_state), 'session_token'), property) else patch("src.presentacion_reflex.state.auth_state.AuthState.session_token", new="token_valido"):
        with patch("src.presentacion_reflex.state.auth_state.AuthState._validate_session", return_value=True):
            with patch("src.presentacion_reflex.state.auth_state.AuthState._sync_permissions") as mock_sync:
                with patch("src.presentacion_reflex.state.auth_state.AuthState.validate_generation", return_value=True):
                    
                    generador = AuthState.require_login_background.fn(auth_state, "test-gen-1")
                    eventos = []
                    async for evento in generador:
                        eventos.append(evento)
                    
                    # No redirige, eventos esta vacio (solo lock context calls _sync_permissions)
                    assert len(eventos) == 0
                    mock_sync.assert_called_once()
