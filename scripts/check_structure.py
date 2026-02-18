import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infraestructura.persistencia.database import db_manager

def check_structure():
    print("=== Database Structure Check ===")
    try:
        with db_manager.obtener_conexion() as conn:
            cursor = conn.cursor()
            
            # List all tables
            print("\n[TABLES]")
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            tables = [r[0] for r in cursor.fetchall()]
            for t in sorted(tables):
                print(f" - {t}")
                
            # Get View Definition
            print("\n[VIEW DEFINITION: vw_alerta_vencimiento_contratos]")
            # Postgres stores view definitions in information_schema.views or pg_get_viewdef function
            cursor.execute("SELECT view_definition FROM information_schema.views WHERE table_name = 'vw_alerta_vencimiento_contratos'")
            row = cursor.fetchone()
            if row:
                print(row[0])
            else:
                print("View not found in information_schema.views (check case?)")
                
            # Try case insensitive search for view
            cursor.execute("SELECT table_name FROM information_schema.views WHERE table_schema = 'public'")
            print("\n[VIEWS FOUND]")
            for r in cursor.fetchall():
                print(f" - {r[0]}")

    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    check_structure()
