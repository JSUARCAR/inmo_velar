
import sys
import os
sys.path.append(os.getcwd())

from src.infraestructura.persistencia.database import db_manager

def debug_advisors():
    print("--- Debugging Advisor Query ---")
    
    # 1. Current Query (Strict)
    query_strict = """
    SELECT DISTINCT
        a.ID_ASESOR,
        p.NOMBRE_COMPLETO
    FROM ASESORES a
    INNER JOIN PERSONAS p ON a.ID_PERSONA = p.ID_PERSONA
    INNER JOIN CONTRATOS_MANDATOS cm ON a.ID_ASESOR = cm.ID_ASESOR
    WHERE a.ESTADO = TRUE
        AND cm.ESTADO_CONTRATO_M = 'Activo'
    ORDER BY p.NOMBRE_COMPLETO
    """
    
    print("\n[STRICT QUERY] (Current implementation):")
    with db_manager.obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(query_strict)
        rows = cursor.fetchall()
        print(f"Rows found: {len(rows)}")
        for row in rows:
            print(f" - {row}")

    # 2. Broader Query (Active Advisors only)
    query_broad = """
    SELECT DISTINCT
        a.ID_ASESOR,
        p.NOMBRE_COMPLETO
    FROM ASESORES a
    INNER JOIN PERSONAS p ON a.ID_PERSONA = p.ID_PERSONA
    WHERE a.ESTADO = TRUE
    ORDER BY p.NOMBRE_COMPLETO
    """
    
    print("\n[BROAD QUERY] (Active Advisors only):")
    with db_manager.obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(query_broad)
        rows = cursor.fetchall()
        print(f"Rows found: {len(rows)}")
        for row in rows:
            print(f" - {row}")

    # 3. Check Mandate Statuses
    print("\n[DIAGNOSTIC] Mandate Statuses:")
    with db_manager.obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT ESTADO_CONTRATO_M FROM CONTRATOS_MANDATOS")
        rows = cursor.fetchall()
        print(f"Statuses found: {rows}")

if __name__ == "__main__":
    debug_advisors()
