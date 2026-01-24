import psycopg2
import os

# Config from shared_db_config
try:
    import sys
    import os
    # Add root to sys.path if running from subdir
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from shared_db_config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
except ImportError:
    # Fallback
    from dotenv import load_dotenv
    load_dotenv()
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "db_inmo_velar")
    DB_USER = os.getenv("DB_USER", "inmo_user")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "7323") 

def force_clean():
    print("Iniciando vaciado FORZADO de tablas...")
    
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # 1. Borrar Cotizaciones y Historial primero (FK dependencies)
        print("Borrando Historial...")
        cursor.execute("DELETE FROM HISTORIAL_INCIDENTES")
        
        print("Borrando Cotizaciones...")
        cursor.execute("DELETE FROM COTIZACIONES")

        # 2. Borrar Incidentes
        print("Borrando Incidentes...")
        cursor.execute("DELETE FROM INCIDENTES")
        
        # 3. Verificar
        cursor.execute("SELECT COUNT(*) FROM INCIDENTES")
        count = cursor.fetchone()[0]
        print(f"Filas restantes en INCIDENTES: {count}")
        
        if count == 0:
            print("SUCCESS: Tabla vacía.")
        else:
            print("WARNING: La tabla aún tiene datos.")

        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    force_clean()
