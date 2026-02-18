import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infraestructura.persistencia.database import db_manager

def check_simple():
    print("=== Simple Check ===")
    try:
        conn = db_manager.obtener_conexion()
        cursor = conn.cursor()
        print("Connection success.")
        
        # Try a direct query on the table we suspect exists
        try:
            print("Querying CONTRATOS_ARRENDAMIENTOS...")
            cursor.execute("SELECT count(*) FROM CONTRATOS_ARRENDAMIENTOS")
            print(f"Count: {cursor.fetchone()[0]}")
        except Exception as e:
            print(f"Error CONTRATOS_ARRENDAMIENTOS: {e}")
            conn.rollback()
            
        try:
            print("Querying contratos_arrendamientos...")
            cursor.execute("SELECT count(*) FROM contratos_arrendamientos")
            print(f"Count: {cursor.fetchone()[0]}")
        except Exception as e:
            print(f"Error contratos_arrendamientos: {e}")
            conn.rollback()

        # Check view content again
        try:
            print("Querying VW_ALERTA_VENCIMIENTO_CONTRATOS...")
            cursor.execute("SELECT count(*) FROM VW_ALERTA_VENCIMIENTO_CONTRATOS")
            print(f"View Count: {cursor.fetchone()[0]}")
        except Exception as e:
            print(f"Error VW: {e}")
            
    except Exception as e:
        print(f"[FATAL] {e}")

if __name__ == "__main__":
    check_simple()
