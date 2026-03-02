
from src.infraestructura.persistencia.database import db_manager
from tabulate import tabulate

def list_users():
    conn = db_manager.obtener_conexion()
    cursor = db_manager.get_dict_cursor(conn)
    
    cursor.execute("SELECT ID_USUARIO, NOMBRE_USUARIO, ROL, ESTADO_USUARIO, FECHA_CREACION FROM USUARIOS")
    users = cursor.fetchall()
    
    # Convert to list of dicts if needed (depending on cursor type)
    if users and hasattr(users[0], 'keys'):
        users = [dict(u) for u in users]
        
    print(tabulate(users, headers="keys"))

if __name__ == "__main__":
    list_users()
