
import os
import sys
import psycopg2
from psycopg2 import sql

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.infraestructura.persistencia.database import db_manager

def update_schema():
    print("Starting Schema Update for Bonuses/Additional Incomes...")
    
    conn = None
    try:
        conn = db_manager.obtener_conexion()
        if hasattr(conn, 'autocommit'):
            conn.autocommit = False # Handle transaction manually if possible, or use logic below
            
        cursor = conn.cursor()
        
        # 1. Add TOTAL_BONIFICACIONES to LIQUIDACIONES_ASESORES
        print("Checking LIQUIDACIONES_ASESORES...")
        try:
            # Check if column exists
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='liquidaciones_asesores' AND column_name='total_bonificaciones'
            """)
            if not cursor.fetchone():
                print("Adding TOTAL_BONIFICACIONES column...")
                cursor.execute("ALTER TABLE LIQUIDACIONES_ASESORES ADD COLUMN TOTAL_BONIFICACIONES INTEGER DEFAULT 0")
            else:
                print("TOTAL_BONIFICACIONES column already exists.")
        except Exception as e:
            # Maybe SQLite?
            if "sqlite" in str(type(conn)):
                print("SQLite detected. Checking PRAGMA...")
                cursor.execute("PRAGMA table_info(LIQUIDACIONES_ASESORES)")
                cols = [c[1] for c in cursor.fetchall()]
                if 'TOTAL_BONIFICACIONES' not in cols:
                    print("Adding TOTAL_BONIFICACIONES column (SQLite)...")
                    cursor.execute("ALTER TABLE LIQUIDACIONES_ASESORES ADD COLUMN TOTAL_BONIFICACIONES INTEGER DEFAULT 0")
                else:
                    print("TOTAL_BONIFICACIONES column already exists (SQLite).")
            else:
                raise e
        
        # COMMIT COLUMN ADD
        conn.commit()
        print("Column ADD Committed.")

        # 2. Create BONIFICACIONES_ASESORES table
        try:
            print("Checking BONIFICACIONES_ASESORES table...")
            
            # Determine syntax based on DB type (simple heuristic)
            is_sqlite = "sqlite" in str(type(conn)).lower()
            
            if is_sqlite:
                create_table_sql = """
                CREATE TABLE IF NOT EXISTS BONIFICACIONES_ASESORES (
                    ID_BONIFICACION_ASESOR INTEGER PRIMARY KEY AUTOINCREMENT,
                    ID_LIQUIDACION_ASESOR INTEGER NOT NULL,
                    TIPO_BONIFICACION VARCHAR(50) NOT NULL,
                    DESCRIPCION_BONIFICACION TEXT,
                    VALOR_BONIFICACION INTEGER NOT NULL,
                    FECHA_REGISTRO DATETIME DEFAULT CURRENT_TIMESTAMP,
                    CREATED_AT DATETIME DEFAULT CURRENT_TIMESTAMP,
                    CREATED_BY VARCHAR(50),
                    FOREIGN KEY(ID_LIQUIDACION_ASESOR) REFERENCES LIQUIDACIONES_ASESORES(ID_LIQUIDACION_ASESOR)
                )
                """
            else:
                # PostgreSQL
                create_table_sql = """
                CREATE TABLE IF NOT EXISTS BONIFICACIONES_ASESORES (
                    ID_BONIFICACION_ASESOR SERIAL PRIMARY KEY,
                    ID_LIQUIDACION_ASESOR INTEGER NOT NULL,
                    TIPO_BONIFICACION VARCHAR(50) NOT NULL,
                    DESCRIPCION_BONIFICACION TEXT,
                    VALOR_BONIFICACION INTEGER NOT NULL,
                    FECHA_REGISTRO TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    CREATED_BY VARCHAR(50),
                    CONSTRAINT fk_liquidacion_bono
                        FOREIGN KEY(ID_LIQUIDACION_ASESOR) 
                        REFERENCES LIQUIDACIONES_ASESORES(ID_LIQUIDACION_ASESOR)
                        ON DELETE CASCADE
                )
                """
                
            cursor.execute(create_table_sql)
            conn.commit()
            print("BONIFICACIONES_ASESORES table ensured.")
        except Exception as e_table:
            print(f"WARNING: Could not create detail table: {e_table}")
            conn.rollback() # Rollback only the failed table creation attempt if transaction was active (though we committed before)

        print("Schema Update Completed Successfully.")
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"ERROR updating schema: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    update_schema()
