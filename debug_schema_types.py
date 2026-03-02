
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from urllib.parse import urlparse

def check_column_types():
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
            print("\nInformación de Columnas (Mandatos):")
            cur.execute("""
                SELECT column_name, data_type, character_maximum_length 
                FROM information_schema.columns 
                WHERE table_name = 'contratos_mandatos' 
                AND column_name = 'estado_contrato_m'
            """)
            print(cur.fetchone())

            print("\nInformación de Columnas (Arrendamientos):")
            cur.execute("""
                SELECT column_name, data_type, character_maximum_length 
                FROM information_schema.columns 
                WHERE table_name = 'contratos_arrendamientos' 
                AND column_name = 'estado_contrato_a'
            """)
            print(cur.fetchone())
            
            # También ver si hay espacios
            cur.execute("SELECT estado_contrato_m, LENGTH(estado_contrato_m) as len FROM contratos_mandatos LIMIT 1")
            row = cur.fetchone()
            if row:
                st = row.get('estado_contrato_m') or row.get('ESTADO_CONTRATO_M')
                l = row.get('len') or row.get('LEN')
                print(f"\nEjemplo Mandato: '{st}' (Length: {l})")
    finally:
        conn.close()

if __name__ == "__main__":
    check_column_types()
