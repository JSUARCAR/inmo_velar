
import os
import sys

# Añadir el directorio actual al path
sys.path.append(os.getcwd())

# Mock de Reflex para evitar importaciones pesadas
from unittest.mock import MagicMock
sys.modules['reflex'] = MagicMock()
sys.modules['magic'] = MagicMock()

def simulate_load():
    from src.infraestructura.persistencia.database import db_manager
    from src.aplicacion.servicios.servicio_contratos import ServicioContratos
    from src.infraestructura.persistencia.repositorio_contrato_mandato_sqlite import RepositorioContratoMandatoSQLite
    from src.infraestructura.persistencia.repositorio_contrato_arrendamiento_sqlite import RepositorioContratoArrendamientoSQLite
    from src.infraestructura.persistencia.repositorio_propiedad_sqlite import RepositorioPropiedadSQLite
    from src.infraestructura.persistencia.repositorio_renovacion_sqlite import RepositorioRenovacionSQLite
    from src.infraestructura.persistencia.repositorio_ipc_sqlite import RepositorioIPCSQLite
    from src.infraestructura.persistencia.repositorio_arrendatario_sqlite import RepositorioArrendatarioSQLite
    from src.infraestructura.persistencia.repositorio_codeudor_sqlite import RepositorioCodeudorSQLite

    print(f"DEBUG: DB_MODE is {db_manager.db_mode}")
    
    repo_mandato = RepositorioContratoMandatoSQLite(db_manager)
    repo_arriendo = RepositorioContratoArrendamientoSQLite(db_manager)
    repo_propiedad = RepositorioPropiedadSQLite(db_manager)
    repo_renovacion = RepositorioRenovacionSQLite(db_manager)
    repo_ipc = RepositorioIPCSQLite(db_manager)
    repo_arrendatario = RepositorioArrendatarioSQLite(db_manager)
    repo_codeudor = RepositorioCodeudorSQLite(db_manager)

    servicio = ServicioContratos(
        db_manager,
        repo_mandato=repo_mandato,
        repo_arriendo=repo_arriendo,
        repo_propiedad=repo_propiedad,
        repo_renovacion=repo_renovacion,
        repo_ipc=repo_ipc,
        repo_arrendatario=repo_arrendatario,
        repo_codeudor=repo_codeudor,
    )

    print("\n--- Mandatos (Activos) ---")
    res_m = servicio.listar_mandatos_paginado(page=1, page_size=25, estado="Activo")
    print(f"Total: {res_m.total}")
    if res_m.items:
        print(f"Item 1: {res_m.items[0]}")

    print("\n--- Arrendamientos (Activos) ---")
    res_a = servicio.listar_arrendamientos_paginado(page=1, page_size=25, estado="Activo")
    print(f"Total: {res_a.total}")
    if res_a.items:
        print(f"Item 1: {res_a.items[0]}")

if __name__ == "__main__":
    simulate_load()
