import psycopg2

DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "db_inmo_velar"
DB_USER = "postgres"
DB_PASSWORD = "7323"
SQL_FILE = "src/infraestructura/db/migrations/fix_audit_postgres_full.sql"

try:
    print("Connecting to PostgreSQL...")
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    print(f"Reading comprehensive audit script: {SQL_FILE}")
    with open(SQL_FILE, 'r', encoding='utf-8') as f:
        sql = f.read()

    print("Applying comprehensive audit triggers...")
    cursor.execute(sql)
    
    print("\n[SUCCESS] Comprehensive audit system installed!")
    print("All tables are now being monitored for INSERT, UPDATE, DELETE operations.")
    
    conn.close()

except Exception as e:
    print(f"[ERROR] {e}")
    exit(1)
