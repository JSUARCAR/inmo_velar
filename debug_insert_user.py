
from src.infraestructura.persistencia.database import db_manager
from src.dominio.entidades.usuario import Usuario
from datetime import datetime
import traceback

def try_insert_user():
    print("Attempting to insert user 'losorio_debug'...")
    try:
        conn = db_manager.obtener_conexion()
        cursor = conn.cursor()
        
        # Hardcoded insert to mimic repository
        placeholder = db_manager.get_placeholder()
        
        # Determine sequence name if possible (Postgres usually table_column_seq)
        # But first let's just try insert and see error
        
        query = f"""
        INSERT INTO USUARIOS (
            NOMBRE_USUARIO,
            CONTRASENA_HASH,
            ROL,
            ESTADO_USUARIO,
            ULTIMO_ACCESO,
            FECHA_CREACION,
            CREATED_BY
        ) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
        """
        
        cursor.execute(query, (
            "losorio_debug",
            "hash_dummy",
            "Asesor",
            True,
            None,
            datetime.now().isoformat(),
            "debug_script"
        ))
        
        conn.commit()
        print("INSERT SUCCESSFUL")
        
        # Cleanup
        cursor.execute(f"DELETE FROM USUARIOS WHERE NOMBRE_USUARIO = {placeholder}", ("losorio_debug",))
        conn.commit()
        print("CLEANUP SUCCESSFUL")
        
    except Exception as e:
        print("INSERT FAILED")
        print(f"Error Type: {type(e)}")
        print(f"Error Message: {e}")
        # traceback.print_exc()

if __name__ == "__main__":
    try_insert_user()
