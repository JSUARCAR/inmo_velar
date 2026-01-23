import psycopg2
import os

DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "db_inmo_velar"
DB_USER = "postgres"
DB_PASSWORD = "7323"

try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = conn.cursor()
    
    print("--- Checking content of DOCUMENTOS ---")
    cursor.execute("SELECT id, es_vigente FROM DOCUMENTOS LIMIT 5")
    rows = cursor.fetchall()
    
    if not rows:
        print("Table is empty")
    else:
        for row in rows:
            print(f"ID: {row[0]} | es_vigente: '{row[1]}' (Type: {type(row[1])})")

    conn.close()

except Exception as e:
    print(f"Error: {e}")
