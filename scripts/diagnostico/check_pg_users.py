import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def check_users():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT id_usuario, nombre_usuario FROM usuarios LIMIT 5")
    rows = cur.fetchall()
    print("USUARIOS EN POSTGRES:")
    for row in rows:
        print(f"ID: {row[0]}, User: {row[1]}")
    conn.close()

if __name__ == "__main__":
    check_users()
