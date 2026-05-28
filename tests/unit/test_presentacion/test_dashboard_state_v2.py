import pytest
from unittest.mock import MagicMock, patch
from src.presentacion_reflex.state.dashboard_state import DashboardState
import time

def test_safe_fetch_with_retry_success():
    """Valida que _safe_fetch_with_retry funciona al primer intento."""
    mock_fn = MagicMock(return_value="OK")
    res = DashboardState._safe_fetch(mock_fn, "FALLBACK", retries=2)
    assert res == "OK"
    assert mock_fn.call_count == 1

def test_safe_fetch_with_retry_failure():
    """Valida que _safe_fetch retries up to N times and returns default value."""
    mock_fn = MagicMock(side_effect=Exception("Error de BD"))
    errors = []
    
    start = time.time()
    res = DashboardState._safe_fetch(mock_fn, "FALLBACK", error_list=errors, retries=1)
    end = time.time()
    
    assert res == "FALLBACK"
    assert mock_fn.call_count == 2 # Initial + 1 retry
    assert len(errors) == 1
    assert "lambda falló" in errors[0]
    assert (end - start) >= 0.2 # 0.2s * (2**0) = 0.2s sleep on first retry

def test_dashboard_base_concurrency_token():
    """Valida que el token de concurrencia protege contra carreras."""
    state = DashboardState()
    token = state._generate_token()
    assert token is not None
    assert state._is_valid_token(token) is True
    
    # Generar nuevo token invalida el anterior
    token2 = state._generate_token()
    assert state._is_valid_token(token) is False
    assert state._is_valid_token(token2) is True
