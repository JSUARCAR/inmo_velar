import psycopg2
import os

DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "db_inmo_velar"
DB_USER = "postgres"
DB_PASSWORD = ""

def init_db_admin():
    schema_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'infraestructura', 'db', 'schema_orden_trabajo.sql')
    print(f"Loading schema from: {schema_path}")
    
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
            print("Executing SQL...")
            cursor.execute(schema_sql)
            print("Schema ORDENES_TRABAJO executed successfully with admin credentials.")
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    init_db_admin()
