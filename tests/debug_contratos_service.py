
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.infraestructura.persistencia.database import DatabaseManager
from src.aplicacion.servicios.servicio_contratos import ServicioContratos

def test_contratos_service():
    print("=== Test ServicioContratos.listar_arrendamientos_paginado ===")
    
    db = DatabaseManager()
    servicio = ServicioContratos(db)
    
    # Test 1: Activos
    print("\n[TEST 1] Filter: estado='Activo'")
    result = servicio.listar_arrendamientos_paginado(page=1, page_size=10, estado='Activo', busqueda=None)
    print(f"Total found: {result.total}")
    print(f"Items: {len(result.items)}")
    for item in result.items:
        print(item)
        
    # Test 2: Todos
    print("\n[TEST 2] Filter: estado='Todos'")
    result = servicio.listar_arrendamientos_paginado(page=1, page_size=10, estado='Todos', busqueda=None)
    print(f"Total found: {result.total}")
    
    # Test 3: Raw Query Check for 'Activo' without join to check consistency
    print("\n[TEST 3] Raw Count Check from Service Connection")
    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM CONTRATOS_ARRENDAMIENTOS WHERE ESTADO_CONTRATO_A = 'Activo'")
        print(f"Raw Count 'Activo': {cursor.fetchone()[0]}")

if __name__ == "__main__":
    test_contratos_service()
