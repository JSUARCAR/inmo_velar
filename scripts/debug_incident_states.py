
import sys
import os
import sqlite3

# Añadir src al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.infraestructura.persistencia.database import db_manager

def debug_db(mode='postgres'):
    try:
        print(f"--- AUDITORÍA DE INCIDENTES Y COTIZACIONES ({mode.upper()}) ---")
        
        if mode == 'sqlite':
            db_path = os.path.join(os.path.dirname(__file__), '..', 'DB_Inmo_Velar.db')
            if not os.path.exists(db_path):
                print(f"No existe el archivo SQLite en {db_path}")
                return
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
        else:
            conn_ctx = db_manager.transaccion()
            conn = conn_ctx.__enter__()
            cursor = db_manager.get_dict_cursor(conn)
            
        # Consultar todos los incidentes
        cursor.execute("SELECT ID_INCIDENTE, ESTADO, DESCRIPCION_INCIDENTE FROM INCIDENTES")
        rows = cursor.fetchall()
        
        if not rows:
            print("No se encontraron incidentes.")
        else:
            print(f"Total de incidentes: {len(rows)}")
            estados = {}
            for r in rows:
                est = r['ESTADO']
                estados[est] = estados.get(est, 0) + 1
            print("Conteo por estado (INCIDENTES):")
            for est, count in estados.items():
                print(f" - '{est}': {count}")

        if mode == 'sqlite':
            conn.close()
        else:
            conn_ctx.__exit__(None, None, None)

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    mode = 'postgres'
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    debug_db(mode)
