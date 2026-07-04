import os
import sys
import json

# Ensure we can import from src
sys.path.append(os.getcwd())

from src.infraestructura.persistencia.database import db_manager


def get_ineligible_properties():
    try:
        with db_manager.obtener_conexion() as conn:
            cursor = db_manager.get_dict_cursor(conn)

            # 1. Get all active properties
            cursor.execute(
                "SELECT ID_PROPIEDAD, DIRECCION_PROPIEDAD FROM PROPIEDADES WHERE ESTADO_REGISTRO = TRUE"
            )
            props = cursor.fetchall()

            ineligible_list = []
            eligible_list = []

            for p in props:
                p_id = p["ID_PROPIEDAD"]
                address = p["DIRECCION_PROPIEDAD"]

                # 2. Check for Active Mandate
                cursor.execute(
                    """
                    SELECT 1 FROM CONTRATOS_MANDATOS 
                    WHERE ID_PROPIEDAD = %s AND ESTADO_CONTRATO_M = 'ACTIVO'
                """ % db_manager.get_placeholder(),
                    (p_id,),
                )
                has_active_mandate = cursor.fetchone() is not None

                if has_active_mandate:
                    ineligible_list.append(address)
                else:
                    eligible_list.append(address)

            report = {
                "ineligible": ineligible_list,
                "eligible": eligible_list,
                "total_active_properties": len(props),
                "total_ineligible": len(ineligible_list),
                "total_eligible": len(eligible_list),
            }

            with open("ineligible_report.json", "w", encoding="utf-8") as f:
                json.dump(report, f, indent=4, ensure_ascii=False)

            print("Report generated: ineligible_report.json")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    get_ineligible_properties()
