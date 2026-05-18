import sys
import os

# Añadir root al path
sys.path.append(os.getcwd())

from src.infraestructura.persistencia.database import db_manager

def validate_financials():
    print("Iniciando validación financiera de liquidaciones por contrato...")
    conn = db_manager.obtener_conexion()
    cur = db_manager.get_dict_cursor(conn)
    
    try:
        # 1. Obtener liquidaciones en modo CONTRATO_MANDATO
        cur.execute("""
            SELECT ID_LIQUIDACION_ASESOR, ID_ASESOR, PERIODO_LIQUIDACION, 
                   COMISION_BRUTA, CANON_ARRENDAMIENTO_LIQUIDADO
            FROM LIQUIDACIONES_ASESORES
            WHERE MODO_COMISION = 'CONTRATO_MANDATO'
        """)
        liquidaciones = cur.fetchall()
        
        if not liquidaciones:
            print("No se encontraron liquidaciones generadas en modo CONTRATO_MANDATO.")
            return

        print(f"Validando {len(liquidaciones)} liquidaciones...")
        
        for liq in liquidaciones:
            id_liq = liq.get('id_liquidacion_asesor') or liq.get('ID_LIQUIDACION_ASESOR')
            periodo = liq.get('periodo_liquidacion') or liq.get('PERIODO_LIQUIDACION')
            monto_reportado = liq.get('comision_bruta') or liq.get('COMISION_BRUTA') or 0
            
            # 2. Obtener detalle de contratos para esta liquidación
            cur.execute("""
                SELECT SUM(COMISION_MONTO_CONTRATO) as comision_suma
                FROM LIQUIDACIONES_CONTRATOS
                WHERE ID_LIQUIDACION_ASESOR = %s
            """, (id_liq,))
            row = cur.fetchone()
            monto_calculado = row.get('comision_suma') or row.get('COMISION_SUMA') or 0
            
            diff = monto_reportado - monto_calculado
            
            if abs(diff) > 1:
                print(f"❌ DISCREPANCIA en Liq {id_liq} ({periodo}):")
                print(f"   Reportado: {monto_reportado}")
                print(f"   Calculado: {monto_calculado}")
                print(f"   Diferencia: {diff}")
            else:
                print(f"✅ Liq {id_liq} OK: {monto_reportado} coincide con desglose.")

    except Exception as e:
        print(f"Error en validación: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    validate_financials()
