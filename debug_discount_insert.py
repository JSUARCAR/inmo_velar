
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infraestructura.persistencia.database import db_manager
from src.dominio.entidades.descuento_asesor import DescuentoAsesor
from src.infraestructura.repositorios.repositorio_descuento_asesor_sqlite import RepositorioDescuentoAsesorSQLite

def debug_insert():
    print("Starting Debug Insert for Discount...")
    
    # 1. Check Placeholder
    ph = db_manager.get_placeholder()
    print(f"DB Placeholder: '{ph}'")
    
    # 2. Prepare Dummy Data
    # We need a valid ID_LIQUIDACION_ASESOR. In previous runs we created ID 13.
    # We'll try to insert for ID 13.
    id_liq = 13
    
    # 3. Manual Query Execution (Mimicking Repository)
    query = f"""
            INSERT INTO DESCUENTOS_ASESORES (
                ID_LIQUIDACION_ASESOR, TIPO_DESCUENTO, DESCRIPCION_DESCUENTO,
                VALOR_DESCUENTO, CREATED_BY
            ) VALUES ({ph}, {ph}, {ph}, {ph}, {ph})
            RETURNING ID_DESCUENTO_ASESOR
    """
    
    params = (id_liq, "Debug", "Debug Discount", 1000, "debug_user")
    
    print(f"Query: {query}")
    print(f"Params: {params}")
    
    try:
        with db_manager.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            print("Execute successful.")
            row = cursor.fetchone()
            print(f"Returned Row: {row}")
            conn.commit()
            print("Commit successful.")
            
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_insert()
