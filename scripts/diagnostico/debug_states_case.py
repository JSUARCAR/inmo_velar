
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from urllib.parse import urlparse

def check_states():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("Error: DATABASE_URL not set")
        return

    parsed = urlparse(db_url)
    conn = psycopg2.connect(
        host=parsed.hostname,
        port=parsed.port,
        database=parsed.path.lstrip('/'),
        user=parsed.username,
        password=parsed.password
    )

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Check Mandatos
            cur.execute("SELECT DISTINCT ESTADO_CONTRATO_M FROM CONTRATOS_MANDATOS")
            mandatos = cur.fetchall()
            print("\nEstados Mandatos:")
            for m in mandatos:
                state = m.get('estado_contrato_m') or m.get('ESTADO_CONTRATO_M')
                print(f"- '{state}'")

            # Check Arrendamientos
            cur.execute("SELECT DISTINCT ESTADO_CONTRATO_A FROM CONTRATOS_ARRENDAMIENTOS")
            arriendos = cur.fetchall()
            print("\nEstados Arrendamientos:")
            for a in arriendos:
                state = a.get('estado_contrato_a') or a.get('ESTADO_CONTRATO_A')
                print(f"- '{state}'")
    finally:
        conn.close()

if __name__ == "__main__":
    check_states()
