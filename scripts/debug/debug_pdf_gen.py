import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(os.getcwd())

try:
    from src.infraestructura.persistencia.database import db_manager
    from src.aplicacion.servicios.servicio_financiero import ServicioFinanciero
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

def test_pdf_gen():
    try:
        service = ServicioFinanciero(db_manager)
        id_liq = 4
        print(f"Testing PDF generation for Liquidation ID: {id_liq}")
        
        # Check if liquidation exists
        data = service.obtener_detalle_liquidacion_ui(id_liq)
        if not data:
            print(f"ERROR: Liquidation {id_liq} not found in DB.")
            return

        print("Liquidation data retrieved successfully.")
        
        # Generate PDF
        print("Calling generar_estado_cuenta_pdf...")
        path = service.generar_estado_cuenta_pdf(id_liq)
        print(f"PDF generated at: {path}")
        
        if os.path.exists(path):
            print("SUCCESS: File exists.")
        else:
            print("FAILURE: File returned path but does not exist.")
            
    except Exception as e:
        print(f"EXCEPTION: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pdf_gen()
