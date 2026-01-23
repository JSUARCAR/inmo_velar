import os
import sys

# Agregar el directorio raíz al path para poder importar módulos
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, 'src'))

from infraestructura.persistencia.contexto_base_datos import db_manager

def run_migration():
    print("Applying migration: agregar_representante_legal.sql")
    try:
        migration_path = os.path.join(current_dir, 'migraciones', 'agregar_representante_legal.sql')
        with open(migration_path, 'r') as f:
            sql = f.read()
            
        with db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql)
                conn.commit()
                print("Migration applied successfully!")
    except Exception as e:
        print(f"Error applying migration: {e}")

if __name__ == "__main__":
    run_migration()
