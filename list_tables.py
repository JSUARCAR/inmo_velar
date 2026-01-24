import psycopg2
import os

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


try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = conn.cursor()
    
    # Get all public tables
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """)
    tables = cursor.fetchall()
    
    print("--- Database Tables & Analyzed PKs ---")
    
    skipped_tables = ['auditoria_cambios', 'alembic_version', 'spatial_ref_sys']
    
    for t in tables:
        table_name = t[0]
        if table_name in skipped_tables:
            continue
            
        # Try to guess PK or find ID column
        # Usually ID_{TABLE_NAME_SINGULAR} or ID_{TABLE_NAME}
        
        cursor.execute(f"""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}' 
            AND column_name LIKE 'id_%'
            ORDER BY ordinal_position
            LIMIT 1
        """)
        col = cursor.fetchone()
        pk_col = col[0] if col else "UNKNOWN"
        
        print(f"Table: {table_name:<30} | PK Guess: {pk_col}")

    conn.close()

except Exception as e:
    print(f"[ERROR] {e}")
