import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infraestructura.persistencia.database import db_manager

def check_path():
    print("=== SEARCH PATH CHECK ===", flush=True)
    try:
        with db_manager.obtener_conexion() as conn:
            cursor = conn.cursor()
            
            # Check search_path
            cursor.execute("SHOW search_path")
            res = cursor.fetchone()
            print(f"Search Path: {list(res.values())[0] if hasattr(res, 'values') else res}", flush=True)
            
            # List Schemas
            print("\n[SCHEMAS]", flush=True)
            cursor.execute("SELECT schema_name FROM information_schema.schemata")
            rows = cursor.fetchall()
            for r in rows:
                print(list(r.values())[0] if hasattr(r, 'values') else r, flush=True)

            # Count qualified vs unqualified
            print("\n[COUNTS]", flush=True)
            queries = [
                ("public.contratos_arrendamientos", "SELECT count(*) FROM public.contratos_arrendamientos"),
                ("unqualified contracts", "SELECT count(*) FROM contratos_arrendamientos")
            ]
            
            for label, q in queries:
                try:
                    cursor.execute(q)
                    res = cursor.fetchone()
                    val = list(res.values())[0] if hasattr(res, 'values') else res[0]
                    print(f"{label}: {val}", flush=True)
                except Exception as e:
                    print(f"{label}: ERROR {e}", flush=True)
                    conn.rollback()

    except Exception as e:
        print(f"Error: {e}", flush=True)

if __name__ == "__main__":
    check_path()
