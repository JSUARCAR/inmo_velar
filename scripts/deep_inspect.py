import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infraestructura.persistencia.database import db_manager

def deep_inspect():
    print("=== DEEP INSPECT ===", flush=True)
    try:
        conn = db_manager.obtener_conexion()
        cursor = conn.cursor()
        
        # List all relations (tables, views, etc)
        query = """
        SELECT n.nspname as schema, c.relname as name, c.relkind as type
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE c.relname ILIKE '%contratos%'
        ORDER BY 1, 2
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        
        for r in rows:
            # Handle dict wrapper
            if hasattr(r, 'values'):
                vals = list(r.values())
                # Dict keys might be upper case
                # SCHEMA, NAME, TYPE
                # But order is preserved in values list usually?
                # Let's rely on keys if possible
                schema = r.get('SCHEMA') or r.get('schema') or vals[0]
                name = r.get('NAME') or r.get('name') or vals[1]
                kind = r.get('TYPE') or r.get('type') or vals[2]
            else:
                schema, name, kind = r
                
            print(f"Found: {schema}.{name} (Type: {kind})", flush=True)
            
            # If it's a table (r) or view (v) or matview (m), try to count
            if kind in ('r', 'v', 'm', 'f', 'p'):
                try:
                    q_count = f"SELECT count(*) FROM {schema}.\"{name}\""
                    cursor.execute(q_count)
                    res = cursor.fetchone()
                    count = list(res.values())[0] if hasattr(res, 'values') else res[0]
                    print(f"   -> Count: {count}", flush=True)
                except Exception as e:
                    print(f"   -> Error counting: {e}", flush=True)
                    conn.rollback()

    except Exception as e:
        print(f"Error: {e}", flush=True)

if __name__ == "__main__":
    deep_inspect()
