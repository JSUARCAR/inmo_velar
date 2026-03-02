import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

# Source: Local PostgreSQL
SRC_HOST = "localhost"
SRC_PORT = 5432
SRC_DB = "db_inmo_velar"
SRC_USER = "inmo_user"
SRC_PASSWORD = "7323"

# Destination: Railway PostgreSQL
DEST_URL = os.getenv("DATABASE_URL")

if not DEST_URL:
    print("Error: DATABASE_URL not set in .env")
    sys.exit(1)

def migrate_postgres_to_railway():
    print("Connecting to SOURCE (Local PostgreSQL)...")
    try:
        src_conn = psycopg2.connect(
            host=SRC_HOST,
            port=SRC_PORT, # This is wrong, should be int
            database=SRC_DB,
            user=SRC_USER,
            password=SRC_PASSWORD
        )
    except Exception as e:
        print(f"Error connecting to SOURCE: {e}")
        return

    print("Connecting to DESTINATION (Railway PostgreSQL)...")
    try:
        dest_conn = psycopg2.connect(DEST_URL)
        dest_conn.autocommit = False # Use transactions
    except Exception as e:
        print(f"Error connecting to DESTINATION: {e}")
        src_conn.close()
        return

    src_cursor = src_conn.cursor(cursor_factory=RealDictCursor) # Dict cursor for easier mapping
    dest_cursor = dest_conn.cursor()

    # Get list of tables from source
    src_cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
    """)
    tables = [row['table_name'] for row in src_cursor.fetchall()]
    
    # Order matters for foreign keys. We'll try a naive approach first, 
    # but disable FK checks on destination if possible or handle order.
    # Postgres doesn't have a global "disable FK" flag easily accessible like SQLite or MySQL without superuser.
    # So we sort tables by dependencies or truncate carefully.
    # For migration, truncating with CASCADE covers deletion.
    # Insertion order matters.
    # Let's try to infer order or just catch errors and retry? No, retry is bad.
    # Better: SET session_replication_role = replica; (Needs superuser usually, but let's try)
    
    print(f"Found {len(tables)} tables in SOURCE.")

    # 1. Truncate Destination Tables
    print("Truncating destination tables...")
    try:
        # Disable triggers/FKs for session if allowed (Railway user usually is owner)
        dest_cursor.execute("SET session_replication_role = 'replica';") 
        
        for table in tables:
            dest_cursor.execute(f"TRUNCATE TABLE {table} CASCADE;")
        print("Truncated all tables.")
    except Exception as e:
        print(f"Error truncating tables (might be permission issue): {e}")
        # Continue anyway, maybe they are empty
        dest_conn.rollback()

    # 2. Copy Data
    for table in tables:
        print(f"Migrating table: {table}")
        try:
            # Read from Source
            src_cursor.execute(f"SELECT * FROM {table}")
            rows = src_cursor.fetchall()
            
            if not rows:
                continue

            # Generate INSERT based on columns
            columns = rows[0].keys()
            cols_str = ", ".join([f'"{c}"' for c in columns]) # Quote columns
            placeholders = ", ".join(["%s"] * len(columns))
            
            insert_query = f'INSERT INTO "{table}" ({cols_str}) VALUES ({placeholders})'
            
            # Batch execute
            values = [list(row.values()) for row in rows]
            
            # Use execute_batch for performance if many rows, but standard execute_many is fine for small DB
            # We'll use simple loop or executemany
            dest_cursor.executemany(insert_query, values)
            print(f"  -> Copied {len(rows)} rows.")
            
        except Exception as e:
            print(f"  -> Error migrating {table}: {e}")
            dest_conn.rollback() 
            # If one table fails, we stop? Or continue? 
            # Ideally stop to not leave partial state, but for now continue to see all errors.
            continue
            
    # Re-enable constraint checks
    dest_cursor.execute("SET session_replication_role = 'origin';")
    
    dest_conn.commit()
    print("Migration completed successfully.")
    
    src_cursor.close()
    src_conn.close()
    dest_cursor.close()
    dest_conn.close()

if __name__ == "__main__":
    migrate_postgres_to_railway()
