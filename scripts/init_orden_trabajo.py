import sys
import os

# Add src to python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.infraestructura.persistencia.database import db_manager

def init_db():
    schema_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'infraestructura', 'db', 'schema_orden_trabajo.sql')
    print(f"Loading schema from: {schema_path}")
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
        db_manager.ejecutar_script(schema_sql)
        print("Schema ORDENES_TRABAJO executed successfully.")

if __name__ == "__main__":
    init_db()
