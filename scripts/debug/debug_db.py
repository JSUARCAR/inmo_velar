import sqlite3

DB_PATH = "DB_Inmo_Velar.db"

def inspect_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("=== TRIGGERS ===")
        cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='trigger'")
        for row in cursor.fetchall():
            print(f"Trigger: {row[0]}")
            print(f"SQL: {row[1]}")
            print("-" * 20)

        print("\n=== COLUMNS: CONTRATOS_ARRENDAMIENTOS ===")
        cursor.execute("PRAGMA table_info(CONTRATOS_ARRENDAMIENTOS)")
        for row in cursor.fetchall():
            print(row)

        print("\n=== COLUMNS: AUDITORIA_CAMBIOS ===")
        cursor.execute("PRAGMA table_info(AUDITORIA_CAMBIOS)")
        for row in cursor.fetchall():
            print(row)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn: conn.close()

if __name__ == "__main__":
    inspect_db()
