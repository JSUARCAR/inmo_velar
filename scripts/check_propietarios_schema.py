
from src.infraestructura.persistencia.database import db_manager

def check_propietarios_schema():
    conn = db_manager.obtener_conexion()
    cursor = db_manager.get_dict_cursor(conn)
    
    # Ver columnas de PROPIETARIOS
    cursor.execute("SELECT * FROM PROPIETARIOS LIMIT 1")
    row = cursor.fetchone()
    if row:
        print(f"Columnas PROPIETARIOS: {list(row.keys())}")
    else:
        print("Tabla PROPIETARIOS vacía, consultando info schema...")
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'propietarios'")
        cols = [r.get('COLUMN_NAME') or r.get('column_name') for r in cursor.fetchall()]
        print(f"Columnas PROPIETARIOS (schema): {cols}")

    # Ver columnas de CONTRATOS_MANDATOS (para ver como se relaciona con propietario)
    cursor.execute("SELECT * FROM CONTRATOS_MANDATOS LIMIT 1")
    row_m = cursor.fetchone()
    if row_m:
        print(f"Columnas CONTRATOS_MANDATOS: {list(row_m.keys())}")

    conn.close()

if __name__ == "__main__":
    check_propietarios_schema()
