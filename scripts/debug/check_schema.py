import sqlite3

conn = sqlite3.connect('inmobiliaria_velar.db')
cursor = conn.cursor()

# Get the CREATE TABLE statement for LIQUIDACIONES_ASESORES
cursor.execute("SELECT sql FROM sqlite_master WHERE name='LIQUIDACIONES_ASESORES'")
result = cursor.fetchone()

print("=== SCHEMA ACTUAL DE LIQUIDACIONES_ASESORES ===\n")
if result:
    print(result[0])
else:
    print("Tabla no encontrada")

# Check what CONTRATOS tables exist
print("\n\n=== TABLAS RELACIONADAS CON CONTRATOS ===\n")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%CONTRATO%' ORDER BY name")
tables = cursor.fetchall()

for table in tables:
    print(f"  - {table[0]}")

conn.close()
