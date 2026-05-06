import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infraestructura.persistencia.database import db_manager

def list_contratos_tables():
    print("=== TABLES MATCHING 'contratos' ===", flush=True)
    try:
        conn = db_manager.obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT table_schema, table_name FROM information_schema.tables WHERE table_name LIKE '%contratos%'")
        rows = cursor.fetchall()
        for r in rows:
            # r is a dict due to db_manager wrapper
            # keys are uppercase: TABLE_SCHEMA, TABLE_NAME
            print(f"{r.get('TABLE_SCHEMA', 'public')}.{r.get('TABLE_NAME', 'unknown')}", flush=True)
            
    except Exception as e:
        print(f"Error: {e}", flush=True)

if __name__ == "__main__":
    list_contratos_tables()
