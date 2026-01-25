import sys
import os
from pathlib import Path

# Add project root to path
current_dir = Path(os.getcwd())
sys.path.append(str(current_dir))

from src.infraestructura.persistencia.database import db_manager

def apply_migration():
    print("Applying migration...")
    migration_path = Path("migraciones/crear_tabla_configuracion.sql")
    if not migration_path.exists():
        print(f"Error: Migration file not found at {migration_path}")
        return

    try:
        db_manager.inicializar_base_datos(migration_path)
        print("Migration applied successfully.")
    except Exception as e:
        print(f"Error applying migration: {e}")

if __name__ == "__main__":
    apply_migration()
