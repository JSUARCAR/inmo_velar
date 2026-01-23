import psycopg2
import os

DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "db_inmo_velar"
DB_USER = "postgres"
DB_PASSWORD = "7323"
SQL_FILE = "src/infraestructura/db/migrations/fix_audit_postgres_v2.sql"

try:
    print(f"Connecting to PostgreSQL...")
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    conn.autocommit = True 
    cursor = conn.cursor()
    
    with open(SQL_FILE, 'r', encoding='utf-8') as f:
        sql = f.read()

    print("Executing V2 Fix...")
    cursor.execute(sql)
    print("[SUCCESS] V2 Fix Applied.")
    conn.close()

except Exception as e:
    print(f"[ERROR] {e}")
