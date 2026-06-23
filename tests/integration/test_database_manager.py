"""
Mock DatabaseManager para tests de integración.

Permite crear instancias con rutas de BD personalizadas para testing.
"""

import sqlite3
from pathlib import Path
from contextlib import contextmanager


def dict_factory(cursor, row):
    return {col[0].upper(): row[idx] for idx, col in enumerate(cursor.description)}


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

    def obtener_conexion(self) -> sqlite3.Connection:
        """
        Obtiene una conexión a la base de datos.

        Returns:
            Conexión SQLite
        """
        if self._connection is None:
            self._connection = sqlite3.connect(
                str(self.database_path), check_same_thread=False
            )
            self._connection.row_factory = dict_factory
            self._connection.execute("PRAGMA foreign_keys = ON")

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
