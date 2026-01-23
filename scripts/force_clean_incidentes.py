import psycopg2
import os

DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "db_inmo_velar"
DB_USER = "inmo_user"
DB_PASSWORD = "7323" 

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
