import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def check_idempotency_keys():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT KEY, PARAMETROS FROM IDEMPOTENCY_KEYS")
    rows = cur.fetchall()
    for row in rows:
        print(f"KEY: {row[0]}")
        print(f"PARAMS: {row[1]}")
    conn.close()

if __name__ == "__main__":
    check_idempotency_keys()
