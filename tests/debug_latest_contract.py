
import sys
import os
import sqlite3

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.infraestructura.persistencia.database import DatabaseManager

def inspect_latest_contract():
    print("=== Inspección Último Contrato ===")
    db = DatabaseManager()
    
    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM CONTRATOS_ARRENDAMIENTOS ORDER BY ID_CONTRATO_A DESC LIMIT 1")
        row = cursor.fetchone()
        if row:
            print(dict(row))
        else:
            print("No se encontraron contratos.")

if __name__ == "__main__":
    inspect_latest_contract()
