import sys
import os
from pathlib import Path
from datetime import datetime

# Add project root to path
current_dir = Path(os.getcwd())
sys.path.append(str(current_dir))

from src.infraestructura.persistencia.database import db_manager
from src.dominio.entidades.configuracion_empresa import ConfiguracionEmpresa
from src.aplicacion.servicios.servicio_configuracion import ServicioConfiguracion

def verify_configuration_logic():
    print("=== Verifying Configuration Module logic ===")
    
    servicio = ServicioConfiguracion(db_manager)
    timestamp = datetime.now().isoformat()
    
    # 1. Test Company Configuration Upsert
    print("\n1. Testing Company Configuration Upsert...")
    new_config = ConfiguracionEmpresa(
        nombre_empresa=f"Test Enterprise {timestamp}",
        nit="900.000.000-TEST",
        email="test@enterprise.com",
        telefono="1234567890",
        direccion="Test Address 123",
        ubicacion="Test City",
        website="www.test.com"
    )
    
    success = servicio.guardar_configuracion_empresa(new_config, "TEST_SCRIPT")
    if success:
        print("   [PASS] Company configuration saved successfully.")
    else:
        print("   [FAIL] Failed to save company configuration.")
        
    # 2. Test Persistence
    print("\n2. Testing Persistence...")
    loaded_config = servicio.obtener_configuracion_empresa()
    if loaded_config.nombre_empresa == new_config.nombre_empresa:
        print(f"   [PASS] Data persisted correctly. Name: {loaded_config.nombre_empresa}")
    else:
        print(f"   [FAIL] Data check failed. Expected: {new_config.nombre_empresa}, Got: {loaded_config.nombre_empresa}")

    # 3. Test System Parameters (assuming some exist, or create one if needed)
    print("\n3. Testing System Parameter Update...")
    parametros = servicio.listar_parametros()
    if not parametros:
        print("   [WARN] No parameters found to test.")
    else:
        # Pick the first modifiable parameter
        target_param = next((p for p in parametros if p.modificable == 1), None)
        if target_param:
            old_val = target_param.valor_parametro
            new_val = "10" if old_val != "10" else "20" # Toggle value
            
            print(f"   Updating parameter '{target_param.nombre_parametro}' from '{old_val}' to '{new_val}'")
            try:
                servicio.actualizar_parametro(target_param.id_parametro, new_val, "TEST_SCRIPT")
                
                # Verify update
                updated_param = servicio.obtener_parametro(target_param.nombre_parametro)
                if updated_param.valor_parametro == new_val:
                    print("   [PASS] Parameter updated successfully.")
                else:
                    print(f"   [FAIL] Parameter update failed. Got: {updated_param.valor_parametro}")
                    
                # Restore value
                servicio.actualizar_parametro(target_param.id_parametro, old_val, "TEST_SCRIPT")
                print("   [INFO] Parameter restored to original value.")
                
            except Exception as e:
                print(f"   [FAIL] Error updating parameter: {e}")
        else:
            print("   [WARN] No modifiable parameters found.")

if __name__ == "__main__":
    verify_configuration_logic()
