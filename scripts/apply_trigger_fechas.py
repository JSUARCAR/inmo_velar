import os
import sys

# Añadir la raíz del proyecto al path para importar database_config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from migraciones.database_config import get_database_connection, DB_MODE

def apply_trigger_fechas():
    print(f"Modo de base de datos actual: {DB_MODE}")
    
    if DB_MODE != 'postgresql':
        print("ERROR: Este trigger es específico para PostgreSQL. Cambie DB_MODE a 'postgresql' en su .env")
        return

    sql_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                 'migraciones', 'sql', 'trg_sync_fechas_mandato.sql')
    
    if not os.path.exists(sql_file_path):
        print(f"ERROR: No se encontró el archivo SQL en {sql_file_path}")
        return

    try:
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
            
        conn = get_database_connection()
        cursor = conn.cursor()
        
        print("Aplicando script DDL de sincronización de fechas...")
        cursor.execute(sql_script)
        conn.commit()
        
        print("¡Éxito! El trigger trg_sync_fechas_mandato ha sido aplicado correctamente.")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"ERROR durante la aplicación del trigger: {e}")

if __name__ == "__main__":
    apply_trigger_fechas()
