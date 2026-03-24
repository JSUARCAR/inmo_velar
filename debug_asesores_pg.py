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

    print(f"Connecting to: {db_url.split('@')[-1]}") # Hide credentials
    
    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("--- Diagnóstico PostgreSQL ---")
        
        # 1. Total Asesores
        cursor.execute("SELECT COUNT(*) as total FROM ASESORES")
        print(f"Total en ASESORES: {cursor.fetchone()['total']}")
        
        # 2. Muestra de Asesores
        cursor.execute("SELECT * FROM ASESORES LIMIT 5")
        rows = cursor.fetchall()
        print("\nMuestra ASESORES (primeros 5):")
        for r in rows:
            print(dict(r))
            
        # 3. Join ASESORES-PERSONAS
        query_join = """
        SELECT a.ID_ASESOR, a.ESTADO, p.NOMBRE_COMPLETO, p.ESTADO_REGISTRO
        FROM ASESORES a
        JOIN PERSONAS p ON a.ID_PERSONA = p.ID_PERSONA
        LIMIT 10
        """
        cursor.execute(query_join)
        rows = cursor.fetchall()
        print("\nJoin ASESORES-PERSONAS (primeros 10):")
        for r in rows:
            print(dict(r))
            
        # 4. La consulta exacta que falló
        query_exact = """
        SELECT a.ID_ASESOR, p.NOMBRE_COMPLETO 
        FROM ASESORES a 
        JOIN PERSONAS p ON a.ID_PERSONA = p.ID_PERSONA 
        WHERE (p.ESTADO_REGISTRO = 1 OR p.ESTADO_REGISTRO IS TRUE) 
          AND (a.ESTADO = 1 OR a.ESTADO IS TRUE)
        ORDER BY p.NOMBRE_COMPLETO
        """
        cursor.execute(query_exact)
        rows = cursor.fetchall()
        print(f"\nResultados consulta EXACTA: {len(rows)}")
        for r in rows:
            print(dict(r))
            
        conn.close()
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")

if __name__ == "__main__":
    diagnostic()
