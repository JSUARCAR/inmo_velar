"""
Configuración global de pytest para el proyecto.

Este archivo contiene fixtures y configuraciones compartidas por todos los tests.
"""
import pytest
import sys
from pathlib import Path

# Agregar el directorio raíz al path para imports
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))


@pytest.fixture(scope="session")
def project_root():
    """Retorna el directorio raíz del proyecto."""
    return ROOT_DIR


@pytest.fixture(scope="session")
def db_path_test(tmp_path_factory):
    """Crea una base de datos temporal para tests."""
    db_file = tmp_path_factory.mktemp("data") / "test.db"
    return str(db_file)
