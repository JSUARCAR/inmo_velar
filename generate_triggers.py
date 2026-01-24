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


try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = conn.cursor()
    
    # Get all tables with their PK columns
    cursor.execute("""
        SELECT DISTINCT t.table_name,
               c.column_name as pk_column
        FROM information_schema.tables t
        LEFT JOIN information_schema.columns c 
            ON t.table_name = c.table_name 
            AND c.column_name LIKE 'id_%'
            AND c.ordinal_position = (
                SELECT MIN(ordinal_position)
                FROM information_schema.columns c2
                WHERE c2.table_name = t.table_name
                AND c2.column_name LIKE 'id_%'
            )
        WHERE t.table_schema = 'public' 
        AND t.table_type = 'BASE TABLE'
        AND t.table_name NOT IN ('auditoria_cambios', 'alembic_version', 'spatial_ref_sys')
        ORDER BY t.table_name
    """)
    
    tables = cursor.fetchall()
    
    print("=== EXISTING TABLES ===")
    for table_name, pk_col in tables:
        print(f"{table_name:<40} | PK: {pk_col or 'NONE'}")
    
    print(f"\nTotal: {len(tables)} tables")
    
    # Generate trigger SQL
    print("\n=== GENERATED TRIGGER STATEMENTS ===")
    for table_name, pk_col in tables:
        trigger_name = f"trg_audit_{table_name}"
        print(f"CREATE TRIGGER {trigger_name} AFTER INSERT OR UPDATE OR DELETE ON {table_name} FOR EACH ROW EXECUTE FUNCTION func_auditoria_cambios();")
    
    conn.close()

except Exception as e:
    print(f"[ERROR] {e}")
