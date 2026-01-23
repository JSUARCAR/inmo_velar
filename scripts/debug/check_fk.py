import sqlite3

conn = sqlite3.connect('DB_Inmo_Velar.db')
cursor = conn.cursor()

print("=== SCHEMA DE LIQUIDACIONES_ASESORES ===\n")
cursor.execute("SELECT sql FROM sqlite_master WHERE name='LIQUIDACIONES_ASESORES'")
result = cursor.fetchone()

if result:
    print(result[0])
    
    # Check foreign keys
    print("\n\n=== FOREIGN KEYS DE LIQUIDACIONES_ASESORES ===\n")
    cursor.execute("PRAGMA foreign_key_list(LIQUIDACIONES_ASESORES)")
    fks = cursor.fetchall()
    
    for fk in fks:
        print(f"  - id={fk[0]}, table={fk[2]}, from={fk[3]}, to={fk[4]}")

conn.close()
