import psycopg2
import sys

# Source: Local PostgreSQL
SRC_HOST = "localhost"
SRC_PORT = 5432
SRC_DB = "db_inmo_velar"
SRC_USER = "inmo_user"
SRC_PASSWORD = "7323"

def list_local_tables():
    conn = psycopg2.connect(
        host=SRC_HOST, port=SRC_PORT, database=SRC_DB, user=SRC_USER, password=SRC_PASSWORD
    )
    cursor = conn.cursor()
    
    print("--- LOCAL TABLES ---")
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """)
    tables = [row[0] for row in cursor.fetchall()]
    for t in tables:
        print(t)

    print("\n--- CONFIGURACION_SISTEMA COLUMNS (LOCAL) ---")
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'configuracion_sistema'
    """)
    cols = [row[0] for row in cursor.fetchall()]
    print(cols)
    
    conn.close()

if __name__ == "__main__":
    list_local_tables()
