import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

def diagnostic():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("Error: DATABASE_URL not found in .env")
        return

    print(f"Connecting to: {db_url.split('@')[-1]}")
    
    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # 1. La consulta corregida (Universal)
        query_exact = """
        SELECT a.ID_ASESOR, p.NOMBRE_COMPLETO 
        FROM ASESORES a 
        JOIN PERSONAS p ON a.ID_PERSONA = p.ID_PERSONA 
        WHERE p.ESTADO_REGISTRO IS TRUE AND a.ESTADO IS TRUE
        ORDER BY p.NOMBRE_COMPLETO
        """
        cursor.execute(query_exact)
        rows = cursor.fetchall()
        print(f"\nResultados consulta CORREGIDA: {len(rows)}")
        for r in rows:
            print(dict(r))
            
        conn.close()
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")

if __name__ == "__main__":
    diagnostic()
