
import os
import psycopg2
from dotenv import load_dotenv

# Load env vars from .env file manually or rely on system envs
# The user provided credentials in the prompt, let's use those directly or try to read .env
# DB_HOST=localhost
# DB_PORT=5432
# DB_NAME=db_inmo_velar
# DB_USER=inmo_user
# DB_PASSWORD=7323

DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "db_inmo_velar"
DB_USER = "inmo_user"
DB_PASSWORD = "7323"

def inspect_table():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cur = conn.cursor()
        
        print(f"Connected to {DB_NAME}")
        
        # Query columns for PROPIEDADES table
        cur.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'propiedades'
        """)
        
        columns = cur.fetchall()
        
        if not columns:
            # Try upper case just in case
            cur.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = 'PROPIEDADES'
            """)
            columns = cur.fetchall()
            
        with open("db_schema.txt", "w") as f:
            if not columns:
                f.write("Table PROPIEDADES not found.")
            else:
                f.write("Columns in PROPIEDADES:\n")
                for col in columns:
                    f.write(f"- {col[0]} ({col[1]}), Nullable: {col[2]}, Default: {col[3]}\n")
                    
        conn.close()
        
    except Exception as e:
        with open("db_schema.txt", "w") as f:
            f.write(f"Error: {e}")

if __name__ == "__main__":
    inspect_table()
