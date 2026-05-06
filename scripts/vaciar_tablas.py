import sqlite3
import os

# Configuración
DB_PATH = r"c:\Users\PC\OneDrive\Desktop\inmobiliaria velar\PYTHON-FLET\DB_Inmo_Velar.db"
SQL_SCRIPT_PATH = r"c:\Users\PC\OneDrive\Desktop\inmobiliaria velar\PYTHON-FLET\scripts\vaciar_tablas.sql"

def vaciar_tablas():
    if not os.path.exists(DB_PATH):
        print(f"Error: No se encontró la base de datos en {DB_PATH}")
        return

    if not os.path.exists(SQL_SCRIPT_PATH):
        print(f"Error: No se encontró el script SQL en {SQL_SCRIPT_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Leer el script SQL
        with open(SQL_SCRIPT_PATH, 'r', encoding='utf-8') as sql_file:
            sql_script = sql_file.read()

        print("Iniciando vaciado de tablas...")
        
        # Ejecutar el script
        cursor.executescript(sql_script)
        
        conn.commit()
        print("Tablas vaciadas exitosamente.")
        
    except sqlite3.Error as e:
        print(f"Error de base de datos: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    confirmacion = input(f"¿Estás SEGURO de que quieres vaciar las tablas de {DB_PATH}? Escribe 'SI' para continuar: ")
    if confirmacion == 'SI':
        vaciar_tablas()
    else:
        print("Operación cancelada.")
