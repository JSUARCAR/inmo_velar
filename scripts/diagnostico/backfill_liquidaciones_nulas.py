import sys
import os
import logging

# Añadir el raíz al sys.path para importaciones
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.infraestructura.persistencia.database import db_manager

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
_log = logging.getLogger("BackfillLiquidacionesNulas")

def run_backfill():
    _log.info("Iniciando backfill de Liquidaciones Nulas (US2)")
    
    query = """
    UPDATE LIQUIDACIONES
    SET 
        TOTAL_INGRESOS = COALESCE(TOTAL_INGRESOS, 0),
        TOTAL_EGRESOS = COALESCE(TOTAL_EGRESOS, 0),
        NETO_A_PAGAR = COALESCE(NETO_A_PAGAR, 0),
        CANON_BRUTO = COALESCE(CANON_BRUTO, 0)
    WHERE 
        TOTAL_INGRESOS IS NULL 
        OR TOTAL_EGRESOS IS NULL 
        OR NETO_A_PAGAR IS NULL 
        OR CANON_BRUTO IS NULL;
    """
    
    try:
        with db_manager.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            filas_afectadas = cursor.rowcount
            conn.commit()
            _log.info(f"Backfill exitoso. {filas_afectadas} liquidaciones actualizadas.")
    except Exception as e:
        _log.error(f"Error ejecutando backfill: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_backfill()
