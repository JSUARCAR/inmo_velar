"""
Script para ejecutar migracion de Propiedad Horizontal.
"""

import os
from dotenv import load_dotenv

load_dotenv()

import psycopg2

DB_HOST = os.getenv("DB_HOST", "hopper.proxy.rlwy.net")
DB_PORT = os.getenv("DB_PORT", "12937")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME", "railway")


def ejecutar_migracion():
    print(f"Conectando a PostgreSQL {DB_HOST}:{DB_PORT}/{DB_NAME}...")

    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, dbname=DB_NAME
    )
    conn.autocommit = True
    cursor = conn.cursor()

    sql_file = "scripts/crear_tablas_propiedad_horizontal.sql"
    print(f"Leyendo {sql_file}...")

    with open(sql_file, "r", encoding="utf-8") as f:
        sql_content = f.read()

    print("Ejecutando SQL...")
    try:
        cursor.execute(sql_content)
        print(" OK")
    except Exception as e:
        print(f" Error: {e}")

    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name IN ('asambleas', 'pagos_administracion')
    """)
    tablas = cursor.fetchall()
    print(f"Tablas creadas: {[t[0] for t in tablas]}")

    cursor.close()
    conn.close()
    print("\nListo!")


if __name__ == "__main__":
    ejecutar_migracion()
