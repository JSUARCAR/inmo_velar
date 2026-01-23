
import sys
import os
import sqlite3

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.infraestructura.configuracion.settings import obtener_configuracion
from src.infraestructura.persistencia.database import DatabaseManager

def debug_ipc():
    try:
        config = obtener_configuracion()
        db = DatabaseManager()
        print(f"DEBUG: Conectando a BD: {config.database_path}")
        
        with db.obtener_conexion() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            print("\n1. Contenido Tabla IPC:")
            cursor.execute("SELECT * FROM IPC")
            rows = cursor.fetchall()
            if not rows:
                print(">>> TABLA VACÍA")
            for row in rows:
                print(dict(row))
                
            print("\n2. Probando query 'obtener_ultimo':")
            cursor.execute("SELECT * FROM IPC WHERE ESTADO_REGISTRO = 1 ORDER BY ANIO DESC LIMIT 1")
            ultimo = cursor.fetchone()
            if ultimo:
                print(f"Ultimo encontrado: {dict(ultimo)}")
            else:
                print(">>> QUERY RETORNA NONE")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_ipc()
