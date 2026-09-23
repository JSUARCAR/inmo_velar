import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from src.presentacion_reflex.state.auth_state import AuthState
from src.dominio.entidades.usuario import Usuario
from src.dominio.entidades.sesion_usuario import SesionUsuario

@pytest.fixture
def auth_state():
    state = AuthState()
    return state

@pytest.mark.asyncio
async def test_login_exito_y_concurrencia(auth_state):
    """Test que verifica que el login exitoso establece login_in_progress=False
    y que bloquea intentos concurrentes."""
    
    # Mocking
    # Dejamos que client_ip falle o tome el valor "unknown"
    
    servicio_mock = MagicMock()
    usuario_mock = Usuario(
        id_usuario=1,
        nombre_usuario="admin",
        contrasena_hash="hash",
        rol="Admin",
        estado_usuario=True,
        fecha_creacion="2023-01-01"
    )
    sesion_mock = SesionUsuario(
        id_usuario=1, token_sesion="token_test",
        fecha_inicio="2023-01-01", fecha_fin="2023-01-02"
    )
    
    servicio_mock.autenticar.return_value = usuario_mock
    servicio_mock.crear_sesion.return_value = sesion_mock
    
    # Need to patch ServicioAutenticacion inside the auth_state method, or mock DB.
    # The actual login uses RepositorioUsuario(db_manager) and ServicioAutenticacion().
    # So we should patch ServicioAutenticacion and RepositorioUsuario, RepositorioSesion.
    with patch("src.presentacion_reflex.state.auth_state.ServicioAutenticacion", return_value=servicio_mock):
        with patch("src.presentacion_reflex.state.auth_state.RepositorioUsuario"):
            with patch("src.presentacion_reflex.state.auth_state.RepositorioSesion"):
                # Simulamos el generador de login
                generador = auth_state.login({"username": "admin", "password": "123"})
                
                # Consumimos el generador completamente
                eventos = []
                async for evento in generador:
                    eventos.append(evento)
                    
                # Verificaciones
                assert auth_state.login_in_progress is False
                assert auth_state.error_message == ""
                
                # Concurrencia
                auth_state.login_in_progress = True
                generador2 = auth_state.login({"username": "admin", "password": "123"})
                eventos2 = []
                async for evento in generador2:
                    eventos2.append(evento)
                
                # Servicio autenticar fue llamado solo 1 vez en el primer test
                servicio_mock.autenticar.assert_called_once()

