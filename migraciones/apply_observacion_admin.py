import os
import sys

# Añadir el directorio raíz al path para poder importar migraciones.database_config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from migraciones.database_config import get_database_connection, DB_MODE

def apply_migration():
    sql_file = os.path.join(os.path.dirname(__file__), 'agregar_observacion_admin.sql')
    
    if not os.path.exists(sql_file):
        print(f"Error: No se encuentra el archivo {sql_file}")
        return

    print(f"Aplicando migración en modo: {DB_MODE}")
    
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql = f.read()
        
        # En SQLite executescript funciona bien para múltiples comandos, 
        # en Postgres psycopg2.execute también puede manejar scripts simples.
        if DB_MODE == 'postgresql':
            cursor.execute(sql)
        else:
            cursor.executescript(sql)
            
        conn.commit()
        print("Migración aplicada exitosamente.")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error al aplicar la migración: {e}")

if __name__ == "__main__":
    apply_migration()
