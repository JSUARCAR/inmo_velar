import sys
import os
from pathlib import Path

# Add project root to path
current_dir = Path(os.getcwd())
sys.path.append(str(current_dir))

from src.infraestructura.persistencia.database import db_manager

def apply_logo_migration():
    print("Aplicando migración para logo...")
    migration_path = Path("migraciones/agregar_logo_configuracion.sql")
    
    if not migration_path.exists():
        print(f"Error: Migration file not found at {migration_path}")
        return False

    try:
        db_manager.inicializar_base_datos(migration_path)
        print("✅ Migración aplicada exitosamente.")
        return True
    except Exception as e:
        print(f"❌ Error applying migration: {e}")
        return False

if __name__ == "__main__":
    success = apply_logo_migration()
    sys.exit(0 if success else 1)
