
import sys
import os
import sqlite3

# Add project root to sys.path
sys.path.insert(0, os.getcwd())

from src.infraestructura.persistencia.database import db_manager
from src.infraestructura.persistencia.repositorio_persona_sqlite import RepositorioPersonaSQLite

def test_repo_personas():
    print("Initializing RepositorioPersonaSQLite...")
    repo = RepositorioPersonaSQLite(db_manager)

    print("\n--- Testing contar_todos ---")
    try:
        total = repo.contar_todos()
        print(f"Total personas: {total}")
        print(f"Type of total: {type(total)}")
    except Exception as e:
        print(f"ERROR in contar_todos: {e}")
        import traceback
        traceback.print_exc()

    print("\n--- Testing obtener_todos (Limit 5) ---")
    try:
        personas = repo.obtener_todos(limit=5)
        print(f"Personas found: {len(personas)}")
        for p in personas:
            print(f" - ID: {p.id_persona}, Name: {p.nombre_completo}, Doc: {p.numero_documento}")
    except Exception as e:
        print(f"ERROR in obtener_todos: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_repo_personas()
