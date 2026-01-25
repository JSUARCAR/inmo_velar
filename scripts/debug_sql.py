import psycopg2
import traceback

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
    print("Connecting...")
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    print("Reading SQL...")
    with open(SQL_FILE, 'r', encoding='utf-8') as f:
        sql = f.read()

    print("Executing SQL...")
    cursor.execute(sql)
    
    print("SUCCESS!")
    
    conn.close()

except Exception as e:
    print("\n" + "=" * 70)
    print("DETAILED ERROR:")
    print("=" * 70)
    print(f"Error Type: {type(e).__name__}")
    print(f"Error Message: {str(e)}")
    print("\nFull Traceback:")
    traceback.print_exc()
    print("=" * 70)
    exit(1)
