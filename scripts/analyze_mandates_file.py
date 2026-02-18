import os
import sys
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infraestructura.persistencia.database import db_manager

def analyze_mandates_file():
    try:
        conn = db_manager.obtener_conexion()
        cursor = conn.cursor()
        
        today = datetime.now().strftime("%Y-%m-%d")
        future_90 = (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d")
        
        output = []
        output.append(f"Today: {today}")
        output.append(f"Limit: {future_90}")

        query = """
        SELECT count(*)
        FROM contratos_mandatos
        WHERE estado_contrato_m = 'Activo'
          AND fecha_fin_contrato_m <= %s
        """
        cursor.execute(query, (future_90,))
        res = cursor.fetchone()
        total_view = list(res.values())[0] if hasattr(res, 'values') else res[0]
        output.append(f"Total View (<= 90): {total_view}")

        query_future = """
        SELECT count(*)
        FROM contratos_mandatos
        WHERE estado_contrato_m = 'Activo'
          AND fecha_fin_contrato_m <= %s
          AND fecha_fin_contrato_m >= %s
        """
        cursor.execute(query_future, (future_90, today))
        res = cursor.fetchone()
        total_service = list(res.values())[0] if hasattr(res, 'values') else res[0]
        output.append(f"Total Service (>= Today <= 90): {total_service}")
        
        output.append(f"Diff: {total_view - total_service}")
        
        with open("results.txt", "w") as f:
            f.write("\n".join(output))
            
    except Exception as e:
        with open("results.txt", "w") as f:
            f.write(f"Error: {e}")

if __name__ == "__main__":
    analyze_mandates_file()
