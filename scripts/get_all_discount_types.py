"""
Get ALL unique discount types from database - comprehensive query
"""
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", 5432)),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

cursor = conn.cursor()

# Get ALL unique discount types
cursor.execute("""
    SELECT DISTINCT tipo_descuento, COUNT(*) as cantidad
    FROM DESCUENTOS_ASESORES
    WHERE tipo_descuento IS NOT NULL AND tipo_descuento != ''
    GROUP BY tipo_descuento
    ORDER BY tipo_descuento
""")

print("TODOS los tipos de descuento en la base de datos:")
print("="*70)

all_types = []
for row in cursor.fetchall():
    tipo = row[0]
    count = row[1]
    all_types.append(tipo)
    print(f"  '{tipo}' - {count} registros")

print("="*70)
print(f"\nTotal de tipos únicos: {len(all_types)}")
print("\nLista Python para TIPOS_DESCUENTO:")
print(f"TIPOS_DESCUENTO = {sorted(all_types)}")

cursor.close()
conn.close()
