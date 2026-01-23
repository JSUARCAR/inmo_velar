
import sqlite3
from src.infraestructura.configuracion.settings import obtener_configuracion

config = obtener_configuracion()
db_path = config.database_path

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    print(f"Inspeccionando vista: VW_ALERTA_MORA_DIARIA")
    cursor.execute("PRAGMA table_info(VW_ALERTA_MORA_DIARIA)")
    columns = cursor.fetchall()
    if columns:
        print("Columnas encontradas:")
        for col in columns:
            print(f"- {col[1]}")
    else:
        print("La vista no devolvió columnas (¿existe?). Probando SELECT * LIMIT 1")
        cursor.execute("SELECT * FROM VW_ALERTA_MORA_DIARIA LIMIT 1")
        print("Columnas en descripción del cursor:")
        print([d[0] for d in cursor.description])

except Exception as e:
    print(f"Error: {e}")

finally:
    conn.close()
