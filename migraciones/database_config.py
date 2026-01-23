"""
Configuración de Base de Datos con soporte para SQLite y PostgreSQL
Carga automática desde variables de entorno (.env)
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# ============================================================================
# CONFIGURACIÓN DE BASE DE DATOS
# ============================================================================

# Modo de base de datos: 'sqlite' o 'postgresql'
DB_MODE = os.getenv('DB_MODE', 'sqlite')

# ============================================================================
# POSTGRESQL - Nueva configuración
# ============================================================================

POSTGRES_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'db_inmo_velar'),
    'user': os.getenv('DB_USER', 'inmo_user'),
    'password': os.getenv('DB_PASSWORD', '7323'),
    'connect_timeout': int(os.getenv('DB_CONNECT_TIMEOUT', 10)),
    'application_name': os.getenv('DB_APPLICATION_NAME', 'InmobiliariaVelar')
}

# URL de conexión PostgreSQL (para ORMs como SQLAlchemy)
DATABASE_URL_POSTGRES = (
    f"postgresql://{POSTGRES_CONFIG['user']}:{POSTGRES_CONFIG['password']}"
    f"@{POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG['port']}/{POSTGRES_CONFIG['database']}"
)

# ============================================================================
# SQLITE - Configuración legacy (mantener para compatibilidad)
# ============================================================================

DATABASE_PATH_SQLITE = os.getenv('DATABASE_PATH_LEGACY', 'migraciones/DB_Inmo_Velar.db')

# ============================================================================
# FUNCIONES HELPER
# ============================================================================

def get_database_connection():
    """
    Retorna una conexión a la base de datos según el modo configurado
    
    Returns:
        connection: Conexión a PostgreSQL o SQLite según DB_MODE
    """
    if DB_MODE == 'postgresql':
        import psycopg2
        return psycopg2.connect(**POSTGRES_CONFIG)
    else:
        import sqlite3
        return sqlite3.connect(DATABASE_PATH_SQLITE)

def get_database_url():
    """
    Retorna la URL de conexión para ORMs
    
    Returns:
        str: URL de conexión (postgresql:// o sqlite:///)
    """
    if DB_MODE == 'postgresql':
        return DATABASE_URL_POSTGRES
    else:
        return f"sqlite:///{DATABASE_PATH_SQLITE}"

def get_placeholder():
    """
    Retorna el placeholder correcto según el modo de BD
    
    Returns:
        str: '%s' para PostgreSQL, '?' para SQLite
    """
    return '%s' if DB_MODE == 'postgresql' else '?'

# ============================================================================
# POOL DE CONEXIONES (Para PostgreSQL en producción)
# ============================================================================

if DB_MODE == 'postgresql':
    try:
        from psycopg2 import pool
        
        # Crear pool de conexiones
        connection_pool = pool.SimpleConnectionPool(
            minconn=int(os.getenv('DB_POOL_MIN', 1)),
            maxconn=int(os.getenv('DB_POOL_MAX', 10)),
            **POSTGRES_CONFIG
        )
        
        def get_connection_from_pool():
            """Obtiene una conexión del pool"""
            return connection_pool.getconn()
        
        def return_connection_to_pool(conn):
            """Devuelve una conexión al pool"""
            connection_pool.putconn(conn)
            
    except ImportError:
        print("psycopg2 no instalado. Pool de conexiones no disponible.")
        connection_pool = None

# ============================================================================
# INFORMACIÓN DE CONFIGURACIÓN
# ============================================================================

def print_config_info():
    """Imprime información de configuración de la base de datos"""
    print("=" * 70)
    print("CONFIGURACIÓN DE BASE DE DATOS")
    print("=" * 70)
    print(f"Modo actual: {DB_MODE.upper()}")
    print()
    
    if DB_MODE == 'postgresql':
        print("PostgreSQL:")
        print(f"  Host: {POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG['port']}")
        print(f"  Base de datos: {POSTGRES_CONFIG['database']}")
        print(f"  Usuario: {POSTGRES_CONFIG['user']}")
        print(f"  Timeout: {POSTGRES_CONFIG['connect_timeout']}s")
        print(f"  Aplicación: {POSTGRES_CONFIG['application_name']}")
        if connection_pool:
            print(f"  Pool: {os.getenv('DB_POOL_MIN')}-{os.getenv('DB_POOL_MAX')} conexiones")
    else:
        print("SQLite:")
        print(f"  Ruta: {DATABASE_PATH_SQLITE}")
    
    print("=" * 70)

# ============================================================================
# TESTING
# ============================================================================

if __name__ == '__main__':
    print_config_info()
    
    # Probar conexión
    print("\nProbando conexión...")
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        
        if DB_MODE == 'postgresql':
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"[OK] Conectado a PostgreSQL:")
            print(f"     {version}")
        else:
            cursor.execute("SELECT sqlite_version();")
            version = cursor.fetchone()[0]
            print(f"[OK] Conectado a SQLite {version}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"[ERROR] No se pudo conectar: {e}")
