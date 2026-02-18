import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infraestructura.persistencia.database import db_manager

def get_view_def():
    print("=== VIEW DEFINITION ===", flush=True)
    try:
        with db_manager.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT definition FROM pg_views WHERE viewname = 'vw_alerta_vencimiento_contratos'")
            row = cursor.fetchone()
            if row:
                print(list(row.values())[0], flush=True)
            else:
                print("View not found", flush=True)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_view_def()
