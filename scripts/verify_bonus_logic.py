
import os
import sys
import logging

# Setup path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.infraestructura.persistencia.database import db_manager
from src.infraestructura.repositorios.repositorio_liquidacion_asesor_sqlite import RepositorioLiquidacionAsesorSQLite
from src.infraestructura.repositorios.repositorio_descuento_asesor_sqlite import RepositorioDescuentoAsesorSQLite
from src.infraestructura.repositorios.repositorio_pago_asesor_sqlite import RepositorioPagoAsesorSQLite
from src.aplicacion.servicios.servicio_liquidacion_asesores import ServicioLiquidacionAsesores

logging.basicConfig(level=logging.INFO)

def verify_bonus():
    print("=== VERIFYING BONUS LOGIC ===")
    
    repo_liq = RepositorioLiquidacionAsesorSQLite(db_manager)
    repo_desc = RepositorioDescuentoAsesorSQLite(db_manager)
    repo_pago = RepositorioPagoAsesorSQLite(db_manager)
    
    servicio = ServicioLiquidacionAsesores(repo_liq, repo_desc, repo_pago)
    
    # Test Data
    ID_ASESOR = 1
    PERIODO = "2027-10" # Future period to avoid conflict
    CONTRATOS = [{'id': 1, 'canon': 1000000}]
    PORCENTAJE = 500 # 5%
    BONUS = 200000 # 200k Bonus
    
    print(f"Scenario: Canon 1M, Comm 5% (50k), Bonus 200k")
    print(f"Expected Net: 50k + 200k = 250k")
    
    # 1. Clean up potential previous run
    print("Cleaning up...")
    try:
         with db_manager.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM LIQUIDACIONES_ASESORES WHERE PERIODO_LIQUIDACION = %s", (PERIODO,))
            conn.commit()
    except Exception as e:
        print(f"Cleanup warning: {e}")
        
    # 2. Generate Liquidation with Bonus
    print("Generating Liquidation...")
    try:
        liq = servicio.generar_liquidacion_multi_contrato(
            id_asesor=ID_ASESOR,
            periodo=PERIODO,
            contratos_lista=CONTRATOS,
            porcentaje_comision=PORCENTAJE,
            total_bonificaciones=BONUS,
            usuario="TEST_BOT"
        )
        
        print(f"Liquidation Created: ID {liq.id_liquidacion_asesor}")
        print(f"Saved Bonus: {liq.total_bonificaciones}")
        print(f"Saved Net: {liq.valor_neto_asesor}")
        
        # Assertions
        assert liq.total_bonificaciones == BONUS, f"Bonus mismatch: {liq.total_bonificaciones} != {BONUS}"
        expected_net = 50000 + BONUS
        assert liq.valor_neto_asesor == expected_net, f"Net mismatch: {liq.valor_neto_asesor} != {expected_net}"
        
        # 3. Verify Persistence (Read back)
        print("Reading back from DB...")
        liq_db = repo_liq.obtener_por_id(liq.id_liquidacion_asesor)
        print(f"DB Bonus: {liq_db.total_bonificaciones}")
        
        assert liq_db.total_bonificaciones == BONUS, "DB Persistence failed for bonus"
        assert liq_db.valor_neto_asesor == expected_net, "DB Persistence failed for net value"
        
        print("SUCCESS: Bonus logic verified!")
        
    except Exception as e:
        print(f"FAILURE: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_bonus()
