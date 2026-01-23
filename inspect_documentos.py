import psycopg2
import os

# Create direct connection based on inspect_postgres.py credentials
# Ideally should load from .env but hardcoded for speed as in inspect_postgres.py
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "db_inmo_velar"
DB_USER = "postgres"
DB_PASSWORD = "7323"

try:
    print(f"Connecting to PostgreSQL: {DB_NAME}...")
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = conn.cursor()
    
    table_name = "DOCUMENTOS"
    print(f"--- Inspecting {table_name} ---")
    
    # Check if table exists
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND UPPER(table_name) = %s
    """, (table_name,))
    
    found = cursor.fetchone()
    if not found:
        print(f"Table {table_name} NOT FOUND")
    else:
        real_name = found[0]
        print(f"Found table: {real_name}")
        
        cursor.execute("""
            SELECT column_name, data_type, udt_name 
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = %s
            ORDER BY ordinal_position
        """, (real_name,))
        
        rows = cursor.fetchall()
        for row in rows:
            print(f"Column: {row[0]} | Type: {row[1]} | UDT: {row[2]}")

    conn.close()

except Exception as e:
    print(f"Error: {e}")
