import sqlite3
import os

DB_PATH = "migraciones/DB_Inmo_Velar.db" 

if not os.path.exists(DB_PATH):
    print(f"Database not found at {DB_PATH}")
    # Search for any .db file
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".db"):
                print(f"Found DB at: {os.path.join(root, file)}")
else:
    print(f"Checking DB at: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    tables = ["USUARIOS", "PERSONAS", "PROPIEDADES", "CONTRATOS_ARRENDAMIENTOS"]
    
    print("--- Checking for UPDATED_BY column ---")
    
    for table in tables:
        try:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            
            if not columns:
                print(f"[ERROR] Table {table} NOT FOUND")
                continue

            col_names = [col[1] for col in columns]
            
            if "UPDATED_BY" in col_names:
                print(f"[OK] {table} has UPDATED_BY")
            else:
                print(f"[FAIL] {table} MISSING UPDATED_BY")
                
        except Exception as e:
            print(f"[ERROR] Could not check {table}: {e}")
            
    conn.close()
