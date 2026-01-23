
import sys
import os
import sqlite3

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.infraestructura.persistencia.database import DatabaseManager

def check_arrendatarios_schema():
    print("=== Inspección ARRENDATARIOS ===")
    db = DatabaseManager()
    
    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        
        print("\n--- Rows in ARRENDATARIOS (Limit 10) ---")
        cursor.execute("SELECT * FROM ARRENDATARIOS LIMIT 10")
        rows = cursor.fetchall()
        for r in rows:
            print(dict(r))
            
        # Check specific ID 18
        print("\n--- Check ID_ARRENDATARIO = 18 ---")
        cursor.execute("SELECT * FROM ARRENDATARIOS WHERE ID_ARRENDATARIO = 18")
        found = cursor.fetchone()
        if found:
            print(f"Found: {dict(found)}")
            # Check corresponding person
            id_persona = found['ID_PERSONA']
            cursor.execute("SELECT * FROM PERSONAS WHERE ID_PERSONA = ?", (id_persona,))
            p = cursor.fetchone()
            print(f"  Linked Persona ({id_persona}): {'Found' if p else 'MISSING'}")
        else:
            print("ID_ARRENDATARIO 18 NOT FOUND")

if __name__ == "__main__":
    check_arrendatarios_schema()
