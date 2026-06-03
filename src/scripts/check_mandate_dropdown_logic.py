import os
import sys

# Ensure we can import from src
sys.path.append(os.getcwd())

from src.infraestructura.persistencia.database import db_manager

def verify_mandate_logic():
    print(f"{'ID':<5} | {'Address':<40} | {'Active Mandate?':<15} | {'ELIGIBLE for New Mandate?':<25}")
    print("-" * 100)

    try:
        with db_manager.obtener_conexion() as conn:
            cursor = db_manager.get_dict_cursor(conn)

            # 1. Get all active properties
            cursor.execute("SELECT ID_PROPIEDAD, DIRECCION_PROPIEDAD FROM PROPIEDADES WHERE ESTADO_REGISTRO = TRUE")
            props = cursor.fetchall()

            eligible_count = 0
            ineligible_but_active_mandate = 0

            print("\nINELIGIBLE PROPERTIES (Should NOT appear in 'Nuevo Mandato'):")
            for p in props:
                p_id = p["ID_PROPIEDAD"]
                address = p["DIRECCION_PROPIEDAD"]

                # 2. Check for Active Mandate
                cursor.execute("""
                    SELECT 1 FROM CONTRATOS_MANDATOS 
                    WHERE ID_PROPIEDAD = %s AND ESTADO_CONTRATO_M = 'ACTIVO'
                """ % db_manager.get_placeholder(), (p_id,))
                has_active_mandate = cursor.fetchone() is not None

                if has_active_mandate:
                    ineligible_but_active_mandate += 1
                    print(f"- {address}")
                else:
                    eligible_count += 1

        print("-" * 100)
        print(f"Total Active Properties: {len(props)}")
        print(f"Eligible for New Mandate (No active mandate): {eligible_count}")
        print(f"Ineligible (Already has active mandate): {ineligible_but_active_mandate}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_mandate_logic()
