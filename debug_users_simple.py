
from src.infraestructura.persistencia.database import db_manager
import sys

def check_user():
    print("Checking for user 'losorio'...")
    try:
        conn = db_manager.obtener_conexion()
        cursor = db_manager.get_dict_cursor(conn)
        
        # Check strict
        cursor.execute("SELECT * FROM USUARIOS WHERE NOMBRE_USUARIO = 'losorio'")
        user = cursor.fetchone()
        if user:
            print(f"FOUND STRICT: {dict(user)}")
        else:
            print("NOT FOUND STRICT")
            
        # Check case insensitive
        cursor.execute("SELECT * FROM USUARIOS WHERE LOWER(NOMBRE_USUARIO) = 'losorio'")
        user_lower = cursor.fetchone()
        if user_lower:
            print(f"FOUND LOWER: {dict(user_lower)}")
        else:
            print("NOT FOUND LOWER")
            
        # List all for good measure
        print("\nALL USERS:")
        cursor.execute("SELECT ID_USUARIO, NOMBRE_USUARIO, ESTADO_USUARIO FROM USUARIOS")
        for row in cursor.fetchall():
            print(dict(row))
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    check_user()
