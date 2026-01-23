import sys
import os

# Add the project root to the python path
sys.path.append(os.getcwd())

from src.infraestructura.persistencia.database import db_manager

def unlock_admin():
    print(f"Modo de base de datos: {db_manager.db_mode}")
    print(f"Usando PostgreSQL: {db_manager.use_postgresql}")

    sql = "UPDATE USUARIOS SET ESTADO_USUARIO = TRUE WHERE NOMBRE_USUARIO = 'admin'"
    if not db_manager.use_postgresql:
         sql = "UPDATE USUARIOS SET ESTADO_USUARIO = 1 WHERE NOMBRE_USUARIO = 'admin'"

    try:
        with db_manager.transaccion() as conn:
            cursor = conn.cursor()
            cursor.execute(sql)
            
            # Check if any row was updated
            if db_manager.use_postgresql:
                # cursor.rowcount works for Postgres
                rows_updated = cursor.rowcount
            else:
                # cursor.rowcount works for SQLite too usually
                rows_updated = cursor.rowcount
                
            print(f"Usuario 'admin' desbloqueado. Filas actualizadas: {rows_updated}")
            
    except Exception as e:
        print(f"Error al desbloquear usuario: {e}")

if __name__ == "__main__":
    unlock_admin()
