import sys
import os
import json
from datetime import datetime

# Añadir el root al path para importar migraciones.database_config
sys.path.append(os.getcwd())

from migraciones.database_config import get_database_connection

def run_audit():
    try:
        conn = get_database_connection()
        import psycopg2.extras
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        results = {}
        
        print("Ejecutando Query 1: Contratos mandato activos con comisión = 0...")
        # Query 1: Contratos de mandato activos con comisión en cero o NULL
        q1 = """
        SELECT ID_CONTRATO_M, ID_PROPIEDAD, ID_ASESOR, COMISION_PORCENTAJE_CONTRATO_M
        FROM CONTRATOS_MANDATOS
        WHERE ESTADO_CONTRATO_M = 'Activo'
          AND (COMISION_PORCENTAJE_CONTRATO_M IS NULL OR COMISION_PORCENTAJE_CONTRATO_M = 0);
        """
        cursor.execute(q1)
        results['q1'] = [dict(r) for r in cursor.fetchall()]
        
        print("Ejecutando Query 2: Discrepancias comisión asesor vs contrato...")
        # Query 2: Discrepancias comisión asesor vs contrato
        q2 = """
        SELECT a.ID_ASESOR, a.COMISION_PORCENTAJE_ARRIENDO as COMISION_ASESOR,
               cm.COMISION_PORCENTAJE_CONTRATO_M as COMISION_CONTRATO,
               (COALESCE(a.COMISION_PORCENTAJE_ARRIENDO, 0) * 100) - COALESCE(cm.COMISION_PORCENTAJE_CONTRATO_M, 0) as DIFERENCIA
        FROM ASESORES a
        JOIN CONTRATOS_MANDATOS cm ON a.ID_ASESOR = cm.ID_ASESOR
        WHERE cm.ESTADO_CONTRATO_M = 'Activo'
          AND (COALESCE(a.COMISION_PORCENTAJE_ARRIENDO, 0) * 100) != COALESCE(cm.COMISION_PORCENTAJE_CONTRATO_M, 0);
        """
        cursor.execute(q2)
        results['q2'] = [dict(r) for r in cursor.fetchall()]
        
        print("Ejecutando Query 3: Contratos arrendamiento sin management contract...")
        # Query 3: Contratos arrendamiento activos sin management contract activo
        q3 = """
        SELECT ca.ID_CONTRATO_A, ca.ID_PROPIEDAD, ca.CANON_ARRENDAMIENTO
        FROM CONTRATOS_ARRENDAMIENTOS ca
        WHERE ca.ESTADO_CONTRATO_A = 'Activo'
          AND NOT EXISTS (
            SELECT 1 FROM CONTRATOS_MANDATOS cm
            WHERE cm.ID_PROPIEDAD = ca.ID_PROPIEDAD AND cm.ESTADO_CONTRATO_M = 'Activo'
          );
        """
        cursor.execute(q3)
        results['q3'] = [dict(r) for r in cursor.fetchall()]
        
        print("Ejecutando Query 4: Distribución de porcentajes en históricos...")
        # Query 4: Distribución de porcentajes en históricos
        q4 = """
        SELECT PERIODO_LIQUIDACION, COUNT(*) as TOTAL,
               MIN(PORCENTAJE_COMISION) as MIN_PCT, 
               MAX(PORCENTAJE_COMISION) as MAX_PCT
        FROM LIQUIDACIONES_ASESORES
        GROUP BY PERIODO_LIQUIDACION
        ORDER BY PERIODO_LIQUIDACION;
        """
        cursor.execute(q4)
        results['q4'] = [dict(r) for r in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        # Guardar resultados en JSON para procesar después
        output_path = 'scripts/diagnostico/audit_results.json'
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=4, default=str)
            
        print(f"Auditoría completada. Resultados guardados en {output_path}")
        
    except Exception as e:
        print(f"Error en auditoría: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    run_audit()
