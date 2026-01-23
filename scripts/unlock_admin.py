
import sys
from pathlib import Path

# Agregar directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from src.infraestructura.persistencia.database import db_manager

def unlock_admin():
    conn = db_manager.obtener_conexion()
    cursor = conn.cursor()
    placeholder = db_manager.get_placeholder()
    
    try:
        username = 'admin'
        # Estado 1 for True/Active
        
        cursor.execute(
            f"""
            UPDATE USUARIOS 
            SET ESTADO_USUARIO = true
            WHERE NOMBRE_USUARIO = {placeholder}
            """,
            (username,)
        )
        
        rows = cursor.rowcount
        conn.commit()
        
        if rows > 0:
            print(f"✅ Usuario '{username}' desbloqueado exitosamente.")
        else:
            print(f"⚠️ No se encontró el usuario '{username}'.")
            
    except Exception as e:
        conn.rollback()
        print(f"❌ Error al desbloquear usuario: {e}")

if __name__ == "__main__":
    unlock_admin()
