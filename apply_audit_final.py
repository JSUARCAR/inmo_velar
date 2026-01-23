import psycopg2

DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "db_inmo_velar"
DB_USER = "postgres"
DB_PASSWORD = "7323"
SQL_FILE = "src/infraestructura/db/migrations/audit_full_final.sql"

try:
    print("=" * 70)
    print("COMPREHENSIVE AUDIT SYSTEM INSTALLATION")
    print("=" * 70)
    print(f"\nConnecting to PostgreSQL database: {DB_NAME}...")
    
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    print(f"Reading SQL script: {SQL_FILE}")
    with open(SQL_FILE, 'r', encoding='utf-8') as f:
        sql = f.read()

    print("Applying comprehensive audit triggers to ALL tables...")
    print("This will enable tracking of:")
    print("  ✓ INSERT (create operations)")
    print("  ✓ UPDATE (modify operations)")
    print("  ✓ DELETE (delete operations)\n")
    
    cursor.execute(sql)
    
    # Count triggers
    cursor.execute("""
        SELECT COUNT(*) 
        FROM information_schema.triggers 
        WHERE trigger_schema = 'public' 
        AND trigger_name LIKE 'trg_audit_%'
    """)
    trigger_count = cursor.fetchone()[0]
    
    print("=" * 70)
    print(f"SUCCESS! {trigger_count} audit triggers installed.")
    print("=" * 70)
    print("\nAll tables are now being monitored.")
    print("Check the 'Auditoría' page to see logged changes.\n")
    
    conn.close()

except Exception as e:
    print(f"\n[ERROR] {e}")
    exit(1)
