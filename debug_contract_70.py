
import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent))

from src.infraestructura.persistencia.database import DatabaseManager
from src.infraestructura.persistencia.repositorio_contrato_mandato_sqlite import RepositorioContratoMandatoSQLite

def check_contract_70():
    db = DatabaseManager()
    repo = RepositorioContratoMandatoSQLite(db)
    contrato = repo.obtener_por_id(70)
    
    if not contrato:
        print("x Contrato 70 no encontrado")
        return

    print("v Contrato 70 encontrado:")
    for k, v in contrato.__dict__.items():
        print(f"{k}: {v}")

if __name__ == "__main__":
    check_contract_70()
