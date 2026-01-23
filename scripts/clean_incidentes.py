import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.infraestructura.persistencia.database import db_manager

def clean_incidentes():
    print("Limpiando tablas de incidentes (Retry)...")
    
    # Order matters for Foreign Keys
    tables_to_clean = [
        "ORDENES_TRABAJO",
        "HISTORIAL_INCIDENTES",
        "COTIZACIONES",
        "INCIDENTES"
    ]
    
    conn = db_manager.obtener_conexion()
    if hasattr(conn, 'autocommit'):
        conn.autocommit = True 

    cursor = db_manager.get_dict_cursor(conn)

    for table in tables_to_clean:
        try:
            print(f"Intentando borrar {table}...")
            cursor.execute(f"DELETE FROM {table}")
            print(f" -> {table} vaciada exitosamente.")
        except Exception as e:
            print(f" -> No se pudo limpiar {table}: {e}")
            # If postgres transaction aborted, we might need rollback to proceed if not autocommit
            try:
                conn.rollback()
            except:
                pass

    print("Limpieza finalizada.")

if __name__ == "__main__":
    clean_incidentes()
