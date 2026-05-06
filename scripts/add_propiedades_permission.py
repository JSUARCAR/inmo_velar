
import sys
from pathlib import Path

# Agregar directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from src.dominio.entidades.permiso import Permiso
from src.infraestructura.persistencia.database import db_manager
from src.infraestructura.persistencia.repositorio_permisos import RepositorioPermisos

def add_permission():
    repo = RepositorioPermisos(db_manager)

    # 1. Verificar si ya existe
    permisos = repo.listar_permisos()
    target_modulo = "Propiedades"
    target_accion = "DISPONIBILIDAD"
    
    exists = False
    for p in permisos:
        if p.modulo == target_modulo and p.accion == target_accion:
            exists = True
            break
            
    if exists:
        print(f"⚠️ El permiso '{target_modulo}: {target_accion}' ya existe.")
        return

    # 2. Crear si no existe
    permiso = Permiso(
        modulo=target_modulo,
        ruta="/propiedades",
        accion=target_accion,
        descripcion="Cambiar disponibilidad de inmueble",
        categoria="Gestión"
    )

    try:
        repo.crear_permiso(permiso)
        print(f"✅ Permiso '{target_modulo}: {target_accion}' creado exitosamente.")
        
    except Exception as e:
        print(f"❌ Error al crear permiso: {e}")

if __name__ == "__main__":
    add_permission()
