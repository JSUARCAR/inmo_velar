"""
Configuración de PostgreSQL para la aplicación Reflex

Este archivo contiene la configuración para conectar tu aplicación
a PostgreSQL en lugar de SQLite.

Instrucciones de uso:
1. Copia esta configuración en tu archivo de configuración principal
2. Actualiza la URL de conexión en todos los repositorios
3. Asegúrate de instalar psycopg2: pip install psycopg2-binary
"""

# =====================================================
# OPCIÓN 1: URL de Conexión Simple (para la mayoría de casos)
# =====================================================

import os
from dotenv import load_dotenv

load_dotenv()

# Para usar con SQLAlchemy o conexiones estándar
# Construir URL desde variables de entorno
DATABASE_URL = f"postgresql://{os.getenv('DB_USER', 'inmo_user')}:{os.getenv('DB_PASSWORD', '7323')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME', 'db_inmo_velar')}"

# =====================================================
# OPCIÓN 2: Diccionario de Configuración (más flexible)
# =====================================================

POSTGRES_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'db_inmo_velar'),
    'user': os.getenv('DB_USER', 'inmo_user'),
    'password': os.getenv('DB_PASSWORD', '7323'),
    'connect_timeout': 10,
    'application_name': 'InmobiliariaVelar'
}

# =====================================================
# EJEMPLO: Conexión con psycopg2
# =====================================================

""" 
import psycopg2

def get_connection():
   
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        return conn
    except Exception as e:
        print(f"Error al conectar a PostgreSQL: {e}")
        raise

# Uso:
# conn = get_connection()
# cursor = conn.cursor()
# cursor.execute("SELECT * FROM USUARIOS")
# ...
"""

# =====================================================
# EJEMPLO: Conexión con SQLAlchemy (si usas ORM)
# =====================================================

"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Crear engine
engine = create_engine(DATABASE_URL, echo=False)

# Crear sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
"""

# =====================================================
# EJEMPLO: Pool de Conexiones (para aplicaciones de alto rendimiento)
# =====================================================

"""
from psycopg2 import pool

# Crear pool de conexiones
connection_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    **POSTGRES_CONFIG
)

def get_connection_from_pool():
    return connection_pool.getconn()

def return_connection_to_pool(conn):
    connection_pool.putconn(conn)
"""

# =====================================================
# CAMBIOS NECESARIOS EN TU CÓDIGO
# =====================================================

"""
1. REEMPLAZAR sqlite3 por psycopg2:
   
   ANTES (SQLite):
   import sqlite3
   conn = sqlite3.connect('database.db')
   
   DESPUÉS (PostgreSQL):
   import psycopg2
   conn = psycopg2.connect(**POSTGRES_CONFIG)

2. AJUSTAR PLACEHOLDERS EN QUERIES:
   
   ANTES (SQLite usa ?):
   cursor.execute("SELECT * FROM usuarios WHERE id = ?", (user_id,))
   
   DESPUÉS (PostgreSQL usa %s):
   cursor.execute("SELECT * FROM usuarios WHERE id = %s", (user_id,))

3. AJUSTAR AUTOINCREMENT:
   
   ANTES (SQLite):
   cursor.execute("INSERT INTO tabla (nombre) VALUES (?)", (nombre,))
   last_id = cursor.lastrowid
   
   DESPUÉS (PostgreSQL):
   cursor.execute("INSERT INTO tabla (nombre) VALUES (%s) RETURNING id", (nombre,))
   last_id = cursor.fetchone()[0]

4. AJUSTAR CONVERSIÓN DE BOOLEANOS:
   
   PostgreSQL usa TRUE/FALSE nativamente, no 0/1
   Los valores ya están convertidos automáticamente en la migración

5. AJUSTAR FUNCIONES DE FECHA:
   
   ANTES (SQLite):
   datetime('now', 'localtime')
   date('now')
   
   DESPUÉS (PostgreSQL):
   CURRENT_TIMESTAMP
   CURRENT_DATE

6. CASE SENSITIVITY:
   
   PostgreSQL es sensible a mayúsculas/minúsculas en identificadores entre comillas.
   Recomendación: Mantén los nombres de columnas/tablas SIN comillas y en MAYÚSCULAS
   como están en la migración.
"""

# =====================================================
# VARIABLES DE ENTORNO (Recomendado para producción)
# =====================================================

"""
# Crea un archivo .env:
DB_HOST=localhost
DB_PORT=5432
DB_NAME=db_inmo_velar
DB_USER=inmo_user
DB_PASSWORD=7323

# Luego en tu código:
import os
from dotenv import load_dotenv

load_dotenv()

POSTGRES_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD')
}
"""

# =====================================================
# TESTING
# =====================================================

if __name__ == '__main__':
    print("Configuracion de PostgreSQL")
    print("=" * 50)
    print(f"Host: {POSTGRES_CONFIG['host']}")
    print(f"Puerto: {POSTGRES_CONFIG['port']}")
    print(f"Base de datos: {POSTGRES_CONFIG['database']}")
    print(f"Usuario: {POSTGRES_CONFIG['user']}")
    print("")
    print(f"URL de conexion:")
    print(f"  {DATABASE_URL}")
    print("")
    print("Para probar la conexion, ejecuta:")
    print("  python verify_connection.py")
