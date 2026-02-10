import sys
import os

# Add src to python path
sys.path.append(os.getcwd())

from src.infraestructura.persistencia.database import db_manager

def list_tables():
    print("Listing tables...")
    try:
        with db_manager.transaccion() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
            tables = cursor.fetchall()
            for table in tables:
                # cursor returns dict if configured with RealDictCursor wrapper in db_manager
                # db_manager returns UpperCaseCursorWrapper which returns dict with upper keys
                if isinstance(table, dict):
                    print(table.get('TABLE_NAME'))
                else:
                    print(table[0])
    except Exception as e:
        print(f"Error listing tables: {e}")

if __name__ == "__main__":
    list_tables()
