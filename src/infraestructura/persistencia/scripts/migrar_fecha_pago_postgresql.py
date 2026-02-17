
import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path para poder importar src
root_path = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.append(str(root_path))

from src.infraestructura.persistencia.database import db_manager

def migrar_postgresql():
    print(f"Iniciando migración en PostgreSQL (Modo: {db_manager.db_mode})...")
    
    if db_manager.db_mode != "postgresql":
        print("ERROR: El modo de base de datos en .env no es 'postgresql'.")
        return

    query = "ALTER TABLE CONTRATOS_ARRENDAMIENTOS ADD COLUMN IF NOT EXISTS FECHA_PAGO TEXT;"
    
    try:
        # execute_write reemplaza ? por %s si es necesario, pero aquí usamos SQL directo
        with db_manager.transaccion() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            print("Columna FECHA_PAGO agregada exitosamente a CONTRATOS_ARRENDAMIENTOS (o ya existía).")
    except Exception as e:
        print(f"Error al ejecutar la migración: {e}")

if __name__ == "__main__":
    migrar_postgresql()
