import os
import sys
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def check_views():
    print("Connecting to Railway DB...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # 1. List Views
        print("\n--- VIEWS ---")
        cursor.execute("SELECT viewname FROM pg_views WHERE schemaname = 'public'")
        views = [row[0] for row in cursor.fetchall()]
        print(views)
        
        required_views = ["vw_alerta_mora_diaria", "vw_alerta_vencimiento_contratos"]
        for v in required_views:
            if v in views:
                print(f"✅ {v} exists.")
                # Try simple select
                try:
                    cursor.execute(f'SELECT count(*) FROM "{v}"')
                    count = cursor.fetchone()[0]
                    print(f"   -> Count: {count}")
                except Exception as e:
                    print(f"   ❌ Error querying {v}: {e}")
                    conn.rollback()
            else:
                print(f"❌ {v} MISSING!")

        conn.close()
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    check_views()
