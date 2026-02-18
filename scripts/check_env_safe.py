import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infraestructura.persistencia.database import db_manager

def check_env_safe():
    print("=== ENVIRONMENT CHECK (SAFE) ===", flush=True)
    try:
        conn = db_manager.obtener_conexion()
        cursor = conn.cursor()
        
        # User/DB
        print("[USER/DB]", flush=True)
        cursor.execute("SELECT current_user, current_database()")
        res = cursor.fetchone()
        print(f" -> {res}", flush=True)
        
        # Schemas
        print("\n[SCHEMAS]", flush=True)
        cursor.execute("SELECT schema_name FROM information_schema.schemata")
        rows = cursor.fetchall()
        for r in rows:
            print(r, flush=True)
            
        # Tables matching 'contratos'
        print("\n[TABLES MATCHING 'contratos']", flush=True)
        cursor.execute("SELECT table_schema, table_name FROM information_schema.tables WHERE table_name LIKE '%contratos%'")
        rows = cursor.fetchall()
        for r in rows:
            print(r, flush=True)
            
        # Count in public.contratos_arrendamientos (using explicit schema)
        print("\n[COUNT public.contratos_arrendamientos]", flush=True)
        try:
            cursor.execute("SELECT count(*) FROM public.contratos_arrendamientos")
            res = cursor.fetchone()
            print(f" -> {res}", flush=True)
        except Exception as e:
            print(f" -> ERROR: {e}", flush=True)
            conn.rollback()

    except Exception as e:
        print(f"Error: {e}", flush=True)

if __name__ == "__main__":
    check_env_safe()
