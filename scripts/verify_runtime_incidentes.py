
import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.getcwd())

from src.infraestructura.persistencia.database import db_manager
from src.aplicacion.servicios.servicio_incidentes import ServicioIncidentes

def test_incidentes_service():
    print("Initializing ServicioIncidentes...")
    try:
        servicio = ServicioIncidentes(db_manager)
        print("Service initialized.")
        
        print("Calling listar_con_filtros...")
        resultado = servicio.listar_con_filtros(page=1, page_size=10)
        
        items = resultado.get("items", [])
        total = resultado.get("total", 0)
        
        print(f"Total incidentes loaded: {total}")
        print(f"Items in page: {len(items)}")
        
        for inc in items:
            print(f" - ID: {inc.id_incidente}, Desc: {inc.descripcion_incidente}, Estado: {inc.estado}")
            
    except Exception as e:
        print(f"CRITICAL ERROR in Runtime Verification: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_incidentes_service()
