"""
Mock DatabaseManager para tests de integración.

Permite crear instancias con rutas de BD personalizadas para testing.
"""

import sqlite3
from pathlib import Path
from contextlib import contextmanager


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0].upper()] = row[idx]
        d[col[0].lower()] = row[idx]
    return d


class MockCursor:
    def __init__(self, cursor):
        self._cursor = cursor
        
    def __getattr__(self, name):
        return getattr(self._cursor, name)
        
    def execute(self, sql, parameters=None):
        if "%s" in sql:
            sql = sql.replace("%s", "?")
        sql = sql.replace(" ILIKE ", " LIKE ")
        
        if parameters is not None:
            return self._cursor.execute(sql, parameters)
        return self._cursor.execute(sql)

    def executemany(self, sql, seq_of_parameters):
        if "%s" in sql:
            sql = sql.replace("%s", "?")
        sql = sql.replace(" ILIKE ", " LIKE ")
        return self._cursor.executemany(sql, seq_of_parameters)

class MockConnection:
    def __init__(self, conn):
        self._conn = conn
        
    def __getattr__(self, name):
        return getattr(self._conn, name)
        
    def cursor(self):
        return MockCursor(self._conn.cursor())
        
    def execute(self, sql, parameters=None):
        if "%s" in sql:
            sql = sql.replace("%s", "?")
        sql = sql.replace(" ILIKE ", " LIKE ")
        if parameters is not None:
            return self._conn.execute(sql, parameters)
        return self._conn.execute(sql)

    def executemany(self, sql, seq_of_parameters):
        if "%s" in sql:
            sql = sql.replace("%s", "?")
        sql = sql.replace(" ILIKE ", " LIKE ")
        return self._conn.executemany(sql, seq_of_parameters)
        
    def __enter__(self):
        self._conn.__enter__()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        return self._conn.__exit__(exc_type, exc_val, exc_tb)

def unaccent_dummy(text):
    return text

class TestDatabaseManager:
    """
    Versión simplificada de DatabaseManager para tests.
    No usa singleton, permite especificar ruta de BD.
    """

    def __init__(self, database_path: str):
        """
        Inicializa el gestor con una ruta de BD específica.

        Args:
            database_path: Ruta al archivo de base de datos
        """
        self.database_path = Path(database_path)
        self._connection = None
        self.use_postgresql = False

    def obtener_conexion(self):
        """
        Obtiene una conexión a la base de datos envuelta para compatibilidad con Postgres %s.

        Returns:
            Conexión MockConnection (SQLite)
        """
        if self._connection is None:
            conn = sqlite3.connect(
                str(self.database_path), check_same_thread=False
            )
            conn.row_factory = dict_factory
            conn.create_function("unaccent", 1, unaccent_dummy)
            conn.execute("PRAGMA foreign_keys = ON")
            self._connection = MockConnection(conn)

        return self._connection

    def get_dict_cursor(self, conexion=None):
        """Mock de get_dict_cursor para tests."""
        if conexion is None:
            conexion = self.obtener_conexion()
        return conexion.cursor()

    def get_placeholder(self) -> str:
        """Retorna el placeholder de SQLite."""
        return "?"

    def get_last_insert_id(self, cursor, tabla: str, pk_columna: str) -> int:
        """Mock de get_last_insert_id para tests."""
        return cursor.lastrowid

    @contextmanager
    def transaccion(self):
        """Context manager para transacciones."""
        conexion = self.obtener_conexion()

        try:
            yield conexion
            conexion.commit()
        except Exception as e:
            conexion.rollback()
            raise e

    def cerrar_todas_conexiones(self) -> None:
        """Cierra la conexión."""
        if self._connection:
            self._connection.close()
            self._connection = None
