import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from migraciones.database_config import DatabaseConfig

def apply_migration():
    print("Obteniendo conexion...")
    with DatabaseConfig.obtener_conexion() as conn:
        with conn.cursor() as cursor:
            try:
                # Add column in PostgreSQL/SQLite
                # Depending on what exactly is running. We will execute standard ALTER TABLE.
                print("Ejecutando ALTER TABLE PAGO_PREDIAL...")
                cursor.execute("ALTER TABLE LIQUIDACIONES ADD COLUMN PAGO_PREDIAL INTEGER DEFAULT 0;")
                conn.commit()
                print("Migracion PAGO_PREDIAL completada con exito.")
            except Exception as e:
                print(f"La columna podria ya existir o hubo un error: {e}")
                conn.rollback()

if __name__ == '__main__':
    apply_migration()
