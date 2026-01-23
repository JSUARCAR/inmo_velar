"""
Script de Verificación de Conexión a PostgreSQL
Verifica que la migración fue exitosa y que la aplicación puede conectarse
"""

import psycopg2
from psycopg2 import sql

POSTGRES_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'db_inmo_velar',
    'user': 'inmo_user',
    'password': '7323'
}

def test_connection():
    """Prueba la conexión a PostgreSQL"""
    print("=" * 70)
    print("VERIFICACION DE CONEXION A POSTGRESQL")
    print("=" * 70)
    print("")
    
    try:
        # Intentar conectar
        print("Intentando conectar a PostgreSQL...")
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cursor = conn.cursor()
        
        print(f"[OK] Conexion exitosa a '{POSTGRES_CONFIG['database']}'")
        print("")
        
        # Verificar versión de PostgreSQL
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"Version de PostgreSQL:")
        print(f"  {version}")
        print("")
        
        # Listar tablas
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        
        print(f"Tablas encontradas: {len(tables)}")
        for table in tables:
            # Contar registros en cada tabla
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"  - {table[0]}: {count} registros")
        
        print("")
        
        # Verificar vistas
        cursor.execute("""
            SELECT table_name
            FROM information_schema.views
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        views = cursor.fetchall()
        
        print(f"Vistas encontradas: {len(views)}")
        for view in views:
            print(f"  - {view[0]}")
        
        print("")
        
        # Verificar triggers
        cursor.execute("""
            SELECT DISTINCT trigger_name
            FROM information_schema.triggers
            WHERE trigger_schema = 'public'
            ORDER BY trigger_name;
        """)
        triggers = cursor.fetchall()
        
        print(f"Triggers encontrados: {len(triggers)}")
        for trigger in triggers:
            print(f"  - {trigger[0]}")
        
        print("")
        
        # Probar una consulta simple
        print("Probando consulta de ejemplo...")
        cursor.execute("""
            SELECT COUNT(*) as total_usuarios
            FROM USUARIOS
            WHERE ESTADO_USUARIO = TRUE
        """)
        result = cursor.fetchone()
        print(f"  Usuarios activos: {result[0]}")
        
        cursor.execute("""
            SELECT COUNT(*) as total_propiedades
            FROM PROPIEDADES
            WHERE DISPONIBILIDAD_PROPIEDAD = TRUE
        """)
        result = cursor.fetchone()
        print(f"  Propiedades disponibles: {result[0]}")
        
        print("")
        
        # Cerrar conexión
        cursor.close()
        conn.close()
        
        print("=" * 70)
        print("[OK] VERIFICACION COMPLETADA EXITOSAMENTE")
        print("=" * 70)
        print("")
        print("Tu base de datos PostgreSQL esta lista para usarse!")
        print("")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error al conectar: {e}")
        print("")
        print("Posibles soluciones:")
        print("1. Verifica que PostgreSQL este en ejecucion")
        print("2. Verifica las credenciales de conexion")
        print("3. Asegurate de haber ejecutado migrate_to_postgresql.py primero")
        print("")
        return False

if __name__ == '__main__':
    test_connection()
