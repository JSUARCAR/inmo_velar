import sys
import os

# Add src to python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.infraestructura.persistencia.database import db_manager

def check():
    try:
        print("Checking if ORDENES_TRABAJO exists...")
        with db_manager.transaccion() as conn:
            cursor = db_manager.get_dict_cursor(conn)
            cursor.execute("SELECT count(*) FROM ORDENES_TRABAJO")
            res = cursor.fetchone()
            print(f"Result: {res}")
            print("TABLE_EXISTS")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    check()
