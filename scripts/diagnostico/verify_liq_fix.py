import sys
import os

# Añadir root al path
sys.path.append(os.getcwd())

from src.infraestructura.persistencia.database import db_manager
from src.infraestructura.persistencia.repositorio_contrato_arrendamiento_postgres import RepositorioContratoArrendamientoPostgres

def verify_direction():
    print("Verificando carga de direcciones en Repositorio...")
    try:
        repo = RepositorioContratoArrendamientoPostgres(db_manager)
        
        # Buscar un asesor con contratos para probar
        conn = db_manager.obtener_conexion()
        cur = db_manager.get_dict_cursor(conn)
        cur.execute("SELECT ID_ASESOR FROM CONTRATOS_MANDATOS WHERE ESTADO_CONTRATO_M = 'Activo' LIMIT 1")
        row = cur.fetchone()
        
        if not row:
            print("No se encontraron asesores activos.")
            return
            
        id_asesor = row.get('id_asesor') or row.get('ID_ASESOR')
        print(f"Probando con Asesor ID: {id_asesor}")
        
        activos = repo.obtener_activos_por_asesor(id_asesor)
        if activos:
            for c in activos:
                direccion = getattr(c, 'direccion_propiedad', 'ATRIBUTO NO ENCONTRADO')
                print(f"Contrato {c.id_contrato_a}: Dirección = {direccion}")
                if direccion == 'ATRIBUTO NO ENCONTRADO' or direccion == 'Sin Dirección':
                    # Podría ser 'Sin Dirección' si la DB está vacía, pero si es 'ATRIBUTO NO ENCONTRADO' es error.
                    pass
        else:
            print("No se encontraron contratos activos para este asesor.")

    except Exception as e:
        print(f"Error en verificación: {e}")
    finally:
        db_manager.shutdown()

if __name__ == "__main__":
    verify_direction()
