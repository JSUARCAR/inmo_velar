import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infraestructura.persistencia.database import db_manager

def analyze_view():
    print("=== VIEW BREAKDOWN ===", flush=True)
    try:
        conn = db_manager.obtener_conexion()
        cursor = conn.cursor()
        
        # 1. Group by Type in View
        print("\n[View Composition]", flush=True)
        cursor.execute("SELECT tipo_contrato, count(*) FROM vw_alerta_vencimiento_contratos GROUP BY tipo_contrato")
        for r in cursor.fetchall():
            res = list(r.values()) if hasattr(r, 'values') else r
            print(f" - {res}", flush=True)

        # 2. Check Mandatos Table Count
        print("\n[Mandatos Table]", flush=True)
        cursor.execute("SELECT count(*) FROM contratos_mandatos")
        res = cursor.fetchone()
        val = list(res.values())[0] if hasattr(res, 'values') else res[0]
        print(f" - Total Mandatos: {val}", flush=True)

        # 3. Check Arrendamientos Old
        print("\n[Arrendamientos Old]", flush=True)
        try:
            cursor.execute("SELECT count(*) FROM contratos_arrendamientos_old")
            res = cursor.fetchone()
            val = list(res.values())[0] if hasattr(res, 'values') else res[0]
            print(f" - Total Old: {val}", flush=True)
        except:
            print(" - Table _old not found", flush=True)

        # 4. Check Arrendamientos (Again)
        print("\n[Arrendamientos Current]", flush=True)
        cursor.execute("SELECT count(*) FROM contratos_arrendamientos")
        res = cursor.fetchone()
        val = list(res.values())[0] if hasattr(res, 'values') else res[0]
        print(f" - Total Current: {val}", flush=True)

    except Exception as e:
        print(f"Error: {e}", flush=True)

if __name__ == "__main__":
    analyze_view()
