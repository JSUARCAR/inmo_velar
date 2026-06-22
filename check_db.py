import sqlite3

def check():
    conn = sqlite3.connect('migraciones/DB_Inmo_Velar.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    print("Tables:", [r[0] for r in cursor.fetchall()])
    
    # Check CONTRATOS_MANDATO schema if exists
    cursor.execute("PRAGMA table_info(CONTRATO_MANDATO)")
    print("CONTRATO_MANDATO schema:", cursor.fetchall())

    cursor.execute("PRAGMA table_info(CONTRATOS_MANDATO)")
    print("CONTRATOS_MANDATO schema:", cursor.fetchall())

check()
