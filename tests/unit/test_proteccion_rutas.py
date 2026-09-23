import pytest
from unittest.mock import MagicMock, patch
from src.presentacion_reflex.state.auth_state import AuthState

@pytest.fixture
def auth_state():
    return AuthState()

@pytest.mark.asyncio
async def test_require_login_background(auth_state):
    """Test que require_login_background restablece is_loading en todas sus rutas"""
    
    with patch("src.presentacion_reflex.state.auth_state.AuthState._validate_session") as mock_validate:
        with patch("src.presentacion_reflex.state.auth_state.AuthState.start_navigation_generation") as mock_start:
            with patch("src.presentacion_reflex.state.auth_state.AuthState.end_navigation_generation") as mock_end:
                with patch("src.presentacion_reflex.state.auth_state.AuthState.validate_generation", return_value=True):
                    
                    # Obtener la funcion original saltando el wrap de Reflex
                    original_fn = AuthState.require_login_background.fn
                    
                    # Ruta 1: Exito (valido -> continua)
                    mock_validate.return_value = True
                    generador = original_fn(auth_state, "test-gen-1")
                    async for _ in generador:
                        pass
                    
                    mock_end.assert_called_with("test-gen-1")
                    
                    # Ruta 2: Invalido -> redirige
                    mock_end.reset_mock()
                    mock_validate.return_value = False
                    
                    generador = original_fn(auth_state, "test-gen-2")
                    async for _ in generador:
                        pass
                        
                    mock_end.assert_called_with("test-gen-2")
