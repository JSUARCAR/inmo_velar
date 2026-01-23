
import psycopg2

# Configuración directa desde el .env que leí
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "db_inmo_velar"
DB_USER = "postgres"
DB_PASSWORD = "7323"

def run_migration():
    print("Connecting to database...")
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        conn.autocommit = True
        
        with conn.cursor() as cursor:
            print("Executing SQL...")
            sql = """
            ALTER TABLE configuracion_sistema
            ADD COLUMN IF NOT EXISTS representante_legal TEXT DEFAULT '',
            ADD COLUMN IF NOT EXISTS cedula_representante TEXT DEFAULT '';
            """
            cursor.execute(sql)
            print("Migration applied successfully!")
            
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_migration()
