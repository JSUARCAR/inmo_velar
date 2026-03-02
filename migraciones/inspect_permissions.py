import sqlite3
import os

DB_PATH = "migraciones/DB_Inmo_Velar.db"

def inspect_permissions_tables():
    if not os.path.exists(DB_PATH):
        print(f"Error: {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    tables_to_check = ["PERMISOS", "ROL_PERMISOS", "ROLES"]
    
    for table in tables_to_check:
        print(f"\n--- Searching for {table} ---")
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
        res = cursor.fetchone()
        if res:
            print(f"Found table: {table}")
            cursor.execute(f"PRAGMA table_info({table})")
            for col in cursor.fetchall():
                print(col)
        else:
            print(f"Table {table} NOT found.")

    conn.close()

if __name__ == "__main__":
    inspect_permissions_tables()
