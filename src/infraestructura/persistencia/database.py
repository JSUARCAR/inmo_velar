"""
Gestor de Base de Datos - Soporte Dual SQLite/PostgreSQL

Maneja las conexiones a la base de datos usando el patrón Singleton.
Detecta automáticamente el modo desde .env (DB_MODE).
"""

import os
import sqlite3
import threading
import atexit
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Optional
import unicodedata
from contextvars import ContextVar

import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv

# ContextVar for managing connections per asyncio task smoothly
_pg_conn_ctx = ContextVar("pg_conn_ctx", default=None)

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

# print(f"DEBUG [database.py]: Final DB_MODE: {DB_MODE}")

# Importar el módulo correcto según el modo
if DB_MODE == "postgresql":
    import psycopg2
    import psycopg2.pool

    USE_POSTGRESQL = True

    import psycopg2.extensions

    class UpperCaseCursorWrapper:
        def __init__(self, cursor, conn_wrapper=None):
            self._cursor = cursor
            self._conn_wrapper = conn_wrapper  # Stong reference to prevent premature GC

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

        def close(self):
            return self._cursor.close()

    class UpperCaseConnectionWrapper:
        def __init__(self, pool_ref, conn):
            self._pool = pool_ref
            self._conn = conn
            self._is_returned = False

        def cursor(self, *args, **kwargs):
            # Always force RealDictCursor if not specified to ensure dict access
            if "cursor_factory" not in kwargs:
                from psycopg2.extras import RealDictCursor

                kwargs["cursor_factory"] = RealDictCursor

            cursor = self._conn.cursor(*args, **kwargs)
            return UpperCaseCursorWrapper(cursor, conn_wrapper=self)

        def __getattr__(self, name):
            return getattr(self._conn, name)

        def close(self):
            if not self._is_returned and self._conn:
                try:
                    self._pool.putconn(self._conn)
                except Exception:
                    pass
                self._is_returned = True

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            # No retornamos aqui para permitir operaciones multiplexadas. Se hara GC en __del__
            return False

        def __del__(self):
            if not self._is_returned and self._conn:
                try:
                    self._pool.putconn(self._conn)
                except Exception:
                    pass
                self._is_returned = True

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
        self._pg_pool = None

        if self.use_postgresql:
            # Solo guardamos configuración, no conectamos todavía
            self._configurar_postgresql()
        else:
            # Configuración SQLite
            config = obtener_configuracion()
            self.database_path = Path(config.database_path)

        self._connection_pool: dict[int, Any] = {}
        atexit.register(self.shutdown)
        self._initialized = True

    def _configurar_postgresql(self):
        """Carga la configuración de Postgres desde el entorno."""
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
                "application_name": os.getenv(
                    "DB_APPLICATION_NAME", "InmobiliariaVelar"
                ),
            }
        else:
            self.pg_config = {
                "host": os.getenv("DB_HOST", "localhost"),
                "port": int(os.getenv("DB_PORT", 5432)),
                "database": os.getenv("DB_NAME", "db_inmo_velar"),
                "user": os.getenv("DB_USER", "inmo_user"),
                "password": os.getenv("DB_PASSWORD"),
                "connect_timeout": int(os.getenv("DB_CONNECT_TIMEOUT", 10)),
                "application_name": os.getenv(
                    "DB_APPLICATION_NAME", "InmobiliariaVelar"
                ),
            }

    def _inicializar_pg_pool(self):
        """Carga perezosa del connection pool de Postgres."""
        if self._pg_pool is None:
            with self._lock:
                if self._pg_pool is None:
                    # Inicializar ThreadedConnectionPool (Min 1, Max 20 sockets independientes)
                    self._pg_pool = psycopg2.pool.ThreadedConnectionPool(
                        minconn=1, maxconn=20, **self.pg_config
                    )

    def _obtener_connection_thread_local(self) -> Any:
        """
        Obtiene una conexión para el contexto actual.
        Usa ContextVars nativo para Postgres o Thread_id para SQLite.
        """
        if self.use_postgresql:
            if self._pg_pool is None:
                self._inicializar_pg_pool()

            conn_wrapper = _pg_conn_ctx.get()

            if (
                conn_wrapper is None
                or conn_wrapper._is_returned
                or not self._validar_conexion(conn_wrapper)
            ):
                # Limpiar la desconectada si hubo alguna
                if conn_wrapper and not conn_wrapper._is_returned:
                    conn_wrapper.close()

                try:
                    real_conn = self._pg_pool.getconn()
                except psycopg2.pool.PoolError:
                    # En caso de agotar el pool, forzar spawn de una off-pool JIT (Safety measure)
                    real_conn = psycopg2.connect(**self.pg_config)

                real_conn.autocommit = False
                conn_wrapper = UpperCaseConnectionWrapper(self._pg_pool, real_conn)
                _pg_conn_ctx.set(conn_wrapper)

            return conn_wrapper

        # Metodo clasico SQLite Thread-Local
        thread_id = threading.get_ident()

        if thread_id not in self._connection_pool:
            # Conexión SQLite
            conexion = sqlite3.connect(str(self.database_path), check_same_thread=False)
            conexion.row_factory = sqlite3.Row
            conexion.execute("PRAGMA foreign_keys = ON")
            # Registrar función de búsqueda sin acentos
            conexion.create_function("unaccent_lower", 1, self.normalize_search_term)

            self._connection_pool[thread_id] = conexion

        return self._connection_pool[thread_id]

    def _validar_conexion(self, conn) -> bool:
        """
        Verifica si la conexión sigue viva orgánicamente usando el socket subyacente de psycopg2
        """
        if not self.use_postgresql:
            return True

        try:
            real_conn = getattr(conn, "_conn", conn)
            # Poll returns 0 (POLL_OK) if connection is active
            if real_conn.closed != 0:
                return False

            if real_conn.poll() != psycopg2.extensions.POLL_OK:
                return False
            # Execute a lightweight query just to be sure
            with real_conn.cursor() as cur:
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

    def get_last_insert_id(
        self, cursor, table_name: str = None, id_column: str = None
    ) -> int:
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

    def shutdown(self) -> None:
        """Cierra todas las conexiones del pool de PostgreSQL y limpia recursos."""
        if self.use_postgresql and self._pg_pool is not None:
            try:
                self._pg_pool.closeall()
                print("DEBUG [database.py]: PostgreSQL pool cerrado exitosamente")
            except Exception as e:
                print(f"DEBUG [database.py]: Error cerrando pool PostgreSQL: {e}")
            finally:
                self._pg_pool = None

        # Cerrar conexiones SQLite si existen
        self.cerrar_todas_conexiones()
        print("DEBUG [database.py]: DatabaseManager shutdown completado")

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
        info = {
            "mode": self.db_mode,
            "type": "PostgreSQL" if self.use_postgresql else "SQLite",
        }

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

    @staticmethod
    def normalize_search_term(term: str) -> str:
        """
        Normaliza un término quitándole tildes y convirtiéndolo a minúsculas.
        Usado internamente por SQLite (inyectado) y por los repositorios web.
        """
        if term is None:
            return ""
        # Normaliza y elimina marcas de combinación (acentos/diacríticos)
        term_str = str(term)
        nfkd_form = unicodedata.normalize("NFKD", term_str)
        return "".join([c for c in nfkd_form if not unicodedata.combining(c)]).lower()

    def get_search_condition(self, columns: list[str]) -> str:
        """
        Genera la condición SQL OR para múltiples columnas que ignora acentos y mayúsculas.
        Ejemplo PG: unaccent(lower(col)) LIKE %s OR unaccent(lower(col2)) LIKE %s
        Ejemplo SL: unaccent_lower(col) LIKE ? OR unaccent_lower(col2) LIKE ?
        """
        placeholder = self.get_placeholder()
        conditions = []
        for col in columns:
            if self.use_postgresql:
                conditions.append(f"unaccent(lower({col})) LIKE {placeholder}")
            else:
                # Usa la función python inyectada
                conditions.append(f"unaccent_lower({col}) LIKE {placeholder}")

        return " OR ".join(conditions)


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
