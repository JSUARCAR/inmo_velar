
import sys
from pathlib import Path

# Agregar directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from src.infraestructura.persistencia.database import db_manager

def merge_module_permissions():
    conn = db_manager.obtener_conexion()
    cursor = conn.cursor()
    placeholder = db_manager.get_placeholder()
    
    try:
        # Unificar nombre del módulo a "Liquidación Asesores" (con tilde)
        # Esto moverá los permisos ANULAR, APROBAR, PAGAR al módulo correcto
        wrong_name = 'Liquidacion Asesores'
        correct_name = 'Liquidación Asesores'
        
        cursor.execute(
            f"""
            UPDATE PERMISOS 
            SET MODULO = {placeholder}
            WHERE MODULO = {placeholder}
            """,
            (correct_name, wrong_name)
        )
        
        rows = cursor.rowcount
        conn.commit()
        print(f"✅ Se actualizaron {rows} permisos de '{wrong_name}' a '{correct_name}'.")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error al unificar permisos: {e}")

if __name__ == "__main__":
    merge_module_permissions()
