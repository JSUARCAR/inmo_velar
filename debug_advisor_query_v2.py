
import sys
import os
sys.path.append(os.getcwd())

from src.infraestructura.persistencia.database import db_manager

def check_query():
    print("--- Executing Advisor Query (v2) ---")
    
    query_asesores = """
    SELECT DISTINCT
        a.ID_ASESOR,
        p.NOMBRE_COMPLETO,
        a.COMISION_PORCENTAJE_ARRIENDO
    FROM ASESORES a
    INNER JOIN PERSONAS p ON a.ID_PERSONA = p.ID_PERSONA
    -- LEFT JOIN to include advisors without active mandates
    LEFT JOIN CONTRATOS_MANDATOS cm ON a.ID_ASESOR = cm.ID_ASESOR
    WHERE a.ESTADO = TRUE
    ORDER BY p.NOMBRE_COMPLETO
    """
    
    try:
        with db_manager.obtener_conexion() as conn:
            # Emulate exactly what the state does (using dict cursor getter if available, or raw execution)
            # The state code uses: cursor = db_manager.get_dict_cursor(conn)
            cursor = conn.cursor() 
            # Note: in real execution it uses "db_manager.get_dict_cursor(conn)". 
            # I should check if I can import that or simulate it. 
            # For now, standard cursor + fetchall.
            
            cursor.execute(query_asesores)
            rows = cursor.fetchall()
            
            print(f"Total Rows Returned: {len(rows)}")
            
            # Print first 5 rows
            for i, row in enumerate(rows[:5]):
                # If row is tuple
                print(f"Row {i}: {row}")
                
            # emulate list comprehension
            # asesores_select = [a['texto'] for a in asesores] 
            # Wait, the SQL returns (ID, NAME, PCT). 
            # If standard cursor, row[1] is name.
            if rows:
                if isinstance(rows[0], tuple):
                    names = [r[1] for r in rows]
                else:
                     # If row factory makes it dict-like
                    names = [r['NOMBRE_COMPLETO'] for r in rows]
                print(f"Names extracted: {names}")
                
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    check_query()
