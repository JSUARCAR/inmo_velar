import sys
import os

# Add src to python path
sys.path.append(os.getcwd())

from src.infraestructura.configuracion.settings import obtener_configuracion
from src.infraestructura.persistencia.database import db_manager

config = obtener_configuracion()
print(f"DB_MODE from env: {os.getenv('DB_MODE')}")
print(f"DB_MODE from manager: {db_manager.db_mode}")
print(f"Is PostgreSQL: {db_manager.use_postgresql}")
if not db_manager.use_postgresql:
    print(f"SQLite Path: {db_manager.database_path}")
else:
    print(f"Postgres Config: {db_manager.pg_config}")
