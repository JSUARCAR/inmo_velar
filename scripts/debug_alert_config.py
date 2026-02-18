import os
import sys

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infraestructura.persistencia.database import db_manager
from src.aplicacion.servicios.servicio_configuracion import ServicioConfiguracion
from src.aplicacion.servicios.servicio_alertas import ServicioAlertas

def check_config():
    print("=== Verificando Configuración de Alertas ===")
    
    if db_manager.use_postgresql:
        print("[INFO] Usando PostgreSQL")
    else:
        print("[INFO] Usando SQLite")

    try:
        config_service = ServicioConfiguracion(db_manager)
        
        # Check current config values
        dias_arriendo = config_service.obtener_valor_parametro("DIAS_ALERTA_ARRENDAMIENTO", None)
        dias_mandato = config_service.obtener_valor_parametro("DIAS_ALERTA_MANDATO", None)
        
        print(f"\n[CONFIG] DIAS_ALERTA_ARRENDAMIENTO en DB: {dias_arriendo} (Default code: 60)")
        print(f"[CONFIG] DIAS_ALERTA_MANDATO en DB: {dias_mandato} (Default code: 60)")
        
        # Check alerts with default
        print("\n[TEST] Probando ServicioAlertas con defaults...")
        alertas_service = ServicioAlertas(db_manager)
        alertas = alertas_service.obtener_alertas()
        print(f"Total alertas retornadas: {len(alertas)}")
        for a in alertas:
             print(f"  - {a['mensaje']}")

        # Test listing contracts directly to see days
        print("\n[TEST] Listando mandatos próximos a vencer (90 días):")
        mandatos = alertas_service.servicio_contratos.listar_mandatos_por_vencer(90)
        for m in mandatos:
            print(f"  - ID {m['id']}: {m['propiedad']} vencen en {m['dias_restantes']} días")

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_config()
