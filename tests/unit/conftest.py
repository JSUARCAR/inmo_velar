"""
Fixtures para tests unitarios.

Proporciona mocks y fixtures para tests unitarios aislados.
"""
import pytest
from unittest.mock import Mock, MagicMock


@pytest.fixture
def mock_repositorio():
    """Mock genérico de un repositorio."""
    return Mock()


@pytest.fixture
def mock_db_manager():
    """Mock del gestor de base de datos."""
    return MagicMock()
