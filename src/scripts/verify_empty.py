import sys
import os

# Add src to python path
sys.path.append(os.getcwd())

from src.infraestructura.persistencia.database import db_manager

tables_to_check = [
    "personas", "propietarios", "arrendatarios", "proveedores", "asesores", 
    "codeudores", "propiedades", "contratos_arrendamientos", "contratos_mandatos", 
    "liquidaciones_contratos", "liquidaciones_asesores", "liquidaciones", 
    "recaudos", "desocupaciones", "incidentes", "historial_incidentes", 
    "descuentos_asesores", "cotizaciones", "bonificaciones_asesores", "ipc", 
    "pagos_asesores", "recaudo_conceptos", "recibos_publicos", "rol_permisos", 
    "seguros", "sesiones_usuario", "tareas_desocupacion"
]

def verify_tables():
    print("Verifying tables are empty...")
    all_empty = True
    try:
        with db_manager.transaccion() as conn:
            cursor = conn.cursor()
            for table in tables_to_check:
                # Use double quotes for table names to handle case sensitivity/keywords
                cursor.execute(f'SELECT COUNT(*) FROM "{table}"')
                # UpperCaseCursorWrapper returns dict or list of dicts. fetchone returns a single dict.
                result = cursor.fetchone()
                # If result is dict, values() gives the count. If tuple/list, index 0.
                if hasattr(result, "values"):
                    count = list(result.values())[0]
                else:
                    count = result[0]
                
                if count > 0:
                    print(f"WARNING: Table '{table}' is NOT empty. Count: {count}")
                    all_empty = False
                # else:
                #     print(f"Table '{table}' is empty.")
    
    except Exception as e:
        print(f"Error checking tables: {e}")
        return

    if all_empty:
        print("All specified tables are empty.")
    else:
        print("Some tables are not empty.")

if __name__ == "__main__":
    verify_tables()
