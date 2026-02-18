import os
import sys
import json

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infraestructura.persistencia.database import db_manager
from src.aplicacion.servicios.servicio_alertas import ServicioAlertas

def check_alerts():
    print("=== Verificando Servicio de Alertas ===")
    
    if db_manager.use_postgresql:
        print("[INFO] Usando PostgreSQL")
    else:
        print("[INFO] Usando SQLite")

    try:
        servicio = ServicioAlertas(db_manager)
        alertas = servicio.obtener_alertas()
        
        print(f"\n[INFO] Total alertas encontradas: {len(alertas)}")
        
        mandato_alertas = [a for a in alertas if "Mandato" in a['tipo']]
        arriendo_alertas = [a for a in alertas if "Arriendo" in a['tipo']]
        
        print(f"[INFO] Alertas de Mandato: {len(mandato_alertas)}")
        for a in mandato_alertas:
            print(f"  - [{a['nivel'].upper()}] {a['mensaje']} (Fecha: {a['fecha']})")
            
        print(f"[INFO] Alertas de Arriendo: {len(arriendo_alertas)}")
        for a in arriendo_alertas:
            print(f"  - [{a['nivel'].upper()}] {a['mensaje']} (Fecha: {a['fecha']})")

        print("\n[INFO] Verificando servicio de contratos con 90 días:")
        from src.aplicacion.servicios.servicio_contratos import ServicioContratos
        # Re-instantiate needed repos locally if not easily accessible, or use service.servicio_contratos
        # ServicioAlertas initializes ServicioContratos internally
        mandatos_90 = servicio.servicio_contratos.listar_mandatos_por_vencer(90)
        print(f"  - Mandatos por vencer en 90 días: {len(mandatos_90)}")
        for m in mandatos_90:
             print(f"    * {m['id']} - {m['propiedad']} ({m['dias_restantes']} días)")

    except Exception as e:
        print(f"[ERROR] Falló la verificación: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_alerts()
