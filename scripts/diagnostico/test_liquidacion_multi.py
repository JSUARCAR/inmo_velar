import sys
import os

# Añadir root al path
sys.path.append(os.getcwd())

from src.infraestructura.persistencia.database import db_manager
from src.infraestructura.repositorios.repositorio_liquidacion_asesor import RepositorioLiquidacionAsesor
from src.infraestructura.repositorios.repositorio_descuento_asesor import RepositorioDescuentoAsesor
from src.infraestructura.repositorios.repositorio_pago_asesor import RepositorioPagoAsesor
from src.aplicacion.servicios.servicio_liquidacion_asesores import ServicioLiquidacionAsesores

def test_multi():
    print("Iniciando prueba de liquidación multi-contrato con comisiones individuales...")
    try:
        repo_liq = RepositorioLiquidacionAsesor(db_manager)
        repo_desc = RepositorioDescuentoAsesor(db_manager)
        repo_pago = RepositorioPagoAsesor(db_manager)
        
        servicio = ServicioLiquidacionAsesores(repo_liq, repo_desc, repo_pago)
        
        id_asesor = 8 # Asesor de prueba usado antes
        periodo = "2026-07" # Periodo futuro para no chocar
        
        # Simular contratos con diferentes %
        # Nota: Los IDs de contrato deben existir en CONTRATOS_ARRENDAMIENTOS
        contratos = [
            {"id": 32, "canon": 1000000, "porcentaje_comision": 1000}, # 10% -> 100,000
            {"id": 33, "canon": 2000000, "porcentaje_comision": 500},  # 5% -> 100,000
        ]
        
        print(f"Generando liquidación para asesor {id_asesor} periodo {periodo}...")
        liq = servicio.generar_liquidacion_multi_contrato(
            id_asesor=id_asesor,
            periodo=periodo,
            contratos_lista=contratos,
            usuario="TEST_AGENT"
        )
        
        print(f"Liquidación creada ID: {liq.id_liquidacion_asesor}")
        print(f"Canon Total: {liq.canon_arrendamiento_liquidado} (Esperado: 3000000)")
        print(f"Comisión Bruta: {liq.comision_bruta} (Esperado: 200000)")
        print(f"Porcentaje Ponderado: {liq.porcentaje_comision} (Esperado: 666)")
        print(f"Modo Comisión: {liq.modo_comision}")
        
        # Verificar detalle de contratos en DB
        detalles = repo_liq.obtener_contratos_de_liquidacion(liq.id_liquidacion_asesor)
        print("\nDetalle de contratos en DB:")
        for d in detalles:
            print(f"  Contrato {d['id_contrato']}: %={d['comision_porcentaje_contrato']}, Monto={d['comision_monto_contrato']}")

        print("\n✅ Prueba finalizada con éxito.")

    except Exception as e:
        print(f"Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_multi()
