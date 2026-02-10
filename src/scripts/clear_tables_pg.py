import sys
import os

# Add src to python path
sys.path.append(os.getcwd())

from src.infraestructura.persistencia.database import db_manager

tables_to_clear = [
    "personas", "propietarios", "arrendatarios", "proveedores", "asesores", 
    "codeudores", "propiedades", "contratos_arrendamientos", "contratos_mandatos", 
    "liquidaciones_contratos", "liquidaciones_asesores", "liquidaciones", 
    "recaudos", "desocupaciones", "incidentes", "historial_incidentes", 
    "descuentos_asesores", "cotizaciones", "bonificaciones_asesores", "ipc", 
    "pagos_asesores", "recaudo_conceptos", "recibos_publicos", "rol_permisos", 
    "seguros", "sesiones_usuario", "tareas_desocupacion"
]

def clear_tables():
    print("Starting to clear tables...")
    try:
        with db_manager.transaccion() as conn:
            cursor = conn.cursor()
            
            # Construct the TRUNCATE command
            # Using CASCADE to handle foreign key constraints
            # We quote table names just in case, though usually lowercase is fine in PG
            # But let's verify if they exist first? No, TRUNCATE will fail if not exist, which is good.
            
            tables_str = ", ".join([f'"{t}"' for t in tables_to_clear])
            sql = f"TRUNCATE TABLE {tables_str} CASCADE;"
            
            print(f"Executing: {sql}")
            cursor.execute(sql)
            
            print("Tables cleared successfully.")
    except Exception as e:
        print(f"Error clearing tables: {e}")
        # Identify which table might be missing
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    clear_tables()
