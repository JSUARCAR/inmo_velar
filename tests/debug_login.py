
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.infraestructura.persistencia.database import DatabaseManager
from src.aplicacion.servicios.servicio_autenticacion import ServicioAutenticacion

def test_login_logic():
    print("=== Testing Login Logic ===")
    db_manager = DatabaseManager()
    servicio = ServicioAutenticacion(db_manager)
    
    print("1. Intentando autenticar admin/admin123...")
    try:
        usuario = servicio.autenticar("admin", "admin123")
        if usuario:
            print(f"SUCCESS: Usuario autenticado: {usuario.nombre_usuario}")
            print(f"Es Activo: {usuario.es_activo()}")
        else:
            print("FAILURE: Usuario no encontrado o credenciales invalidas")
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"CRITICAL ERROR: {e}")

if __name__ == "__main__":
    test_login_logic()
