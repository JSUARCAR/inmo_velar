import psycopg2
import os

# Config from .env
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "db_inmo_velar"
DB_USER = "postgres"
DB_PASSWORD = "7323"

try:
    print(f"Connecting to PostgreSQL: {DB_NAME} at {DB_HOST}...")
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = conn.cursor()
    
    tables = ["USUARIOS", "PERSONAS", "PROPIEDADES", "CONTRATOS_ARRENDAMIENTOS"]
    # Postgres stores table names usually in lowercase if not quoted, but let's check uppercase too
    # Actually information_schema stores them as is. If created without quotes, they are likely lowercase? 
    # Or uppercase if created with quotes?
    # Let's check matching ignoring case.

    print("--- Checking for UPDATED_BY column in PostgreSQL ---")
    
    for table_name in tables:
        # Check if table exists (case insensitive)
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND UPPER(table_name) = %s
        """, (table_name,))
        
        found_table = cursor.fetchone()
        
        if not found_table:
            print(f"[ERROR] Table {table_name} NOT FOUND")
            continue
            
        real_table_name = found_table[0]
        
        # Check columns
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = %s
        """, (real_table_name,))
        
        columns = [row[0].upper() for row in cursor.fetchall()]
        
        if "UPDATED_BY" in columns:
            print(f"[OK] {table_name} (found as {real_table_name}) has UPDATED_BY")
        else:
            print(f"[FAIL] {table_name} (found as {real_table_name}) MISSING UPDATED_BY")

    conn.close()

except Exception as e:
    print(f"[CRITICAL ERROR] {e}")
