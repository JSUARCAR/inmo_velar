"""
Migration: Add FECHA_PAGO column to CONTRATOS_MANDATOS table.
"""

import sys
import os

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
# Adjusted path relative to src/infraestructura/db/migrations
project_root = os.path.abspath(os.path.join(current_dir, "../../../../"))
sys.path.insert(0, project_root)

from src.infraestructura.persistencia.database import db_manager

def migrate():
    print("Running migration: Add FECHA_PAGO to CONTRATOS_MANDATOS...")
    
    try:
        with db_manager.obtener_conexion() as conn:
            cursor = conn.cursor()
            
            try:
                # Use TEXT for SQLite compatibility (ISO8601 strings)
                cursor.execute("ALTER TABLE CONTRATOS_MANDATOS ADD COLUMN FECHA_PAGO TEXT;")
                conn.commit()
                print("Column FECHA_PAGO added successfully.")
            except Exception as e:
                # SQLite error for duplicate column
                if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                    print("Column FECHA_PAGO already exists.")
                else:
                    # Reraise heavily as it might be a real issue
                    raise e
                    
    except Exception as e:
        print(f"Error executing migration: {e}")

if __name__ == "__main__":
    migrate()
