import sqlite3
import os

# Usamos la ruta absoluta de la base de datos detectada en logs previos
db_path = r'c:\Users\PC\OneDrive\Desktop\inmobiliaria velar\PYTHON-REFLEX\database.db'

def diagnostic():
    if not os.path.exists(db_path):
        print(f"Error: DB not found at {db_path}")
        # Intentar buscar en el directorio actual por si acaso
        db_path_local = os.path.join(os.getcwd(), 'database.db')
        if os.path.exists(db_path_local):
            print(f"Found DB at {db_path_local}")
            return run_queries(db_path_local)
        return

    run_queries(db_path)

def run_queries(valid_db_path):
    conn = sqlite3.connect(valid_db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print(f"--- Diagnóstico DB: {valid_db_path} ---")
    
    # 1. Verificar registros en ASESORES
    try:
        cursor.execute("SELECT COUNT(*) as total FROM ASESORES")
        print(f"Total en ASESORES: {cursor.fetchone()['total']}")
    except Exception as e:
        print(f"Error COUNT ASESORES: {e}")

    # 2. Verificar estructura y estados
    try:
        cursor.execute("SELECT * FROM ASESORES LIMIT 5")
        rows = cursor.fetchall()
        print("\nMuestra ASESORES (primeros 5):")
        for r in rows:
            print(dict(r))
    except Exception as e:
        print(f"Error SAMPLE ASESORES: {e}")

    # 3. Verificar PERSONAS
    try:
        cursor.execute("SELECT COUNT(*) as total FROM PERSONAS")
        print(f"\nTotal en PERSONAS: {cursor.fetchone()['total']}")
    except Exception as e:
        print(f"Error COUNT PERSONAS: {e}")

    # 4. Join ASESORES y PERSONAS con la condición problemática
    query_join = """
    SELECT a.ID_ASESOR, a.ESTADO, p.NOMBRE_COMPLETO, p.ESTADO_REGISTRO
    FROM ASESORES a
    JOIN PERSONAS p ON a.ID_PERSONA = p.ID_PERSONA
    LIMIT 10
    """
    try:
        cursor.execute(query_join)
        rows = cursor.fetchall()
        print("\nJoin ASESORES-PERSONAS (primeros 10):")
        for r in rows:
            print(dict(r))
    except Exception as e:
        print(f"Error JOIN SAMPLE: {e}")

    # 5. Ejecutar la consulta exacta del Estado
    query_exact = """
    SELECT a.ID_ASESOR, p.NOMBRE_COMPLETO 
    FROM ASESORES a 
    JOIN PERSONAS p ON a.ID_PERSONA = p.ID_PERSONA 
    WHERE (p.ESTADO_REGISTRO = 1 OR p.ESTADO_REGISTRO IS TRUE) 
      AND (a.ESTADO = 1 OR a.ESTADO IS TRUE)
    ORDER BY p.NOMBRE_COMPLETO
    """
    try:
        cursor.execute(query_exact)
        rows = cursor.fetchall()
        print(f"\nResultados consulta EXACTA: {len(rows)}")
        for r in rows:
            print(dict(r))
    except Exception as e:
        print(f"Error QUERY EXACTA: {e}")

    conn.close()

if __name__ == "__main__":
    diagnostic()
