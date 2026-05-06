
import sqlite3
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.infraestructura.configuracion.settings import obtener_configuracion

def fix_renovaciones_schema():
    config = obtener_configuracion()
    db_path = config.database_path
    print(f"Fixing schema in: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. Drop existing table
        print("Dropping RENOVACIONES_CONTRATOS...")
        cursor.execute("DROP TABLE IF EXISTS RENOVACIONES_CONTRATOS")
        
        # 2. Re-create with CORRECT Foreign Keys
        print("Re-creating RENOVACIONES_CONTRATOS with correct FKs...")
        create_sql = """
        CREATE TABLE RENOVACIONES_CONTRATOS (
            ID_RENOVACION INTEGER PRIMARY KEY AUTOINCREMENT,
            ID_CONTRATO_M INTEGER,
            ID_CONTRATO_A INTEGER,
            TIPO_CONTRATO TEXT NOT NULL CHECK(TIPO_CONTRATO IN ('Mandato', 'Arrendamiento')),
            FECHA_INICIO_ORIGINAL TEXT NOT NULL,
            FECHA_FIN_ORIGINAL TEXT NOT NULL,
            FECHA_INICIO_RENOVACION TEXT NOT NULL,
            FECHA_FIN_RENOVACION TEXT NOT NULL,
            CANON_ANTERIOR INTEGER NOT NULL,
            CANON_NUEVO INTEGER NOT NULL,
            PORCENTAJE_INCREMENTO INTEGER,
            MOTIVO_RENOVACION TEXT,
            FECHA_RENOVACION TEXT DEFAULT (date('now')),
            CREATED_AT TEXT DEFAULT (datetime('now', 'localtime')),
            CREATED_BY TEXT,
            
            -- FKs corrected to point to MAIN tables
            FOREIGN KEY (ID_CONTRATO_M) REFERENCES CONTRATOS_MANDATOS(ID_CONTRATO_M),
            FOREIGN KEY (ID_CONTRATO_A) REFERENCES CONTRATOS_ARRENDAMIENTOS(ID_CONTRATO_A),
            
            CHECK((ID_CONTRATO_M IS NOT NULL AND ID_CONTRATO_A IS NULL) OR (ID_CONTRATO_M IS NULL AND ID_CONTRATO_A IS NOT NULL))
        )
        """
        cursor.execute(create_sql)
        print("Table re-created successfully.")
        
        conn.commit()
        
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_renovaciones_schema()
