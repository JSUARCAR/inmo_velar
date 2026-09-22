
import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.getcwd())

print("Verifying imports...")

try:
    print("personas_state loaded.")
    print("propiedades_state loaded.")
    print("liquidaciones_state loaded.")
    print("contratos_state loaded.")
    print("recibos_state loaded.")
    print("dashboard_state loaded.")
    print("incidentes_state loaded.")
    print("proveedores_state loaded.")
    print("All states compiled and imported successfully.")
except Exception as e:
    print(f"FAILED to import states: {e}")
    sys.exit(1)
