
import sys
import os
from pathlib import Path

# Add root to path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

print("Iniciando importacion...")
try:
    from src.aplicacion.servicios.servicio_financiero import ServicioFinanciero
    print("SUCCESS: ServicioFinanciero importado correctamente")
except ImportError as e:
    print(f"ERROR IMPORT: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"ERROR GENERAL: {e}")
    import traceback
    traceback.print_exc()
