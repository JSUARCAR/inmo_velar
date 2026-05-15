
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

def find_duplicates():
    conn = psycopg2.connect(DB_URL)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT ID_PROPIEDAD, DIRECCION_PROPIEDAD FROM PROPIEDADES WHERE DIRECCION_PROPIEDAD ILIKE '%CR 44 CL 50-86 TO 7 APT 401%'")
            rows = cur.fetchall()
            print(f"Found {len(rows)} properties:")
            for r in rows:
                print(f"  ID: {r[0]}, Address: {r[1]}")
    finally:
        conn.close()

if __name__ == "__main__":
    find_duplicates()
