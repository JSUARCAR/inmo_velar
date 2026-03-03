from src.infraestructura.persistencia.database import db_manager

def check_tables():
    conn = db_manager.obtener_conexion()
    cursor = db_manager.get_dict_cursor(conn)
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    rows = cursor.fetchall()
    # Con el dict cursor, las llaves suelen ser en mayúsculas dependiendo del driver
    print(f"Claves del primer row: {list(rows[0].keys()) if rows else 'Sin datos'}")
    tables = [row.get('TABLE_NAME') or row.get('table_name') for row in rows]
    print(f"Tablas encontradas: {tables}")
    conn.close()

if __name__ == "__main__":
    check_tables()
