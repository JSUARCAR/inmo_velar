"""
Verificar estructura tabla USUARIOS
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

# Ver estructura de USUARIOS
cursor.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'usuarios'
    ORDER BY ordinal_position
""")

print("Columnas en tabla USUARIOS:")
for row in cursor.fetchall():
    print(f"  - {row[0]}: {row[1]}")

# Ver datos del usuario admin
cursor.execute("SELECT * FROM USUARIOS WHERE nombre_usuario = 'admin' LIMIT 1")
columns = [desc[0] for desc in cursor.description]
result = cursor.fetchone()

if result:
    print("\nDatos usuario admin:")
    for col, val in zip(columns, result):
        print(f"  {col}: {val}")

cursor.close()
conn.close()
