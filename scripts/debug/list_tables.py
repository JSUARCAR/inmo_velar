import sqlite3

conn = sqlite3.connect('inmobiliaria_velar.db')
cursor = conn.cursor()

# Get ALL tables
print("=== TODAS LAS TABLAS EN LA BASE DE DATOS ===\n")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()

for table in tables:
    print(f"  - {table[0]}")

# Specifically check for contract tables
print("\n\n=== BUSCANDO TABLAS DE CONTRATOS ===\n")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name LIKE '%CONTRATO%' OR name LIKE '%ARRENDA%') ORDER BY name")
contract_tables = cursor.fetchall()

if contract_tables:
    for table in contract_tables:
        print(f"ENCONTRADA: {table[0]}")
else:
    print("No se encontraron tablas de contratos")

conn.close()
