import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="db_inmo_velar",
    user="postgres",
    password=os.getenv("DB_PASSWORD", "")
)

cur = conn.cursor()

# Ver estructura de tabla LIQUIDACIONES_ASESORES
cur.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE LOWER(table_name) = 'liquidaciones_asesores' 
    ORDER BY ordinal_position
""")

print("="*70)
print("Columnas de LIQUIDACIONES_ASESORES:")
print("="*70)
for col in cur.fetchall():
    print(f"  - {col[0]:30} ({col[1]})")

# Verificar si los duplicados fueron eliminados
cur.execute("SELECT COUNT(*) FROM DESCUENTOS_ASESORES")
total_desc = cur.fetchone()[0]
print(f"\n✓ Total descuentos restantes en BD: {total_desc:,}")

cur.close()
conn.close()
