import sys
import os

# Añadir root al path
sys.path.append(os.getcwd())

from src.infraestructura.persistencia.database import db_manager

def run_data_repair():
    print("EJECUTANDO FASE 1: Reparación de Datos (PostgreSQL)")
    conn = db_manager.obtener_conexion()
    cur = conn.cursor()
    
    try:
        # SQL para actualizar comisiones en cero desde los contratos de mandato
        # Se usa CAST a NUMERIC para evitar desbordamiento de INTEGER en el cálculo intermedio
        query = """
        UPDATE LIQUIDACIONES_CONTRATOS lc
        SET COMISION_PORCENTAJE_CONTRATO = cm.COMISION_PORCENTAJE_CONTRATO_M,
            COMISION_MONTO_CONTRATO = CAST((CAST(lc.CANON_INCLUIDO AS NUMERIC) * cm.COMISION_PORCENTAJE_CONTRATO_M / 10000) AS INTEGER)
        FROM CONTRATOS_ARRENDAMIENTOS ca
        JOIN CONTRATOS_MANDATOS cm ON ca.ID_PROPIEDAD = cm.ID_PROPIEDAD
        WHERE lc.ID_CONTRATO_A = ca.ID_CONTRATO_A
          AND lc.COMISION_PORCENTAJE_CONTRATO = 0
          AND cm.ESTADO_CONTRATO_M = 'Activo';
        """
        
        print("Sincronizando porcentajes desde Mandatos activos...")
        cur.execute(query)
        rows_affected = cur.rowcount
        conn.commit()
        
        print(f"✅ Sincronización exitosa. Registros actualizados: {rows_affected}")
        
    except Exception as e:
        print(f"❌ Error en reparación: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()
        db_manager.shutdown()

if __name__ == "__main__":
    run_data_repair()
