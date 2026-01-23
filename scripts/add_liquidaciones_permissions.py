
import sys
from pathlib import Path

# Agregar directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from src.dominio.entidades.permiso import Permiso
from src.infraestructura.persistencia.database import db_manager
from src.infraestructura.persistencia.repositorio_permisos import RepositorioPermisos

def add_permissions():
    repo = RepositorioPermisos(db_manager)
    permisos_existentes = repo.listar_permisos()
    
    new_permissions = [
        {
            "accion": "APROBAR",
            "descripcion": "Aprobar liquidaciones de propietarios",
        },
        {
            "accion": "PAGAR",
            "descripcion": "Registrar pago de liquidaciones",
        }
    ]
    
    target_modulo = "Liquidaciones"
    
    for p_info in new_permissions:
        accion = p_info["accion"]
        
        # 1. Verificar existencia
        exists = False
        for p in permisos_existentes:
            if p.modulo == target_modulo and p.accion == accion:
                exists = True
                break
                
        if exists:
            print(f"⚠️ El permiso '{target_modulo}: {accion}' ya existe.")
            continue

        # 2. Crear
        permiso = Permiso(
            modulo=target_modulo,
            ruta="/liquidaciones",
            accion=accion,
            descripcion=p_info["descripcion"],
            categoria="Gestión"
        )

        try:
            repo.crear_permiso(permiso)
            print(f"✅ Permiso '{target_modulo}: {accion}' creado exitosamente.")
        except Exception as e:
            print(f"❌ Error al crear permiso '{accion}': {e}")

if __name__ == "__main__":
    add_permissions()
