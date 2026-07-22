"""
Fixtures para tests de integración.

Proporciona fixtures para:
- Conexión a base de datos de prueba (PostgreSQL)
- Repositorios configurados
- Datos de prueba
"""
import pytest
import psycopg2
import os


@pytest.fixture(scope="session")
def db_connection():
    """
    Crea una conexión a la base de datos PostgreSQL de test/staging.
    """
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        pytest.skip("DATABASE_URL no configurado")
    
    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    yield conn
    conn.close()


@pytest.fixture(scope="function")
def db_with_schema(db_connection):
    """
    Crea una base de datos con el esquema completo.
    (Staging DB ya debería tener el esquema)
    """
    return db_connection

@pytest.fixture
def cursor(db_connection):
    """Proporciona un cursor para ejecutar consultas en tests."""
    with db_connection.cursor() as cur:
        yield cur
