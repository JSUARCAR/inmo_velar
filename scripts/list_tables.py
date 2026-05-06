import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infraestructura.persistencia.database import db_manager

def list_tables():
    print("=== Listando Tablas ===")
    try:
        with db_manager.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            for row in cursor.fetchall():
                print(row[0])
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    list_tables()
