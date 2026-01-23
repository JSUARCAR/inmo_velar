
import sys
import os
from datetime import datetime

# Adjust path to find src
sys.path.append(os.getcwd())

from src.infraestructura.persistencia.database import DatabaseManager
from src.aplicacion.servicios.servicio_dashboard import ServicioDashboard

def verify_filters():
    print("=== Verificando Filtros Dashboard ===")
    
    db_manager = DatabaseManager()
    servicio = ServicioDashboard(db_manager)
    
    # 1. Test Default (Current Month, No Advisor)
    print("\n[TEST 1] Default Values (Mes Actual, Sin Asesor)")
    flujo_default = servicio.obtener_flujo_caja_mes()
    print(f"  Flujo Caja: {flujo_default}")
    
    # 2. Test Specific Month (e.g. November 2024)
    print("\n[TEST 2] Specific Date (Nov 2024)")
    flujo_nov = servicio.obtener_flujo_caja_mes(mes=11, anio=2024)
    print(f"  Flujo Caja (Nov 24): {flujo_nov}")
    
    # 3. Test Specific Advisor (ID=1)
    # Assuming Advisor 1 exists. If not, results might be 0, but no crash.
    print("\n[TEST 3] Specific Advisor (ID=1)")
    flujo_asesor = servicio.obtener_flujo_caja_mes(id_asesor=1)
    ocupacion_asesor = servicio.obtener_tasa_ocupacion(id_asesor=1)
    contratos_asesor = servicio.obtener_total_contratos_activos(id_asesor=1)
    comisiones_asesor = servicio.obtener_comisiones_pendientes(id_asesor=1)
    
    print(f"  Flujo Caja (Asesor 1): {flujo_asesor}")
    print(f"  Ocupacion (Asesor 1): {ocupacion_asesor}")
    print(f"  Contratos (Asesor 1): {contratos_asesor}")
    print(f"  Comisiones (Asesor 1): {comisiones_asesor}")
    
    print("\n=== Verificación Correcta (Sin Errores de Ejecución) ===")

if __name__ == "__main__":
    try:
        verify_filters()
    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
