import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.infraestructura.persistencia.database import db_manager
from src.infraestructura.persistencia.repositorio_incidentes_sqlite import RepositorioIncidentesSQLite

def verify_table_creation():
    print("Verifying HISTORIAL_INCIDENTES table creation...")
    repo = RepositorioIncidentesSQLite(db_manager)
    try:
        repo.crear_tabla_historial()
        print("Success: Method creating_tabla_historial executed without error.")
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    verify_table_creation()
