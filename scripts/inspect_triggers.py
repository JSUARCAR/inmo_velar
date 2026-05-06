import sqlite3

DB_PATH = r"c:\Users\PC\OneDrive\Desktop\inmobiliaria velar\PYTHON-FLET\DB_Inmo_Velar.db"

def inspect_triggers():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='trigger' AND tbl_name='CONTRATOS_ARRENDAMIENTOS'")
        triggers = cursor.fetchall()
        
        print(f"Found {len(triggers)} triggers for CONTRATOS_ARRENDAMIENTOS:")
        for name, sql in triggers:
            print(f"--- TRIGGER: {name} ---")
            print(sql)
            print("-------------------------")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    inspect_triggers()
