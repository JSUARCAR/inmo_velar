import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infraestructura.persistencia.database import db_manager

def list_to_file():
    try:
        conn = db_manager.obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema NOT IN ('information_schema', 'pg_catalog')")
        rows = cursor.fetchall()
        
        with open("tables_list.txt", "w") as f:
            for r in rows:
                # r is dict
                s = r.get('TABLE_SCHEMA', '')
                t = r.get('TABLE_NAME', '')
                f.write(f"{s}.{t}\n")
                
        print("Written to tables_list.txt")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_to_file()
