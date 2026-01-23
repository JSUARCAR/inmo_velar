"""
Mock DatabaseManager para tests de integración.

Permite crear instancias con rutas de BD personalizadas para testing.
"""
import sqlite3
from pathlib import Path
from contextlib import contextmanager


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
    
    def obtener_conexion(self) -> sqlite3.Connection:
        """
        Obtiene una conexión a la base de datos.
        
        Returns:
            Conexión SQLite
        """
        if self._connection is None:
            self._connection = sqlite3.connect(
                str(self.database_path),
                check_same_thread=False
            )
            self._connection.row_factory = sqlite3.Row
            self._connection.execute("PRAGMA foreign_keys = ON")
        
        return self._connection
    
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
