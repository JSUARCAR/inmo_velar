import os
import sys
from dotenv import load_dotenv
import psycopg2

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def validar_migracion():
    load_dotenv()
    url = os.getenv("POSTGRES_PUBLIC_URL", os.getenv("DATABASE_URL"))
    if not url:
        print("Falta POSTGRES_PUBLIC_URL o DATABASE_URL en .env")
        return
        
    try:
        print(f"Conectando a BD...")
        conn = psycopg2.connect(url)
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("Aplicando script de migración...")
        migracion_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "migraciones", "sql", "alter_propiedades_admin_ph.sql"
        )
        
        with open(migracion_path, "r", encoding="utf-8") as f:
            sql = f.read()
            cursor.execute(sql)
            print("Script SQL ejecutado exitosamente.")
            
        print("\nValidando columnas creadas en la tabla PROPIEDADES...")
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE LOWER(table_name) = 'propiedades'
              AND LOWER(column_name) IN (
                  'fecha_pago_administracion', 
                  'link_pago_administracion', 
                  'cuota_extra_ordinaria'
              );
        """)
        rows = cursor.fetchall()
        
        print("\nColumnas encontradas:")
        for row in rows:
            print(f"- {row[0]}: {row[1]}")
            
        if len(rows) >= 3:
            print("\n✅ Verificación exitosa. Las tres columnas existen.")
        else:
            print(f"\n⚠️ Faltan columnas. Se encontraron {len(rows)} de 3.")
            
        conn.close()
    except Exception as e:
        print(f"Error durante la migración/validación: {e}")

if __name__ == "__main__":
    validar_migracion()
