import psycopg2

# Config from shared_db_config
try:
    from shared_db_config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
except ImportError:
    import sys
    import os
    # Add root to sys.path if running from subdir
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    try:
        from shared_db_config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
    except ImportError:
        # Fallback to env vars directly if shared config missing
        from dotenv import load_dotenv
        load_dotenv()
        DB_HOST = os.getenv("DB_HOST", "localhost")
        DB_PORT = os.getenv("DB_PORT", "5432")
        DB_NAME = os.getenv("DB_NAME", "db_inmo_velar")
        DB_USER = os.getenv("DB_USER", "inmo_user")
        DB_PASSWORD = os.getenv("DB_PASSWORD", "7323")

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
