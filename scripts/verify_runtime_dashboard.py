
import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.getcwd())

from src.infraestructura.persistencia.database import db_manager
from src.aplicacion.servicios.servicio_dashboard import ServicioDashboard
from src.infraestructura.persistencia.repositorio_dashboard_sqlite import RepositorioDashboardSQLite

def test_dashboard_service():
    print("Initializing ServicioDashboard...")
    try:
        repo = RepositorioDashboardSQLite(db_manager)
        servicio = ServicioDashboard(repo)
        print("Service initialized.")
        
        print("Calling obtener_recibos_vencidos_resumen...")
        resumen = servicio.obtener_recibos_vencidos_resumen()
        print(f"Resumen Recibos Vencidos: {resumen}")
        
        print("Calling other dashboard methods...")
        mora = servicio.obtener_cartera_mora()
        print(f"Resumen Mora: {mora}")
        
        print("Verification SUCCESSFUL: All tested methods responded.")
            
    except Exception as e:
        print(f"CRITICAL ERROR in Runtime Verification: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_dashboard_service()
