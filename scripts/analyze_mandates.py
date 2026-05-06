import os
import sys
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infraestructura.persistencia.database import db_manager

def analyze_mandates():
    print("=== MANDATES ANALYSIS ===", flush=True)
    try:
        conn = db_manager.obtener_conexion()
        cursor = conn.cursor()
        
        today = datetime.now().strftime("%Y-%m-%d")
        future_90 = (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d")
        
        print(f"Today: {today}", flush=True)
        print(f"Limit: {future_90}", flush=True)

        query = """
        SELECT count(*)
        FROM contratos_mandatos
        WHERE estado_contrato_m = 'Activo'
          AND fecha_fin_contrato_m <= %s
        """
        # Note: We simulate the View logic (<= 90 days, no lower bound)
        cursor.execute(query, (future_90,))
        res = cursor.fetchone()
        total_view = list(res.values())[0] if hasattr(res, 'values') else res[0]
        print(f"Total in View logic (<= 90): {total_view}", flush=True)

        query_future = """
        SELECT count(*)
        FROM contratos_mandatos
        WHERE estado_contrato_m = 'Activo'
          AND fecha_fin_contrato_m <= %s
          AND fecha_fin_contrato_m >= %s
        """
        # Note: We simulate the Service logic (<= 90 days AND >= Today)
        cursor.execute(query_future, (future_90, today))
        res = cursor.fetchone()
        total_service = list(res.values())[0] if hasattr(res, 'values') else res[0]
        print(f"Total in Service logic (>= Today AND <= 90): {total_service}", flush=True)
        
        print(f"Difference (Expired?): {total_view - total_service}", flush=True)

    except Exception as e:
        print(f"Error: {e}", flush=True)

if __name__ == "__main__":
    analyze_mandates()
