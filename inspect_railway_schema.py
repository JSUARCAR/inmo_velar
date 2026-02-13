import os
import sys
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def inspect_railway_schema():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    tables = ["propietarios", "propiedades", "usuarios"]
    
    print("--- RAILWAY SCHEMA INSPECTION ---")
    for table in tables:
        print(f"\nTABLE: {table}")
        cursor.execute(f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = '{table}'
        """)
        for row in cursor.fetchall():
            if row[1] != 'text' and row[1] != 'character varying': # Filter for interesting types
                print(f"  - {row[0]}: {row[1]}")
                
    conn.close()

if __name__ == "__main__":
    inspect_railway_schema()
