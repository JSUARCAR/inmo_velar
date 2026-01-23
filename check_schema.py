import psycopg2
import sys

try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="db_inmo_velar",
        user="postgres",
        password="7323"
    )
    
    cur = conn.cursor()
    
    # Get RECAUDOS columns
    cur.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'recaudos'
        ORDER BY ordinal_position
    """)
    
    print("RECAUDOS_COLUMNS:")
    for row in cur.fetchall():
        print(f"{row[0]}|{row[1]}")
    
    # Check for concepto tables
    cur.execute("""
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public' AND tablename LIKE '%concepto%'
    """)
    
    print("CONCEPTO_TABLES:")
    for row in cur.fetchall():
        print(row[0])
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
