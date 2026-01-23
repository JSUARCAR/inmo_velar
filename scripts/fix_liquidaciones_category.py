
import sys
from pathlib import Path

# Agregar directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from src.infraestructura.persistencia.database import db_manager

def fix_category():
    conn = db_manager.obtener_conexion()
    cursor = conn.cursor()
    placeholder = db_manager.get_placeholder()
    
    try:
        # Actualizar la categoría de los permisos APROBAR y PAGAR del módulo Liquidaciones
        # para que coincidan con 'Financiero' y se agrupen correctamente en la UI.
        target_actions = ['APROBAR', 'PAGAR']
        target_module = 'Liquidaciones'
        new_category = 'Financiero'
        
        for accion in target_actions:
            cursor.execute(
                f"""
                UPDATE PERMISOS 
                SET CATEGORIA = {placeholder}
                WHERE MODULO = {placeholder} AND ACCION = {placeholder}
                """,
                (new_category, target_module, accion)
            )
            
        conn.commit()
        print(f"✅ Categoría actualizada a '{new_category}' para permisos APROBAR y PAGAR de Liquidaciones.")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error al actualizar categoría: {e}")

if __name__ == "__main__":
    fix_category()
