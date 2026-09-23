import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from src.presentacion_reflex.state.auth_state import AuthState
from src.dominio.excepciones.excepciones_base import ErrorRecurso
import asyncio

@pytest.fixture
def auth_state():
    from src.presentacion_reflex.state.auth_state import _login_attempts
    _login_attempts.clear()
    return AuthState()

@pytest.mark.asyncio
async def test_bd_no_disponible_desenlace_terminal(auth_state):
    # Simulamos que la DB tira OperationalError o que ServicioAutenticacion tira ErrorRecurso(BD)
    # y chequeamos que login_in_progress=False y error_message es correcto
    with patch("src.presentacion_reflex.state.auth_state.ServicioAutenticacion") as MockServicio:
        mock_instance = MockServicio.return_value
        mock_instance.autenticar.side_effect = ErrorRecurso(codigo_recurso="BD")
        
        generador = auth_state.login({"username": "admin", "password": "123"})
        eventos = []
        async for evento in generador:
            eventos.append(evento)
            
        assert auth_state.login_in_progress is False
        assert auth_state.error_message == "El servicio no está disponible en este momento. Intente de nuevo."

@pytest.mark.asyncio
async def test_backend_no_disponible_desenlace_terminal(auth_state):
    # Simulamos timeout -> ErrorRecurso(BACKEND)
    with patch("src.presentacion_reflex.state.auth_state.ServicioAutenticacion") as MockServicio:
        mock_instance = MockServicio.return_value
        mock_instance.autenticar.side_effect = ErrorRecurso(codigo_recurso="BACKEND")
        
        generador = auth_state.login({"username": "admin", "password": "123"})
        eventos = []
        async for evento in generador:
            eventos.append(evento)
            
        assert auth_state.login_in_progress is False
        assert auth_state.error_message == "No se pudo conectar con el servidor. Verifique su conexión e intente de nuevo."
