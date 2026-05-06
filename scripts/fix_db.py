
import sys
import os
import sqlite3

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.infraestructura.configuracion.settings import obtener_configuracion

def fix_db():
    try:
        config = obtener_configuracion()
        db_path = config.database_path
        print(f"Conectando a: {db_path}")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Verify table existence
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='CONTRATOS_ARRENDAMIENTOS_OLD'")
        if cursor.fetchone():
            print(">>> TABLA CONTRATOS_ARRENDAMIENTOS_OLD EXISTE.")
        else:
            print(">>> TABLA CONTRATOS_ARRENDAMIENTOS_OLD NO EXISTE.")

        # 2. Search for triggers referencing this table
        cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='trigger'")
        triggers = cursor.fetchall()
        
        found_bad = False
        for t in triggers:
            name = t[0]
            sql = t[1]
            if "CONTRATOS_ARRENDAMIENTOS_OLD" in str(sql):
                print(f"!!! TRIGGER CULPABLE ENCONTRADO: {name}")
                print(f"SQL: {sql}")
                conn.execute(f"DROP TRIGGER {name}")
                print(">>> TRIGGER ELIMINADO.")
                found_bad = True
        
        if not found_bad:
            print("No se encontraron triggers referenciando explícitamente a CONTRATOS_ARRENDAMIENTOS_OLD")

        # 3. Check Views
        cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='view'")
        views = cursor.fetchall()
        for v in views:
             name = v[0]
             sql = v[1]
             if "CONTRATOS_ARRENDAMIENTOS_OLD" in str(sql):
                 print(f"!!! VISTA CULPABLE ENCONTRADA: {name}")
                 print(f"SQL: {sql}")
                 conn.execute(f"DROP VIEW {name}")
                 print(">>> VISTA ELIMINADA.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_db()
