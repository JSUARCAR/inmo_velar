
from src.infraestructura.persistencia.database import db_manager
from src.infraestructura.persistencia.repositorio_usuario_sqlite import RepositorioUsuarioSQLite
from src.dominio.entidades.usuario import Usuario
from datetime import datetime
import traceback

def check_indexes():
    print("\n--- CHECKING INDEXES ---")
    conn = db_manager.obtener_conexion()
    cursor = db_manager.get_dict_cursor(conn)
    # Query for Postgres indexes
    try:
        cursor.execute("""
            SELECT indexname, indexdef 
            FROM pg_indexes 
            WHERE tablename = 'usuarios';
        """)
        for row in cursor.fetchall():
            print(f"{row['indexname']}: {row['indexdef']}")
    except Exception as e:
        print(f"Could not list indexes (might not be postgres?): {e}")

def reproduce_repo_behavior():
    print("\n--- REPRODUCING WITH REPO ---")
    repo = RepositorioUsuarioSQLite(db_manager)
    
    # mimick creating a user
    nombre = "losorio"
    
    # 1. Check existing
    existing = repo.obtener_por_nombre(nombre)
    print(f"Obtener por nombre '{nombre}': {existing}")
    
    if existing:
        print("User exists! Skipping insert.")
        return

    # 2. Try insert
    print(f"Attempting to create user '{nombre}' via Repo...")
    user = Usuario(
        id_usuario=None,
        nombre_usuario=nombre,
        contrasena_hash="hash_dummy",
        rol="Asesor",
        estado_usuario=True,
        fecha_creacion=datetime.now().isoformat()
    )
    
    try:
        created = repo.crear(user, "debug_script")
        print(f"User created successfully! ID: {created.id_usuario}")
        
        # Cleanup
        repo.eliminar(created.id_usuario) # This is soft delete
        # Hard delete for cleanup
        conn = db_manager.obtener_conexion()
        cursor = conn.cursor()
        placeholder = db_manager.get_placeholder()
        cursor.execute(f"DELETE FROM USUARIOS WHERE ID_USUARIO = {placeholder}", (created.id_usuario,))
        conn.commit()
        print("Cleanup successful.")
        
    except Exception as e:
        print("REPO CREATE FAILED")
        print(f"Error: {e}")
        # print full traceback to see where it fails
        traceback.print_exc()

if __name__ == "__main__":
    check_indexes()
    reproduce_repo_behavior()
