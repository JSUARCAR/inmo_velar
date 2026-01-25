import os
import sys

sys.path.append(os.getcwd())

from src.infraestructura.persistencia.database import db_manager


def fix_contract_data():
    print("--- Patching Contract 1 ---")

    with db_manager.obtener_conexion() as conn:
        cursor = db_manager.get_dict_cursor(conn)

        # 1. Find a valid Arrendatario
        cursor.execute("SELECT ID_ARRENDATARIO FROM ARRENDATARIOS LIMIT 1")
        row = cursor.fetchone()

        if not row:
            print("❌ No valid Arrendatario found to patch with.")
            return

        valid_id = list(row.values())[0] if hasattr(row, "values") else row[0]
        print(f"Found valid Arrendatario ID: {valid_id}")

        # 2. Update Contract
        print(f"Updating Contract 1 to use ID_ARRENDATARIO={valid_id}...")
        update_query = f"UPDATE CONTRATOS_ARRENDAMIENTOS SET ID_ARRENDATARIO = {valid_id} WHERE ID_CONTRATO_A = 1"
        cursor.execute(update_query)
        conn.commit()
        print("✅ Update successful.")


if __name__ == "__main__":
    fix_contract_data()
