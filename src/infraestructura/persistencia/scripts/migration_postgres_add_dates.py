import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from src.infraestructura.persistencia.database import DatabaseManager

def migrate():
    print("Iniciando migración para PostgreSQL...")
    db = DatabaseManager()
    
    if not db.use_postgresql:
        print("ERROR: La configuración actual no es PostgreSQL. Verifique .env")
        return

    # Scripts de alteración
    scripts = [
        "ALTER TABLE RECIBOS_PUBLICOS ADD COLUMN IF NOT EXISTS FECHA_DESDE TEXT;",
        "ALTER TABLE RECIBOS_PUBLICOS ADD COLUMN IF NOT EXISTS FECHA_HASTA TEXT;",
        "ALTER TABLE RECIBOS_PUBLICOS ADD COLUMN IF NOT EXISTS DIAS_FACTURADOS INTEGER DEFAULT 0;"
    ]
    
    try:
        with db.transaccion() as conn:
            cursor = conn.cursor()
            for sql in scripts:
                print(f"Ejecutando: {sql}")
                cursor.execute(sql)
            print("Migración completada exitosamente.")
            
    except Exception as e:
        print(f"Error durante la migración: {e}")

if __name__ == "__main__":
    migrate()
