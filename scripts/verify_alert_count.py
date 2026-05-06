import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infraestructura.persistencia.database import db_manager
from src.aplicacion.servicios.servicio_alertas import ServicioAlertas

def verify_count():
    print("=== VERIFYING ALERT COUNT ===", flush=True)
    try:
        servicio = ServicioAlertas(db_manager)
        alertas = servicio.obtener_alertas()
        
        mandatos = [a for a in alertas if a['tipo'] == 'Contrato Mandato']
        arriendos = [a for a in alertas if a['tipo'] == 'Contrato Arriendo']
        
        print(f"Total Alertas: {len(alertas)}", flush=True)
        print(f"Mandatos: {len(mandatos)}", flush=True)
        print(f"Arriendos: {len(arriendos)}", flush=True)
        
        print("\n[MANDATOS SAMPLE]", flush=True)
        for m in mandatos[:5]:
            print(f" - {m['mensaje']}", flush=True)
            
    except Exception as e:
        print(f"Error: {e}", flush=True)

if __name__ == "__main__":
    verify_count()
