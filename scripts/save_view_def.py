import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infraestructura.persistencia.database import db_manager

def save_view_def():
    try:
        with db_manager.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT definition FROM pg_views WHERE viewname = 'vw_alerta_vencimiento_contratos'")
            row = cursor.fetchone()
            if row:
                definition = list(row.values())[0]
                with open("view_def.txt", "w") as f:
                    f.write(definition)
                print("Saved to view_def.txt")
            else:
                print("View not found")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    save_view_def()
