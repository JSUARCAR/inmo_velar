import psycopg2
import sys

# Source: Local PostgreSQL
SRC_HOST = "localhost"
SRC_PORT = 5432
SRC_DB = "db_inmo_velar"
SRC_USER = "inmo_user"
SRC_PASSWORD = "7323"

def extract_view_defs():
    print("Connecting to Local DB...")
    conn = psycopg2.connect(
        host=SRC_HOST, port=SRC_PORT, database=SRC_DB, user=SRC_USER, password=SRC_PASSWORD
    )
    cursor = conn.cursor()
    
    views = ["vw_alerta_mora_diaria", "vw_alerta_vencimiento_contratos"]
    
    for v in views:
        cursor.execute(f"SELECT definition FROM pg_views WHERE viewname = '{v}'")
        res = cursor.fetchone()
        if res:
            print(f"\n--- {v} DEFINITION ---")
            print(res[0])
        else:
            print(f"View {v} not found locally!")
            
    conn.close()

if __name__ == "__main__":
    extract_view_defs()
