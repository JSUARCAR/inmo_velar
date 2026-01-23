import psycopg2
import os

# Config from .env
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "db_inmo_velar"
DB_USER = "postgres"
DB_PASSWORD = "7323"
SQL_FILE = "src/infraestructura/db/migrations/fix_audit_postgres.sql"

if not os.path.exists(SQL_FILE):
    print(f"[ERROR] SQL file not found: {SQL_FILE}")
    exit(1)

try:
    print(f"Connecting to PostgreSQL: {DB_NAME} at {DB_HOST}...")
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    conn.autocommit = True # Allow CREATE FUNCTION/TRIGGER
    cursor = conn.cursor()
    
    print(f"Reading SQL script: {SQL_FILE}")
    with open(SQL_FILE, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    print("Executing SQL script...")
    cursor.execute(sql_content)
    
    print("[SUCCESS] Audit triggers applied successfully.")
    conn.close()

except Exception as e:
    print(f"[CRITICAL ERROR] {e}")
    exit(1)
