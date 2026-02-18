import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infraestructura.persistencia.database import db_manager

def check_env():
    print("=== ENVIRONMENT CHECK ===", flush=True)
    try:
        conn = db_manager.obtener_conexion()
        cursor = conn.cursor()
        
        # User/DB
        cursor.execute("SELECT current_user, current_database()")
        u, d = list(cursor.fetchone().values()) if hasattr(cursor.fetchone(), 'values') else cursor.fetchone() # Wrapper returns dict?
        # Actually fetchone returns dict {Col: Val} due to wrapper
        # The keys will be UPPERCASE: CURRENT_USER, CURRENT_DATABASE
        # Let's inspect the dict
        cursor.execute("SELECT current_user, current_database()")
        res = cursor.fetchone()
        print(f"Connected as: {res}", flush=True)
        
        # Schemas
        print("\n[SCHEMAS]", flush=True)
        cursor.execute("SELECT schema_name FROM information_schema.schemata")
        for r in cursor.fetchall():
            print(list(r.values())[0], flush=True)
            
        # Tables matching 'contratos'
        print("\n[TABLES MATCHING 'contratos']", flush=True)
        cursor.execute("SELECT table_schema, table_name FROM information_schema.tables WHERE table_name LIKE '%contratos%'")
        for r in cursor.fetchall():
            print(r, flush=True)
            
        # Count in public.contratos_arrendamientos
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
    check_env()
