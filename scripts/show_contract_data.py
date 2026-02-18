import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infraestructura.persistencia.database import db_manager

def show_data():
    try:
        conn = db_manager.obtener_conexion()
        cursor = conn.cursor()
        print("=== DATA SAMPLES ===")
        cursor.execute("SELECT ID_CONTRATO_A, ESTADO_CONTRATO_A, FECHA_FIN_CONTRATO_A FROM CONTRATOS_ARRENDAMIENTOS LIMIT 10")
        for r in cursor.fetchall():
            # Handle real dict cursor wrapper
            if hasattr(r, 'values'):
                print(list(r.values()))
            else:
                print(r)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    show_data()
