import sqlite3
import os

# Get correct database path  
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "DB_Inmo_Velar.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("=== Listando todas las tablas de la base de datos ===\n")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
tables = cursor.fetchall()

print(f"Total de tablas: {len(tables)}\n")
for table in tables:
    print(f"  - {table[0]}")

print("\n=== Buscando tablas con 'CONTRATO' ===\n")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%CONTRATO%' ORDER BY name;")
contract_tables = cursor.fetchall()

if contract_tables:
    for table in contract_tables:
        print(f"  - {table[0]}")
else:
    print("  (No se encontraron tablas con 'CONTRATO')")

conn.close()
