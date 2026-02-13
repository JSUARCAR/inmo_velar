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

# Destination: Railway PostgreSQL
DEST_URL = os.getenv("DATABASE_URL")

def get_column_type(conn, table, column):
    cursor = conn.cursor()
    try:
        cursor.execute(f"""
            SELECT data_type 
            FROM information_schema.columns 
            WHERE table_name = '{table}' AND column_name = '{column}'
        """)
        res = cursor.fetchone()
        return res[0] if res else "NOT FOUND"
    except Exception as e:
        return str(e)

def inspect_schemas():
    print("--- INSPECTING SCHEMAS ---")
    
    # 1. Local
    try:
        src_conn = psycopg2.connect(
            host=SRC_HOST, port=SRC_PORT, database=SRC_DB, user=SRC_USER, password=SRC_PASSWORD
        )
        src_type = get_column_type(src_conn, "propietarios", "estado_propietario")
        print(f"LOCAL 'propietarios.estado_propietario': {src_type}")
        src_conn.close()
    except Exception as e:
        print(f"Error checking local: {e}")

    # 2. Railway
    try:
        dest_conn = psycopg2.connect(DEST_URL)
        dest_type = get_column_type(dest_conn, "propietarios", "estado_propietario")
        print(f"RAILWAY 'propietarios.estado_propietario': {dest_type}")
        
        # Check usuarios count
        cursor = dest_conn.cursor()
        cursor.execute("SELECT count(*) FROM usuarios")
        count = cursor.fetchone()[0]
        print(f"RAILWAY 'usuarios' count: {count}")
        
        dest_conn.close()
    except Exception as e:
        print(f"Error checking railway: {e}")

if __name__ == "__main__":
    inspect_schemas()
