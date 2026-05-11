"""
Script inteligente para ejecutar archivos SQL contra la base de datos activa.
Soporta SQLite y PostgreSQL basado en database_config.py.
"""
import sys
import os

# Añadir directorio actual al path para importar database_config
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from database_config import get_database_connection, DB_MODE
except ImportError:
    print("Error: No se pudo encontrar database_config.py")
    sys.exit(1)

def execute_sql_file(file_path):
    if not os.path.exists(file_path):
        print(f"Error: El archivo '{file_path}' no existe.")
        return

    print(f"Modo de Base de Datos: {DB_MODE.upper()}")
    print(f"Ejecutando: {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            sql = f.read()

        conn = get_database_connection()
        cursor = conn.cursor()

        if DB_MODE == 'postgresql':
            print("Conectado a PostgreSQL. Ejecutando...")
            cursor.execute(sql)
        else:
            print("Conectado a SQLite. Ejecutando script...")
            # PRAGMA para optimizar la ejecución en SQLite si no están puestos
            cursor.execute("PRAGMA foreign_keys = ON;")
            cursor.executescript(sql)

        conn.commit()
        print("✅ Ejecución finalizada con ÉXITO.")
        
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ ERROR durante la ejecución: {e}")
        if 'conn' in locals():
            conn.rollback()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python apply_sql.py <ruta_archivo_sql>")
        sys.exit(1)
    
    execute_sql_file(sys.argv[1])
