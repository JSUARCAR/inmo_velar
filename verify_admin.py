import sys
import os

# Add the project root to the python path
sys.path.append(os.getcwd())

from src.infraestructura.persistencia.database import db_manager

def verify_admin():
    sql = "SELECT NOMBRE_USUARIO, ESTADO_USUARIO FROM USUARIOS WHERE NOMBRE_USUARIO = 'admin'"

    try:
        with db_manager.transaccion() as conn:
            cursor = db_manager.get_dict_cursor(conn)
            cursor.execute(sql)
            user = cursor.fetchone()
            
            if user:
                print(f"Usuario: {user.get('NOMBRE_USUARIO')}")
                print(f"Estado (Activo=True/1): {user.get('ESTADO_USUARIO')}")
                
                is_active = user.get('ESTADO_USUARIO')
                if is_active:
                    print("VERIFICACIÓN EXITOSA: El usuario está activo.")
                else:
                    print("VERIFICACIÓN FALLIDA: El usuario sigue inactivo.")
            else:
                print("Usuario 'admin' no encontrado.")
            
    except Exception as e:
        print(f"Error al verificar usuario: {e}")

if __name__ == "__main__":
    verify_admin()
