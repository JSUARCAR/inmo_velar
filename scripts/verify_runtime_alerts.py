
import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.getcwd())

from src.infraestructura.persistencia.database import db_manager
from src.aplicacion.servicios.servicio_alertas import ServicioAlertas

def test_alerts_service():
    print("Initializing ServicioAlertas...")
    try:
        servicio = ServicioAlertas(db_manager)
        print("Service initialized.")
        
        print("Calling obtener_alertas...")
        alertas = servicio.obtener_alertas()
        
        print(f"Total alerts found: {len(alertas)}")
        for a in alertas:
            print(f" - [{a['tipo']}] ({a['nivel']}): {a['mensaje']} | Fecha: {a.get('fecha')}")
            
        if len(alertas) == 0:
            print("WARNING: No alerts found. Checking if this is expected...")
            
    except Exception as e:
        print(f"CRITICAL ERROR in Runtime Verification: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_alerts_service()
