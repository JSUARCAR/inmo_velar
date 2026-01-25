
import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.getcwd())

from src.infraestructura.persistencia.database import db_manager
from src.aplicacion.servicios.servicio_usuarios import ServicioUsuarios

def test_usuarios_service():
    print("Initializing ServicioUsuarios...")
    try:
        servicio = ServicioUsuarios(db_manager)
        print("Service initialized.")
        
        print("Calling listar_usuarios...")
        usuarios = servicio.listar_usuarios()
        
        print(f"Total usuarios found: {len(usuarios)}")
        
        for u in usuarios:
            print(f" - ID: {u.id_usuario}, Nombre: {u.nombre_usuario}, Rol: {u.rol}, Activo: {u.es_activo()}")
            
    except Exception as e:
        print(f"CRITICAL ERROR in Runtime Verification: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_usuarios_service()
