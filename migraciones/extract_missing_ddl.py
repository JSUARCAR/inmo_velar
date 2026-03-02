import psycopg2
import sys

# Source: Local PostgreSQL
SRC_HOST = "localhost"
SRC_PORT = 5432
SRC_DB = "db_inmo_velar"
SRC_USER = "inmo_user"
SRC_PASSWORD = "7323"

def extract_ddl():
    conn = psycopg2.connect(
        host=SRC_HOST, port=SRC_PORT, database=SRC_DB, user=SRC_USER, password=SRC_PASSWORD
    )
    cursor = conn.cursor()
    
    print("--- EXTRACTING DDL ---")
    
    # Get columns for bonificaciones_asesores
    cursor.execute("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_name = 'bonificaciones_asesores'
    """)
    cols = cursor.fetchall()
    
    if not cols:
        print("Table 'bonificaciones_asesores' not found in local DB!")
        return

    create_stmt = "CREATE TABLE IF NOT EXISTS bonificaciones_asesores (\n"
    col_defs = []
    for col_name, dtype, nullable, default in cols:
        nullable_str = "NULL" if nullable == "YES" else "NOT NULL"
        default_str = f"DEFAULT {default}" if default else ""
        col_defs.append(f"    {col_name} {dtype} {nullable_str} {default_str}")
    
    create_stmt += ",\n".join(col_defs)
    create_stmt += "\n);"
    
    print(create_stmt)
    conn.close()

if __name__ == "__main__":
    extract_ddl()
