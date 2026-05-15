import sys
import os
import traceback

# Add project root to path to import src
sys.path.append(os.getcwd())

from src.infraestructura.persistencia.database import db_manager

def migrar_postgres():
    print("Iniciando migración para PostgreSQL (Documento Consignatario)...")
    print(f"DB Mode: {db_manager.db_mode}")
    
    sql = """
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1
            FROM information_schema.columns
            WHERE table_name = 'propietarios'
            AND column_name = 'documento_consignatario'
        ) THEN
            ALTER TABLE "propietarios" ADD COLUMN "documento_consignatario" TEXT;
            RAISE NOTICE 'Columna documento_consignatario agregada a tabla propietarios';
        ELSE
            RAISE NOTICE 'La columna documento_consignatario ya existe en tabla propietarios';
        END IF;
    END
    $$;
    """
    
    try:
        conn = db_manager.obtener_conexion()
        
        # Manually manage transaction if context manager fails
        cursor = conn.cursor()
        
        cursor.execute(sql)
        conn.commit()
        print("Migración completada exitosamente.")
        cursor.close()
                
    except Exception as e:
        print(f"Error durante la migración: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    migrar_postgres()
