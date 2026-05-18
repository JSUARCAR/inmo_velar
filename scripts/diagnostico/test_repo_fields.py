import sys
import os

# Añadir root al path
sys.path.append(os.getcwd())

from src.infraestructura.persistencia.repositorio_contrato_arrendamiento_postgres import RepositorioContratoArrendamientoPostgres
from src.infraestructura.persistencia.database import DatabaseManager

def test_fields():
    print("Iniciando prueba de campos del repositorio...")
    try:
        db = DatabaseManager() 
        repo = RepositorioContratoArrendamientoPostgres(db)
        
        # Primero buscar un asesor con contratos para que la prueba sea significativa
        conn = db.obtener_conexion()
        cur = db.get_dict_cursor(conn)
        cur.execute("SELECT ID_ASESOR, COUNT(*) FROM CONTRATOS_MANDATOS GROUP BY ID_ASESOR HAVING COUNT(*) > 0 LIMIT 1")
        row = cur.fetchone()
        
        if not row:
            print("No se encontraron asesores con contratos para probar.")
            return
            
        id_asesor = row.get("id_asesor") or row.get("ID_ASESOR")
        print(f"Probando con Asesor ID: {id_asesor}")
        
        print(f"\n--- Probando obtener_activos_por_asesor({id_asesor}) ---")
        activos = repo.obtener_activos_por_asesor(id_asesor)
        if activos:
            c = activos[0]
            print(f"Contrato ID: {c.id_contrato_a}")
            pct = getattr(c, 'comision_porcentaje_contrato_m', 'ATRIBUTO NO ENCONTRADO')
            id_m = getattr(c, 'id_contrato_m', 'ATRIBUTO NO ENCONTRADO')
            print(f"Comisión (attr): {pct}")
            print(f"ID Mandato (attr): {id_m}")
            
            if pct != 'ATRIBUTO NO ENCONTRADO' and id_m != 'ATRIBUTO NO ENCONTRADO':
                print("✅ Atributos inyectados correctamente en la entidad.")
            else:
                print("❌ Atributos NO encontrados en la entidad.")
        else:
            print(f"No se encontraron activos para asesor {id_asesor}")

        print(f"\n--- Probando obtener_detalle_contratos_asesor({id_asesor}) ---")
        detalles = repo.obtener_detalle_contratos_asesor(id_asesor)
        if detalles:
            d = detalles[0]
            print(f"Detalle ID: {d.get('ID_CONTRATO_A')}")
            pct = d.get('COMISION_PORCENTAJE_CONTRATO_M', 'LLAVE NO ENCONTRADA')
            print(f"Comisión (dict): {pct}")
            
            if pct != 'LLAVE NO ENCONTRADA':
                print("✅ Llave encontrada correctamente en el diccionario.")
            else:
                print("❌ Llave NO encontrada en el diccionario.")
        else:
            print(f"No se encontraron detalles para asesor {id_asesor}")

    except Exception as e:
        print(f"Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fields()
