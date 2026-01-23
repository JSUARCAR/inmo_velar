
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.infraestructura.persistencia.database import DatabaseManager

def inspect():
    db = DatabaseManager()
    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print("TABLES COUNT:", len(tables))
        for t in tables:
             print("-", t)
        
        if 'MUNICIPIOS' in tables:
             cursor.execute("PRAGMA table_info(MUNICIPIOS)")
             print("MUNICIPIOS INFO:", [list(row) for row in cursor.fetchall()])
        if 'DEPARTAMENTOS' in tables:
             cursor.execute("PRAGMA table_info(DEPARTAMENTOS)")
             print("DEPARTAMENTOS INFO:", [list(row) for row in cursor.fetchall()])
        if 'PAISES' in tables:
             cursor.execute("PRAGMA table_info(PAISES)")
             print("PAISES INFO:", [list(row) for row in cursor.fetchall()])
        if 'ARRENDATARIOS' in tables:
             cursor.execute("PRAGMA table_info(ARRENDATARIOS)")
             print("ARRENDATARIOS INFO:", [list(row) for row in cursor.fetchall()])

if __name__ == "__main__":
    inspect()
