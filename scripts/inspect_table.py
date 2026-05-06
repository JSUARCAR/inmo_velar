import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infraestructura.persistencia.database import db_manager

def inspect():
    print("=== INSPECTING TABLES ===", flush=True)
    try:
        with db_manager.obtener_conexion() as conn:
            cursor = conn.cursor()
            
            # 1. List all tables
            print("\n[ALL TABLES]", flush=True)
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            # Rows are dicts due to db_manager wrapper: {'TABLE_NAME': '...'}
            tables = [list(r.values())[0] for r in cursor.fetchall()] 
            for t in sorted(tables):
                print(f" - {t}", flush=True)
                
            # 2. Check strict counts
            target_table = "contratos_arrendamientos" # Lowercase check
            try:
                print(f"\n[COUNT] {target_table} ...", flush=True)
                cursor.execute(f"SELECT count(*) FROM {target_table}")
                res = cursor.fetchone()
                # res is dict {'COUNT': ...} or similar
                print(f" -> {list(res.values())[0]}", flush=True)
            except Exception as e:
                print(f" -> ERROR: {e}", flush=True)
                conn.rollback()

            target_table_upper = "CONTRATOS_ARRENDAMIENTOS" # Uppercase check
            try:
                print(f"\n[COUNT] {target_table_upper} ...", flush=True)
                cursor.execute(f"SELECT count(*) FROM {target_table_upper}")
                res = cursor.fetchone()
                print(f" -> {list(res.values())[0]}", flush=True)
            except Exception as e:
                print(f" -> ERROR: {e}", flush=True)
                conn.rollback()

            # 3. Check View Def
            print("\n[VIEW DEF]", flush=True)
            cursor.execute("SELECT definition FROM pg_views WHERE viewname = 'vw_alerta_vencimiento_contratos'")
            row = cursor.fetchone()
            if row:
                print(list(row.values())[0], flush=True)
            else:
                print("View def not found in pg_views", flush=True)
                
            # 4. Check Contract Statuses
            print("\n[STATUSES IN CONTRATOS_ARRENDAMIENTOS]", flush=True)
            try:
                cursor.execute("SELECT DISTINCT ESTADO_CONTRATO_A FROM CONTRATOS_ARRENDAMIENTOS")
                rows = cursor.fetchall()
                print([list(r.values())[0] for r in rows], flush=True)
            except Exception as e:
                print(f"Error checking status: {e}", flush=True)

    except Exception as e:
        print(f"[FATAL] {e}", flush=True)

if __name__ == "__main__":
    inspect()
