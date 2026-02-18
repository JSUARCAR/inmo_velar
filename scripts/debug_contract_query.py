import os
import sys
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infraestructura.persistencia.database import db_manager

def debug_query():
    print("=== DEBUG TABLE QUERY ===", flush=True)
    conn = db_manager.obtener_conexion()
    cursor = conn.cursor()
    
    try:
        # 1. Count Total
        print("\n1. Count 'contratos_arrendamientos':", flush=True)
        cursor.execute("SELECT count(*) FROM contratos_arrendamientos")
        ct = cursor.fetchone()
        # Handle dict cursor
        val = list(ct.values())[0] if hasattr(ct, 'values') else ct[0]
        print(f"   -> {val}", flush=True)

        # 2. Check Column Types
        print("\n2. Column Types (FECHA_FIN_CONTRATO_A):", flush=True)
        cursor.execute("SELECT data_type FROM information_schema.columns WHERE table_name = 'contratos_arrendamientos' AND column_name = 'fecha_fin_contrato_a'")
        row = cursor.fetchone()
        dt = list(row.values())[0] if row else "Unknown"
        print(f"   -> Type: {dt}", flush=True)
        
        # 3. Check Data Samples (Estado and Fecha)
        print("\n3. Sample Data (Estado, Fecha):", flush=True)
        cursor.execute("SELECT estado_contrato_a, fecha_fin_contrato_a FROM contratos_arrendamientos LIMIT 5")
        for r in cursor.fetchall():
            print(f"   -> {r}", flush=True)
            
        # 4. Simulate Service Query
        print("\n4. Simulating App Query:", flush=True)
        dias_antelacion = 90
        fecha_limite = (datetime.now() + timedelta(days=dias_antelacion)).strftime("%Y-%m-%d")
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")
        print(f"   Params: <= {fecha_limite} AND >= {fecha_hoy}", flush=True)
        
        query = """
        SELECT count(*)
        FROM CONTRATOS_ARRENDAMIENTOS ca
        WHERE ca.ESTADO_CONTRATO_A = 'Activo'
          AND ca.FECHA_FIN_CONTRATO_A <= %s
          AND ca.FECHA_FIN_CONTRATO_A >= %s
        """
        cursor.execute(query, (fecha_limite, fecha_hoy))
        ct = cursor.fetchone()
        val = list(ct.values())[0] if hasattr(ct, 'values') else ct[0]
        print(f"   -> Matches: {val}", flush=True)
        
        # 5. Simulate App Query with Cast (Like View)
        print("\n5. Query with CAST (::date):", flush=True)
        query_cast = """
        SELECT count(*)
        FROM CONTRATOS_ARRENDAMIENTOS ca
        WHERE ca.ESTADO_CONTRATO_A = 'Activo'
          AND ca.FECHA_FIN_CONTRATO_A::date <= %s::date
          AND ca.FECHA_FIN_CONTRATO_A::date >= %s::date
        """
        cursor.execute(query_cast, (fecha_limite, fecha_hoy))
        ct = cursor.fetchone()
        val = list(ct.values())[0] if hasattr(ct, 'values') else ct[0]
        print(f"   -> Matches with CAST: {val}", flush=True)

    except Exception as e:
        print(f"[ERROR] {e}", flush=True)
        conn.rollback()

if __name__ == "__main__":
    debug_query()
