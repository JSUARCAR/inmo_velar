
import sys
import os

# Add src to path
sys.path.append(os.getcwd())

from src.infraestructura.persistencia.database import DatabaseManager
from src.aplicacion.servicios.servicio_propiedades import ServicioPropiedades
from src.infraestructura.persistencia.repositorio_propiedad_sqlite import RepositorioPropiedadSQLite

# Robust Mocking
class MockConn:
    def cursor(self): return MockCursor()
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def commit(self): pass
    def close(self): pass

class MockCursor:
    def execute(self, *args): pass
    def fetchall(self): return []
    def fetchone(self): return None
    def close(self): pass

class MockDB:
    use_postgresql = False
    def obtener_conexion(self):
        return MockConn()
    def get_placeholder(self):
        return "?"
    def get_dict_cursor(self, conn):
        return MockCursor()
    def get_last_insert_id(self, cursor, table, col):
        return 1

print("--- REPRODUCTION SCRIPT ---")
servicio = None

try:
    # Instantiate service
    db_manager = MockDB()
    # Patch RepositorioPropiedadSQLite to skip _ensure_tables if it exists/runs
    # Or just rely on mocks passing enough
    servicio = ServicioPropiedades(db_manager)
    
    # Try calling with limit (The Bug)
    print("Attempting: servicio.listar_propiedades(limit=100)")
    servicio.listar_propiedades(limit=100)
    print("SUCCESS? (Unexpected)")
except TypeError as e:
    print(f"CAUGHT EXPECTED ERROR: {e}")
except Exception as e:
    print(f"CAUGHT OTHER ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n--- VERIFICATION SCRIPT ---")
try:
    if servicio:
        # Try calling without limit (The Fix)
        print("Attempting: servicio.listar_propiedades()")
        
        # Monkey patch repo to avoid calls
        servicio.repo.listar_propiedades = lambda *args, **kwargs: []
        
        servicio.listar_propiedades()
        print("SUCCESS: Method signature accepted without arguments.")
    else:
        print("FAILURE: Service not initialized.")
except Exception as e:
    print(f"FAILURE: {e}")

