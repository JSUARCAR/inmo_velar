"""
Fixtures para tests de integración.

Proporciona fixtures para:
- Conexión a base de datos de prueba
- Repositorios configurados
- Datos de prueba
"""
import pytest
import sqlite3
from pathlib import Path


@pytest.fixture(scope="function")
def db_connection(tmp_path):
    """
    Crea una conexión a una base de datos SQLite temporal.
    Se limpia después de cada test.
    """
    db_file = tmp_path / "test_integration.db"
    conn = sqlite3.connect(str(db_file))
    
    yield conn
    
    conn.close()
    if db_file.exists():
        db_file.unlink()


@pytest.fixture(scope="function")
def db_with_schema(db_connection):
    """
    Crea una base de datos con el esquema completo.
    """
    # Aquí se puede cargar el esquema desde un archivo SQL
    # Por ahora retornamos la conexión básica
    return db_connection
