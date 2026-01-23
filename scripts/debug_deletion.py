import sqlite3
import time

DB_PATH = r"c:\Users\PC\OneDrive\Desktop\inmobiliaria velar\PYTHON-FLET\DB_Inmo_Velar.db"
TABLA = "CONTRATOS_ARRENDAMIENTOS"
TABLA2 = "PROVEEDORES"

def debug_deletion():
    print(f"DEBUG: Intentando abrir DB")
    try:
        conn = sqlite3.connect(DB_PATH, timeout=20)
        cursor = conn.cursor()
        
        print("DEBUG: PRAGMA foreign_keys = OFF")
        cursor.execute("PRAGMA foreign_keys = OFF;")
        
        # Check count
        c1 = cursor.execute(f"SELECT COUNT(*) FROM {TABLA}").fetchone()[0]
        c2 = cursor.execute(f"SELECT COUNT(*) FROM {TABLA2}").fetchone()[0]
        print(f"DEBUG: Counts pre-delete: {TABLA}={c1}, {TABLA2}={c2}")
        
        print("DEBUG: BEGIN TRANSACTION")
        cursor.execute("BEGIN TRANSACTION;")
        
        print(f"DEBUG: DELETE FROM {TABLA}")
        cursor.execute(f"DELETE FROM {TABLA}")
        
        print(f"DEBUG: DELETE FROM {TABLA2}")
        cursor.execute(f"DELETE FROM {TABLA2}")
        
        print("DEBUG: COMMIT")
        conn.commit()
        
        c1_after = cursor.execute(f"SELECT COUNT(*) FROM {TABLA}").fetchone()[0]
        c2_after = cursor.execute(f"SELECT COUNT(*) FROM {TABLA2}").fetchone()[0]
        print(f"DEBUG: Counts post-delete: {TABLA}={c1_after}, {TABLA2}={c2_after}")
        
    except Exception as e:
        print(f"DEBUG ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    debug_deletion()
