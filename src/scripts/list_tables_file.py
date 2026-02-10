import sys
import os

# Add src to python path
sys.path.append(os.getcwd())

from src.infraestructura.persistencia.database import db_manager

def list_tables():
    try:
        with db_manager.transaccion() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;")
            tables = cursor.fetchall()
            with open("tables.txt", "w") as f:
                for table in tables:
                    if isinstance(table, dict):
                        f.write(table.get('TABLE_NAME') + "\n")
                    else:
                        f.write(table[0] + "\n")
            print("Tables listed to tables.txt")
    except Exception as e:
        print(f"Error listing tables: {e}")

if __name__ == "__main__":
    list_tables()
