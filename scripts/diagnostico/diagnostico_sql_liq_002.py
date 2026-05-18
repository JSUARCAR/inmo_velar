import sys
import os
import json

# Añadir root al path
sys.path.append(os.getcwd())

from src.infraestructura.persistencia.database import db_manager

def run_diagnostico_sql():
    print("EJECUTANDO PASO 1: Extracción de Data Cruda (PostgreSQL)")
    try:
        conn = db_manager.obtener_conexion()
        cur = db_manager.get_dict_cursor(conn)
        
        query = """
        SELECT la.ID_LIQUIDACION_ASESOR, la.MODO_COMISION, la.PERIODO_LIQUIDACION,
               lc.ID_CONTRATO_A, lc.CANON_INCLUIDO,
               lc.COMISION_PORCENTAJE_CONTRATO, lc.COMISION_MONTO_CONTRATO
        FROM LIQUIDACIONES_ASESORES la
        JOIN LIQUIDACIONES_CONTRATOS lc ON la.ID_LIQUIDACION_ASESOR = lc.ID_LIQUIDACION_ASESOR
        WHERE la.PERIODO_LIQUIDACION = '2026-05'
          AND la.ID_ASESOR = (SELECT a.ID_ASESOR FROM ASESORES a 
                              JOIN PERSONAS p ON a.ID_PERSONA = p.ID_PERSONA 
                              WHERE p.NOMBRE_COMPLETO LIKE '%VELAR%' LIMIT 1);
        """
        
        cur.execute(query)
        rows = cur.fetchall()
        
        if not rows:
            print("No se encontraron registros para el periodo y asesor especificado.")
            return

        print(f"\nSe encontraron {len(rows)} registros de contratos asociados.")
        
        results = [dict(r) for r in rows]
        print(json.dumps(results, indent=2))
        
        # Análisis rápido
        pct_0 = all(r.get('comision_porcentaje_contrato') == 0 for r in results)
        modo_asesor = all(r.get('modo_comision') == 'ASESOR' for r in results)
        
        print("\n--- DIAGNÓSTICO PRELIMINAR ---")
        if pct_0:
            print("HIPÓTESIS CONFIRMADA: Las columnas de comisión en LIQUIDACIONES_CONTRATOS están en 0.")
        if modo_asesor:
            print("INFO: La liquidación está marcada como MODO_COMISION = 'ASESOR' (Legacy).")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db_manager.shutdown()

if __name__ == "__main__":
    run_diagnostico_sql()
