import psycopg2
import sys

# Source: Local PostgreSQL
SRC_HOST = "localhost"
SRC_PORT = 5432
SRC_DB = "db_inmo_velar"
SRC_USER = "inmo_user"
SRC_PASSWORD = "7323"

def list_boolean_columns():
    try:
        conn = psycopg2.connect(
            host=SRC_HOST, port=SRC_PORT, database=SRC_DB, user=SRC_USER, password=SRC_PASSWORD
        )
        cursor = conn.cursor()
        cursor.execute("""
            SELECT table_name, column_name 
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND data_type = 'boolean'
        """)
        
        print("--- BOOLEAN COLUMNS IN LOCAL DB ---")
        for row in cursor.fetchall():
            print(f"{row[0]}.{row[1]}")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_boolean_columns()
