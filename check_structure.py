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

# Ver estructura de tabla
cur.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE LOWER(table_name) = 'descuentos_asesores' 
    ORDER BY ordinal_position
""")

print("Columnas de DESCUENTOS_ASESORES:")
for col in cur.fetchall():
    print(f"  - {col[0]} ({col[1]})")

# Ver un sample
cur.execute("SELECT * FROM DESCUENTOS_ASESORES LIMIT 1")
print("\nSample row:")
if cur.description:
    cols = [desc[0] for desc in cur.description]
    print(f"Columns: {cols}")
    row = cur.fetchone()
    if row:
        for col, val in zip(cols, row):
            print(f"  {col}: {val}")

cur.close()
conn.close()
