import os
import sys
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# Source: Local PostgreSQL
SRC_HOST = "localhost"
SRC_PORT = 5432
SRC_DB = "db_inmo_velar"
SRC_USER = "inmo_user"
SRC_PASSWORD = "7323"

# Destination: Railway
DEST_URL = os.getenv("DATABASE_URL")

def get_columns(conn, schema='public'):
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT table_name, column_name, data_type 
        FROM information_schema.columns 
        WHERE table_schema = '{schema}'
    """)
    cols = {}
    for table, col, dtype in cursor.fetchall():
        if table not in cols:
            cols[table] = {}
        cols[table][col] = dtype
    return cols

def sync_schema():
    print("Connecting to Source (Local)...")
    src_conn = psycopg2.connect(host=SRC_HOST, port=SRC_PORT, database=SRC_DB, user=SRC_USER, password=SRC_PASSWORD)
    src_cols = get_columns(src_conn)
    src_conn.close()

    print("Connecting to Destination (Railway)...")
    dest_conn = psycopg2.connect(DEST_URL)
    dest_cols = get_columns(dest_conn)
    dest_cursor = dest_conn.cursor()

    print("--- SYNCING COLUMNS ---")
    for table, columns in src_cols.items():
        if table not in dest_cols:
            print(f"⚠️ Table {table} missing in Destination (Full migration script should create it if code exists, but ignoring for now)")
            continue
            
        for col, dtype in columns.items():
            if col not in dest_cols[table]:
                print(f"➕ Adding missing column: {table}.{col} ({dtype})")
                mapped_type = dtype
                if dtype == 'character varying':
                    mapped_type = 'TEXT' # Simplify
                elif dtype == 'integer':
                    mapped_type = 'INTEGER'
                elif dtype == 'boolean':
                    mapped_type = 'BOOLEAN'
                elif 'timestamp' in dtype:
                    mapped_type = 'TIMESTAMP'
                
                try:
                    dest_cursor.execute(f'ALTER TABLE "{table}" ADD COLUMN IF NOT EXISTS "{col}" {mapped_type}')
                    dest_conn.commit()
                    print(f"   ✅ Added.")
                except Exception as e:
                    print(f"   ❌ Failed to add {col}: {e}")
                    dest_conn.rollback()

    print("Schema sync check complete.")
    dest_conn.close()

if __name__ == "__main__":
    sync_schema()
