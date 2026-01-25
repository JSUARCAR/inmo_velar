import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from src.infraestructura.persistencia.database import db_manager

if len(sys.argv) < 2:
    print("Usage: python execute_managed.py <sql_file_path>")
    sys.exit(1)

sql_file = sys.argv[1]

if not os.path.exists(sql_file):
    print(f"Error: File '{sql_file}' not found.")
    sys.exit(1)

print(f"Database Mode: {db_manager.db_mode}")
if db_manager.use_postgresql:
    print(f"Target: PostgreSQL ({db_manager.pg_config['host']}:{db_manager.pg_config['port']})")
else:
    print(f"Target: SQLite ({db_manager.database_path})")

try:
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    print(f"Executing script: {sql_file}")
    db_manager.ejecutar_script(sql_content)
    print("Execution SUCCESS.")

except Exception as e:
    print(f"Execution FAILED: {e}")
    sys.exit(1)
finally:
    db_manager.cerrar_todas_conexiones()
