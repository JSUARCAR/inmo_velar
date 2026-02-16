"""
Gestor de Base de Datos - Soporte Dual SQLite/PostgreSQL

Maneja las conexiones a la base de datos usando el patrón Singleton.
Detecta automáticamente el modo desde .env (DB_MODE).
"""

import os
import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Optional

import psycopg2
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Determinar modo de base de datos
# Auto-detect PostgreSQL if DATABASE_URL is set (Railway, Heroku, etc.)
_database_url = os.getenv("DATABASE_URL", "")

# DEBUG LOGGING
# print(f"DEBUG [database.py]: DATABASE_URL length: {len(_database_url)}")
# print(f"DEBUG [database.py]: Is postgresql? {_database_url.startswith('postgresql')}")

if _database_url and _database_url.startswith("postgresql"):
    DB_MODE = "postgresql"
else:
    DB_MODE = os.getenv("DB_MODE", "sqlite").lower()

print(f"DEBUG [database.py]: Final DB_MODE: {DB_MODE}")

# Importar el módulo correcto según el modo
if DB_MODE == "postgresql":
    import psycopg2

    USE_POSTGRESQL = True

    import psycopg2.extensions

    class UpperCaseCursorWrapper:
        def __init__(self, cursor):
            self._cursor = cursor

        def _make_dict(self, row):
            if row is None:
                return None
            # If row is dict-like (RealDictRow)
            if hasattr(row, "keys"):
                return {k.upper(): v for k, v in row.items()}
            # If row is tuple (should not happen if RealDictCursor used, but fallback)
            return row

        def fetchone(self):
            row = self._cursor.fetchone()
            return self._make_dict(row)

        def fetchall(self):
            rows = self._cursor.fetchall()
            if not rows:
                return []
            return [self._make_dict(row) for row in rows]

        def fetchmany(self, size=None):
            rows = self._cursor.fetchmany(size)
            if not rows:
                return []
            return [self._make_dict(row) for row in rows]

        def __iter__(self):
            for row in self._cursor:
                yield self._make_dict(row)

        def __getattr__(self, name):
            return getattr(self._cursor, name)

    class UpperCaseConnectionWrapper:
        def __init__(self, conn):
            self._conn = conn

        def cursor(self, *args, **kwargs):
            # Always force RealDictCursor if not specified to ensure dict access
            if "cursor_factory" not in kwargs:
                from psycopg2.extras import RealDictCursor

                kwargs["cursor_factory"] = RealDictCursor

            cursor = self._conn.cursor(*args, **kwargs)
            return UpperCaseCursorWrapper(cursor)

        def __getattr__(self, name):
            return getattr(self._conn, name)

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            return self._conn.__exit__(exc_type, exc_val, exc_tb)

else:
    import sqlite3

    USE_POSTGRESQL = False


from src.infraestructura.configuracion.settings import obtener_configuracion


class DatabaseManager:
    """
    Singleton para gestión de conexiones dual SQLite/PostgreSQL.

    Características:
    - Thread-safe usando threading.Lock
    - Pool de conexiones simple
    - Context manager para transacciones
    - Soporte automático para SQLite y PostgreSQL
    - Detección automática desde .env
    """

    _instance: Optional["DatabaseManager"] = None
    _lock = threading.Lock()

    def __new__(cls):
        """Patrón Singleton thread-safe."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Inicializa el gestor de base de datos."""
        if self._initialized:
            return

        self.db_mode = DB_MODE
        self.use_postgresql = USE_POSTGRESQL

        if self.use_postgresql:
            # Configuración PostgreSQL
            # Parse DATABASE_URL if available (Railway, Heroku, etc.)
            database_url = os.getenv("DATABASE_URL", "")
            if database_url and database_url.startswith("postgresql"):
                from urllib.parse import urlparse
                parsed = urlparse(database_url)
                self.pg_config = {
                    "host": parsed.hostname or "localhost",
                    "port": parsed.port or 5432,
                    "database": (parsed.path or "/railway").lstrip("/"),
                    "user": parsed.username or "postgres",
                    "password": parsed.password or "",
                    "connect_timeout": int(os.getenv("DB_CONNECT_TIMEOUT", 10)),
                    "application_name": os.getenv("DB_APPLICATION_NAME", "InmobiliariaVelar"),
                }
            else:
                self.pg_config = {
                    "host": os.getenv("DB_HOST", "localhost"),
                    "port": int(os.getenv("DB_PORT", 5432)),
                    "database": os.getenv("DB_NAME", "db_inmo_velar"),
                    "user": os.getenv("DB_USER", "inmo_user"),
                    "password": os.getenv("DB_PASSWORD"),
                    "connect_timeout": int(os.getenv("DB_CONNECT_TIMEOUT", 10)),
                    "application_name": os.getenv("DB_APPLICATION_NAME", "InmobiliariaVelar"),
                }
        else:
            # Configuración SQLite
            config = obtener_configuracion()
            self.database_path = Path(config.database_path)

        self._connection_pool: dict[int, Any] = {}
        self._initialized = True

    def _obtener_connection_thread_local(self) -> Any:
        """
        Obtiene una conexión para el thread actual.

        Retorna conexión apropiada según el modo (SQLite o PostgreSQL).
        """
        thread_id = threading.get_ident()

        if thread_id not in self._connection_pool:
            if self.use_postgresql:
                # Conexión PostgreSQL
                real_conn = psycopg2.connect(**self.pg_config)
                real_conn.autocommit = False
                # Wrap it to ensure cursors return uppercase dicts
                conexion = UpperCaseConnectionWrapper(real_conn)
            else:
                # Conexión SQLite
                conexion = sqlite3.connect(str(self.database_path), check_same_thread=False)
                conexion.row_factory = sqlite3.Row
                conexion.execute("PRAGMA foreign_keys = ON")

            self._connection_pool[thread_id] = conexion

        # Validar conexión antes de retornarla (Solo PostgreSQL)
        if self.use_postgresql:
            conn = self._connection_pool[thread_id]
            if not self._validar_conexion(conn):
                # Si falló, reconectar
                # print(f"DEBUG [database.py]: Connection for thread {thread_id} is dead. Reconnecting...")
                try:
                    conn.close()
                except:
                    pass
                
                real_conn = psycopg2.connect(**self.pg_config)
                real_conn.autocommit = False
                self._connection_pool[thread_id] = UpperCaseConnectionWrapper(real_conn)

        return self._connection_pool[thread_id]

    def _validar_conexion(self, conn) -> bool:
        """
        Verifica si la conexión sigue viva.
        """
        try:
            # Poll returns 0 (POLL_OK) if connection is active
            if conn.closed != 0:
                return False
                
            if conn.poll() != psycopg2.extensions.POLL_OK:
                return False
            # Execute a lightweight query just to be sure
            with conn.cursor() as cur:
               cur.execute("SELECT 1")
            return True
        except Exception:
            # Silent failure for validation checks
            return False

    def obtener_conexion(self) -> Any:
        """
        Obtiene una conexión thread-safe.

        Returns:
            Conexión a la base de datos (SQLite o PostgreSQL según configuración)
        """
        return self._obtener_connection_thread_local()

    def get_dict_cursor(self, conexion=None):
        """
        Obtiene un cursor que retorna resultados como diccionarios.

        Args:
            conexion: Conexión opcional. Si no se provee, usa la del thread actual.

        Returns:
            Cursor configurado para retornar diccionarios
        """
        if conexion is None:
            conexion = self.obtener_conexion()

        if self.use_postgresql:
            # PostgreSQL: La conexión ya está wrappeada y retorna UpperCaseCursorWrapper
            # Por lo tanto, solo llamamos .cursor()
            return conexion.cursor()
        else:
            # SQLite: El row_factory ya está configurado
            return conexion.cursor()

    def get_placeholder(self) -> str:
        """
        Retorna el placeholder correcto según el modo de BD.

        Returns:
            '%s' para PostgreSQL, '?' para SQLite
        """
        return "%s" if self.use_postgresql else "?"

    def execute_write(self, query: str, params: tuple = ()) -> int:
        """
        Ejecuta una consulta de escritura (INSERT, UPDATE, DELETE).
        Maneja automáticamente el placeholder.

        Args:
            query: Consulta SQL con placeholders '?' (serán reemplazados si es PG)
            params: Parámetros para la consulta

        Returns:
            Número de filas afectadas
        """
        placeholder = self.get_placeholder()
        if placeholder != "?":
            query = query.replace("?", placeholder)

        with self.transaccion() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.rowcount

    def execute_query_one(self, query: str, params: tuple = ()) -> Optional[dict]:
        """
        Ejecuta una consulta que retorna una sola fila como diccionario.

        Args:
            query: Consulta SQL
            params: Parámetros

        Returns:
            Diccionario con los datos o None
        """
        placeholder = self.get_placeholder()
        if placeholder != "?":
            query = query.replace("?", placeholder)

        conn = self.obtener_conexion()
        cursor = self.get_dict_cursor(conn)
        cursor.execute(query, params)
        return cursor.fetchone()

    def get_last_insert_id(self, cursor, table_name: str = None, id_column: str = None) -> int:
        """
        Obtiene el último ID insertado de manera compatible.

        Args:
            cursor: Cursor de la base de datos
            table_name: Nombre de la tabla (requerido para PostgreSQL)
            id_column: Nombre de la columna ID (requerido para PostgreSQL)

        Returns:
            Último ID insertado

        Nota:
            Para PostgreSQL, usa RETURNING en tu query INSERT.
            Este método es para compatibilidad con código legacy.
        """
        if self.use_postgresql:
            # PostgreSQL: Usa CURRVAL de la secuencia
            if table_name and id_column:
                seq_name = f"{table_name}_{id_column}_seq".lower()
                cursor.execute(f"SELECT currval('{seq_name}')")
                row = cursor.fetchone()
                # UpperCaseCursorWrapper returns a dict, so we can't use index [0]
                # We need to get the first value from the dictionary
                if hasattr(row, "values"):
                    return list(row.values())[0]
                return row[0]
            else:
                raise ValueError("Para PostgreSQL se requiere table_name e id_column")
        else:
            # SQLite: Usa lastrowid
            return cursor.lastrowid

    @contextmanager
    def transaccion(self):
        """
        Context manager para transacciones.

        Ejemplo de uso:
            >>> with db_manager.transaccion() as conn:
            ...     cursor = conn.cursor()
            ...     cursor.execute("INSERT ...")
            ...     # commit automático al salir del context
        """
        conexion = self.obtener_conexion()

        try:
            yield conexion
            conexion.commit()
        except Exception as e:
            conexion.rollback()
            raise e

    def ejecutar_script(self, script_sql: str) -> None:
        """
        Ejecuta un script SQL (múltiples statements).

        Args:
            script_sql: Script SQL a ejecutar

        Nota:
            Para PostgreSQL, ejecuta statements uno por uno.
        """
        with self.transaccion() as conexion:
            if self.use_postgresql:
                # PostgreSQL: Ejecutar statement por statement
                cursor = conexion.cursor()
                for statement in script_sql.split(";"):
                    statement = statement.strip()
                    if statement:
                        cursor.execute(statement)
                cursor.close()
            else:
                # SQLite: executescript
                conexion.executescript(script_sql)

    def cerrar_todas_conexiones(self) -> None:
        """Cierra todas las conexiones del pool."""
        for conexion in self._connection_pool.values():
            conexion.close()
        self._connection_pool.clear()

    def inicializar_base_datos(self, ruta_schema: Optional[Path] = None) -> None:
        """
        Inicializa la base de datos con el esquema.

        Args:
            ruta_schema: Ruta al archivo SQL del esquema

        Nota:
            Para PostgreSQL, asegúrate de que el esquema esté ya cargado.
        """
        if ruta_schema and ruta_schema.exists():
            with open(ruta_schema, "r", encoding="utf-8") as f:
                schema_sql = f.read()
                self.ejecutar_script(schema_sql)

    def get_db_info(self) -> dict:
        """
        Retorna información sobre la configuración de la base de datos.

        Returns:
            Diccionario con información de configuración
        """
        info = {"mode": self.db_mode, "type": "PostgreSQL" if self.use_postgresql else "SQLite"}

        if self.use_postgresql:
            info.update(
                {
                    "host": self.pg_config["host"],
                    "port": self.pg_config["port"],
                    "database": self.pg_config["database"],
                    "user": self.pg_config["user"],
                }
            )
        else:
            info["path"] = str(self.database_path)

        return info


# Singleton global
db_manager = DatabaseManager()


# Funciones helper para compatibilidad
def get_placeholder() -> str:
    """Helper global para obtener placeholder."""
    return db_manager.get_placeholder()


def get_db_mode() -> str:
    """Helper global para obtener el modo de BD."""
    return db_manager.db_mode


def is_postgresql() -> bool:
    """Helper global para verificar si se usa PostgreSQL."""
    return db_manager.use_postgresql
