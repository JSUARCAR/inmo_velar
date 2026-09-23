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
                    with patch("src.presentacion_reflex.state.auth_state.AuthState.end_navigation_generation"):
                        
                        generador = AuthState.require_login_background.fn(auth_state, "test-gen-1")
                        eventos = []
                        async for evento in generador:
                            eventos.append(evento)
                        
                        # No redirige, eventos esta vacio (solo lock context calls _sync_permissions)
                        assert len(eventos) == 0
                        mock_sync.assert_called_once()
