import os
import sys
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("Error: DATABASE_URL not set")
    sys.exit(1)

TABLES_TO_CHECK = ["usuarios", "propiedades", "contratos_arrendamientos", "permisos", "rol_permisos", "configuracion_sistema"]

def verify_data():
    print(f"Connecting to Railway DB...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        print("\n--- ROW COUNTS ---")
        for table in TABLES_TO_CHECK:
            try:
                cursor.execute(f'SELECT count(*) FROM "{table}"')
                count = cursor.fetchone()[0]
                print(f"{table}: {count}")
            except Exception as e:
                print(f"{table}: ERROR ({e})")
                conn.rollback()

        # Check configuracion_sistema columns specifically
        print("\n--- CONFIG COLUMNS ---")
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'configuracion_sistema'")
        cols = [row[0] for row in cursor.fetchall()]
        print(f"configuracion_sistema columns: {cols}")
        if 'ubicacion' in cols:
            print("✅ 'ubicacion' column exists.")
        else:
            print("❌ 'ubicacion' column MISSING.")

        conn.close()
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    verify_data()
