
from src.infraestructura.persistencia.database import DatabaseManager
from src.aplicacion.servicios.servicio_desocupaciones import ServicioDesocupaciones

def verify_contracts_loading():
    print("Testing Contracts Loading...")
    
    try:
        db = DatabaseManager()
        service = ServicioDesocupaciones(db)
        
        contratos = service.listar_contratos_candidatos()
        print(f"Contracts loaded: {len(contratos)}")
        
        if contratos:
            print("SUCCESS: Contracts list is not empty.")
            for c in contratos[:3]:
                print(f" - {c}")
        else:
            print("WARNING: Contracts list is empty (this might be normal if DB is empty, but verify if you expected data).")
            
    except Exception as e:
        print(f"ERROR: Failed to load contracts. {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_contracts_loading()
