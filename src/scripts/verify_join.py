import sys
import os
sys.path.append(os.getcwd())

from src.infraestructura.persistencia.database import db_manager

def verify_join_integrity():
    print("--- Verifying JOIN Integrity for Contract 1 ---")
    
    with db_manager.obtener_conexion() as conn:
        cursor = db_manager.get_dict_cursor(conn)
        
        # 1. Check Link CA -> ARR
        query1 = """
        SELECT COUNT(*) as count 
        FROM CONTRATOS_ARRENDAMIENTOS ca
        JOIN ARRENDATARIOS arr ON ca.ID_ARRENDATARIO = arr.ID_ARRENDATARIO
        WHERE ca.ID_CONTRATO_A = 1
        """
        cursor.execute(query1)
        res1 = cursor.fetchone()
        c1 = list(res1.values())[0] if hasattr(res1, 'values') else res1[0]
        print(f"JOIN Contrato -> Arrendatario: {'OK' if c1 > 0 else 'FAIL'} (Count: {c1})")
        
        # 2. Check Link CA -> ARR -> PER
        query2 = """
        SELECT COUNT(*) as count 
        FROM CONTRATOS_ARRENDAMIENTOS ca
        JOIN ARRENDATARIOS arr ON ca.ID_ARRENDATARIO = arr.ID_ARRENDATARIO
        JOIN PERSONAS per ON arr.ID_PERSONA = per.ID_PERSONA
        WHERE ca.ID_CONTRATO_A = 1
        """
        cursor.execute(query2)
        res2 = cursor.fetchone()
        c2 = list(res2.values())[0] if hasattr(res2, 'values') else res2[0]
        print(f"JOIN Contrato -> Arrendatario -> Persona: {'OK' if c2 > 0 else 'FAIL'} (Count: {c2})")

        # 3. Check raw IDs if failed
        if c1 == 0 or c2 == 0:
            cursor.execute("SELECT ID_ARRENDATARIO FROM CONTRATOS_ARRENDAMIENTOS WHERE ID_CONTRATO_A = 1")
            row = cursor.fetchone()
            if row:
                raw_id_arr = list(row.values())[0] if hasattr(row, 'values') else row[0]
                print(f"DEBUG: Contrato has ID_ARRENDATARIO = {raw_id_arr}")
                
                check_arr = f"SELECT * FROM ARRENDATARIOS WHERE ID_ARRENDATARIO = {raw_id_arr}"
                cursor.execute(check_arr)
                arr_row = cursor.fetchone()
                print(f"DEBUG: Arrendatario Row: {arr_row}")

if __name__ == "__main__":
    verify_join_integrity()
