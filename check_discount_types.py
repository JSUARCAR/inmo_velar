"""
Investigar tipos de descuento que existen en la BD
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

# Obtener todos los tipos ÚNICOS de descuentos que existen
cursor.execute("""
    SELECT DISTINCT tipo_descuento, COUNT(*) as cantidad
    FROM DESCUENTOS_ASESORES
    WHERE tipo_descuento IS NOT NULL
    GROUP BY tipo_descuento
    ORDER BY cantidad DESC
""")

print("Tipos de descuento en la base de datos:")
print("="*60)
for row in cursor.fetchall():
    print(f"  {row[0]:<30} ({row[1]} registros)")
print("="*60)

cursor.close()
conn.close()
