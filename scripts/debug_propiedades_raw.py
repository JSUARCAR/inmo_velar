
from src.infraestructura.persistencia.database import db_manager

def debug_propiedades_raw():
    print("--- DIAGNÓSTICO DE PROPIEDADES (RAW) ---")
    conn = db_manager.obtener_conexion()
    cursor = db_manager.get_dict_cursor(conn)
    
    # 1. Ver total sin filtros
    cursor.execute("SELECT COUNT(*) as count FROM PROPIEDADES")
    total = cursor.fetchone()["COUNT"]
    print(f"Total absoluto en PROPIEDADES: {total}")
    
    if total > 0:
        # 2. Ver una muestra para chequear tipos
        cursor.execute("SELECT * FROM PROPIEDADES LIMIT 1")
        sample = cursor.fetchone()
        print(f"Muestra de Propiedad: {sample}")
        
        # 3. Probar filtros específicos
        cursor.execute("SELECT COUNT(*) as count FROM PROPIEDADES WHERE ESTADO_REGISTRO IS TRUE")
        activos = cursor.fetchone()["COUNT"]
        print(f"Total con ESTADO_REGISTRO IS TRUE: {activos}")

        cursor.execute("SELECT COUNT(*) as count FROM PROPIEDADES WHERE ESTADO_REGISTRO = TRUE")
        activos_eq = cursor.fetchone()["COUNT"]
        print(f"Total con ESTADO_REGISTRO = TRUE: {activos_eq}")
        
        cursor.execute("SELECT COUNT(*) as count FROM PROPIEDADES WHERE DISPONIBILIDAD_PROPIEDAD IS TRUE")
        disp = cursor.fetchone()["COUNT"]
        print(f"Total con DISPONIBILIDAD_PROPIEDAD IS TRUE: {disp}")

    conn.close()

if __name__ == "__main__":
    debug_propiedades_raw()
