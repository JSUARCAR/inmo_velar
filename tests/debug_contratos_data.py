
import sys
import os
import sqlite3

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.infraestructura.persistencia.database import DatabaseManager

def inspect_db():
    print("=== Inspección de Base de Datos ===")
    db = DatabaseManager()
    print(f"DB Path: {db.database_path.absolute()}")
    
    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        
        # 1. Listar Tablas
        print("\n--- Tablas Existentes ---")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for t in tables:
            print(f"- {t[0]}")
            
        # 2. Inspect CONTRATOS_ARRENDAMIENTOS
        print("\n--- CONTRATOS_ARRENDAMIENTOS ---")
        try:
            cursor.execute("SELECT count(*) FROM CONTRATOS_ARRENDAMIENTOS")
            count = cursor.fetchone()[0]
            print(f"Total filas: {count}")
            
            cursor.execute("SELECT * FROM CONTRATOS_ARRENDAMIENTOS LIMIT 5")
            rows = cursor.fetchall()
            for row in rows:
                # Convert active row to dict for printing
                print(dict(row))
        except Exception as e:
            print(f"Error accediendo a tabla: {e}")

        # 3. Inspect PROPIEDADES (since contracts depend on properties)
        print("\n--- PROPIEDADES ---")
        try:
            cursor.execute("SELECT count(*) FROM PROPIEDADES")
            print(f"Total filas: {cursor.fetchone()[0]}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    inspect_db()
