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

def create_table():
    print("Connecting to Local...")
    src_conn = psycopg2.connect(host=SRC_HOST, port=SRC_PORT, database=SRC_DB, user=SRC_USER, password=SRC_PASSWORD)
    src_cursor = src_conn.cursor()
    
    # Get columns
    src_cursor.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns 
        WHERE table_name = 'bonificaciones_asesores'
    """)
    cols = src_cursor.fetchall()
    src_conn.close()
    
    if not cols:
        print("Could not find columns for 'bonificaciones_asesores' in Local!")
        # Debug: list all tables
        # ...
        return

    print(f"Found {len(cols)} columns.")
    
    create_sql = 'CREATE TABLE IF NOT EXISTS "bonificaciones_asesores" ('
    defs = []
    
    # Infer PK (id usually)
    has_id = False
    
    for name, dtype, nullable in cols:
        if name == 'id': # common convention
             defs.append(f'"{name}" SERIAL PRIMARY KEY')
             has_id = True
             continue
             
        # Type mapping
        ptype = dtype
        if dtype == 'character varying': ptype = 'TEXT'
        
        null_str = "NULL" if nullable == 'YES' else "NOT NULL"
        defs.append(f'"{name}" {ptype} {null_str}')
    
    create_sql += ",\n".join(defs)
    if not has_id:
         # simple fallback
         pass
    create_sql += ");"
    
    print("Generated SQL:", create_sql)
    
    print("Connecting to Railway...")
    dest_conn = psycopg2.connect(DEST_URL)
    dest_cursor = dest_conn.cursor()
    
    try:
        dest_cursor.execute(create_sql)
        dest_conn.commit()
        print("✅ Table created successfully.")
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        dest_conn.rollback()
    
    dest_conn.close()

if __name__ == "__main__":
    create_table()
