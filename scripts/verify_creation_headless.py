from datetime import datetime
from src.infraestructura.persistencia.database import db_manager
from src.infraestructura.repositorios.repositorio_liquidacion_asesor_sqlite import RepositorioLiquidacionAsesorSQLite
from src.infraestructura.repositorios.repositorio_descuento_asesor_sqlite import RepositorioDescuentoAsesorSQLite
from src.infraestructura.repositorios.repositorio_pago_asesor_sqlite import RepositorioPagoAsesorSQLite
from src.infraestructura.persistencia.repositorio_contrato_arrendamiento_sqlite import RepositorioContratoArrendamientoSQLite
from src.aplicacion.servicios.servicio_liquidacion_asesores import ServicioLiquidacionAsesores

def verify_headless():
    print("Starting Headless Verification...")
    try:
        # 1. Setup Service
        repo_liq = RepositorioLiquidacionAsesorSQLite(db_manager)
        repo_desc = RepositorioDescuentoAsesorSQLite(db_manager)
        repo_pago = RepositorioPagoAsesorSQLite(db_manager)
        repo_contrato = RepositorioContratoArrendamientoSQLite(db_manager)
        
        print(f"DB Placeholder: '{db_manager.get_placeholder()}'")
        
        servicio = ServicioLiquidacionAsesores(repo_liq, repo_desc, repo_pago)
        
        # 2. Get Advisor (ARTHUR SUAREZ)
        # We need his ID. Assuming we know it or fetch it.
        # From previous logs, Arthur often has ID 1 or similar.
        # Let's search by name.
        with db_manager.obtener_conexion() as conn:
            cursor = db_manager.get_dict_cursor(conn)
            cursor.execute("SELECT a.ID_ASESOR FROM ASESORES a JOIN PERSONAS p ON a.ID_PERSONA=p.ID_PERSONA WHERE p.NOMBRE_COMPLETO LIKE '%ARTHUR%'")
            row = cursor.fetchone()
            if not row:
                print("Arthur not found!")
                return
            id_asesor = list(row.values())[0] # Handle dict
            print(f"Found Arthur ID: {id_asesor}")
            
        # 3. Get Active Contracts (Elite Logic Check)
        contratos = repo_contrato.obtener_activos_por_asesor(id_asesor)
        print(f"Active Contracts Found: {len(contratos)}")
        
        contratos_dto = [{"id": c.id_contrato_a, "canon": c.canon_arrendamiento} for c in contratos]
        
        # 4. Create Liquidation
        periodo = "2027-06"
        print(f"Creating Liquidation for {periodo}...")
        
        liq = servicio.generar_liquidacion_multi_contrato(
            id_asesor=id_asesor,
            periodo=periodo,
            contratos_lista=contratos_dto,
            porcentaje_comision=800, # 8.00%
            usuario="headless_test"
        )
        print(f"Liquidation Created. ID: {liq.id_liquidacion_asesor}")
        print(f"Canon: {liq.canon_arrendamiento_liquidado}")
        print(f"Commission Base: {liq.comision_bruta}")
        
        # 5. Add Discount
        print("Adding Discount: Multa - 50000...")
        servicio.agregar_descuento(
            id_liquidacion=liq.id_liquidacion_asesor,
            tipo="Multa",
            descripcion="Headless Test Discount",
            valor=50000,
            usuario="headless_test"
        )
        print("Discount Added via Service.")

        # 6. Verify Final State
        final_liq = servicio.obtener_por_id(liq.id_liquidacion_asesor)
        print(f"Final Net Value: {final_liq.valor_neto_asesor}")
        print(f"Total Discounts: {final_liq.total_descuentos}")
        
        if final_liq.total_descuentos == 50000 and final_liq.valor_neto_asesor == 140080: # 190080 - 50000
             print("VERIFICATION SUCCESS: Net Value Updated Correctly.")
        else:
             print(f"VERIFICATION FAILED: Expected Net 140080, Got {final_liq.valor_neto_asesor}")
        final_liq = servicio.obtener_por_id(liq.id_liquidacion_asesor)
        print("--- Final Verification ---")
        print(f"Total Discounts: {final_liq.total_descuentos}")
        print(f"Net Value: {final_liq.valor_neto_asesor}")
        
        expected_net = final_liq.comision_bruta - 50000
        if final_liq.valor_neto_asesor == expected_net:
            print("SUCCESS: Net Value matches expected calculation.")
        else:
            print(f"FAILURE: Expected {expected_net}, got {final_liq.valor_neto_asesor}")
            
    except Exception as e:
        print(f"Headless Verification FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_headless()
