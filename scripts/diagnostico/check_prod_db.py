import psycopg2
import sys

def check_prod():
    conn = psycopg2.connect(
        host="hopper.proxy.rlwy.net",
        port=12937,
        user="postgres",
        password="tBltIuhaUSMqQFvUMtSqIPFQZdXwpPtU",
        dbname="railway"
    )
    cursor = conn.cursor()
    
    print("=== DOCUMENTOS ===")
    try:
        cursor.execute("SELECT DISTINCT entidad_tipo FROM DOCUMENTOS")
        print(cursor.fetchall())
        
        print("\n=== DOCUMENTOS EN CONTRATO_MANDATO ===")
        cursor.execute("SELECT id, entidad_id, nombre_archivo FROM DOCUMENTOS WHERE entidad_tipo LIKE '%MANDATO%' OR entidad_tipo LIKE '%CONTRATO%'")
        print(cursor.fetchall())
    except Exception as e:
        print("Error en DOCUMENTOS:", e)
        conn.rollback()
        
    print("\n=== ARCHIVOS_ADJUNTOS ===")
    try:
        cursor.execute("SELECT DISTINCT TIPO_ENTIDAD FROM ARCHIVOS_ADJUNTOS")
        print(cursor.fetchall())
    except Exception as e:
        print("Error en ARCHIVOS_ADJUNTOS:", e)

check_prod()
