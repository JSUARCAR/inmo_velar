import sqlite3

# Conectar a la base de datos CORRECTA
conn = sqlite3.connect('DB_Inmo_Velar.db')
cursor = conn.cursor()

# Get ALL tables
print("=== TODAS LAS TABLAS EN DB_Inmo_Velar.db ===\n")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()

for table in tables:
    print(f"  - {table[0]}")

# Check for liquidacion tables
print("\n\n=== TABLAS DE LIQUIDACION ===\n")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%LIQUIDACION%' ORDER BY name")
liq_tables = cursor.fetchall()

if liq_tables:
    for table in liq_tables:
        print(f"  - {table[0]}")
else:
    print("No hay tablas de liquidacion")

conn.close()
