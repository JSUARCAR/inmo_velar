
import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.getcwd())

print("Verifying imports...")

try:
    import src.presentacion_reflex.state.personas_state
    print("personas_state loaded.")
    import src.presentacion_reflex.state.propiedades_state
    print("propiedades_state loaded.")
    import src.presentacion_reflex.state.liquidaciones_state
    print("liquidaciones_state loaded.")
    import src.presentacion_reflex.state.contratos_state
    print("contratos_state loaded.")
    import src.presentacion_reflex.state.recibos_state
    print("recibos_state loaded.")
    import src.presentacion_reflex.state.dashboard_state
    print("dashboard_state loaded.")
    import src.presentacion_reflex.state.incidentes_state
    print("incidentes_state loaded.")
    import src.presentacion_reflex.state.proveedores_state
    print("proveedores_state loaded.")
    print("All states compiled and imported successfully.")
except Exception as e:
    print(f"FAILED to import states: {e}")
    sys.exit(1)
