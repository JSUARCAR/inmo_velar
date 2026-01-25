
import sys
import os
import asyncio

# Add project root to sys.path
sys.path.insert(0, os.getcwd())

# Mock Reflex State
class MockState:
    def __init__(self):
        self.personas = []
        self.total_items = 0
        self.page = 1
        self.page_size = 10
        self.search_query = ""
        self.filtro_rol = "Todos"
        self.fecha_inicio = ""
        self.fecha_fin = ""
        self.is_loading = False
    
    # Copy load_personas method logic here to test it in isolation
    def load_personas(self):
        self.is_loading = True
        try:
            from src.infraestructura.persistencia.database import db_manager
            from src.aplicacion.servicios.servicio_personas import ServicioPersonas
            from src.infraestructura.persistencia.repositorio_persona_sqlite import RepositorioPersonaSQLite
            from src.infraestructura.persistencia.repositorio_propietario_sqlite import RepositorioPropietarioSQLite
            from src.infraestructura.persistencia.repositorio_arrendatario_sqlite import RepositorioArrendatarioSQLite
            from src.infraestructura.persistencia.repositorio_codeudor_sqlite import RepositorioCodeudorSQLite
            from src.infraestructura.persistencia.repositorio_asesor_sqlite import RepositorioAsesorSQLite
            from src.infraestructura.persistencia.repositorio_proveedores_sqlite import RepositorioProveedoresSQLite

            repo_persona = RepositorioPersonaSQLite(db_manager)
            repo_propietario = RepositorioPropietarioSQLite(db_manager)
            repo_arrendatario = RepositorioArrendatarioSQLite(db_manager)
            repo_codeudor = RepositorioCodeudorSQLite(db_manager)
            repo_asesor = RepositorioAsesorSQLite(db_manager)
            repo_proveedor = RepositorioProveedoresSQLite(db_manager)

            print("Instantiating ServicioPersonas...")
            servicio = ServicioPersonas(
                repo_persona=repo_persona,
                repo_propietario=repo_propietario,
                repo_arrendatario=repo_arrendatario,
                repo_codeudor=repo_codeudor,
                repo_asesor=repo_asesor,
                repo_proveedor=repo_proveedor,
            )
            print("ServicioPersonas instantiated successfully.")

            rol_filter = self.filtro_rol if self.filtro_rol != "Todos" else None

            print(f"Calling listar_personas_paginado with page={self.page}, rol={rol_filter}...")
            resultado = servicio.listar_personas_paginado(
                page=self.page,
                page_size=self.page_size,
                filtro_rol=rol_filter,
                busqueda=self.search_query if self.search_query else None,
                fecha_inicio=self.fecha_inicio if self.fecha_inicio else None,
                fecha_fin=self.fecha_fin if self.fecha_fin else None,
            )
            
            self.total_items = resultado.total
            print(f"Total items found: {self.total_items}")
            print(f"Items in current page: {len(resultado.items)}")

            self.personas = [
                {
                    "id": p.persona.id_persona,
                    "nombre": p.nombre_completo,
                    "roles": p.roles,
                }
                for p in resultado.items
            ]
            print("Successfully mapped personas.")
            for p in self.personas:
                print(f" - {p}")

        except Exception as e:
            print(f"CAUGHT EXCEPTION: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.is_loading = False

if __name__ == "__main__":
    print("Starting Runtime Verification for Personas...")
    state = MockState()
    state.load_personas()
    print("Verification complete.")
