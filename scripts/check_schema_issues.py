import os
import sys
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def check_troublesome_tables():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Check configuracion_sistema columns
    print("\n--- CONFIGURACION_SISTEMA COLUMNS ---")
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'configuracion_sistema'
    """)
    cols = [row[0] for row in cursor.fetchall()]
    print(cols)
    if "ubicacion" not in cols:
        print("❌ 'ubicacion' column is MISSING!")

    # Check database existence of bonificaciones_asesores
    print("\n--- CHECKING TABLES ---")
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'bonificaciones_asesores'
    """)
    if cursor.fetchone():
        print("✅ 'bonificaciones_asesores' exists.")
    else:
        print("❌ 'bonificaciones_asesores' DOES NOT exist.")

    conn.close()

if __name__ == "__main__":
    check_troublesome_tables()
