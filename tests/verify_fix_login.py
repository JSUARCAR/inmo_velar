
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

try:
    print("Attempting to import ServicioContratos...")
    # This import triggers the decorators execution. If they fail (like returning int instead of callable), 
    # the import itself might fail or subsequent usage will fail.
    # In the original error, it failed at import time/definition time because @cache_manager.invalidate(..) 
    # was executed and returned an int, which the decorator syntax tried to call as a function.
    from src.aplicacion.servicios.servicio_contratos import ServicioContratos
    print("SUCCESS: ServicioContratos imported successfully.")
    
    # Optional: Check if methods are callable
    print("Checking method types...")
    print(f"crear_mandato type: {type(ServicioContratos.crear_mandato)}")
    
    if callable(ServicioContratos.crear_mandato):
         print("SUCCESS: ServicioContratos.crear_mandato is callable.")
    else:
         print("FAILURE: ServicioContratos.crear_mandato is NOT callable.")
         exit(1)

except TypeError as e:
    print(f"FAILURE: TypeError during import/execution: {e}")
    exit(1)
except Exception as e:
    print(f"FAILURE: Unexpected error: {e}")
    exit(1)
