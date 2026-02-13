import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

# Source: Local PostgreSQL
SRC_HOST = "localhost"
SRC_PORT = 5432
SRC_DB = "db_inmo_velar"
SRC_USER = "inmo_user"
SRC_PASSWORD = "7323"

# Destination: Railway PostgreSQL
DEST_URL = os.getenv("DATABASE_URL")

BOOLEAN_COLUMNS = [
    ("propiedades", "disponibilidad_propiedad"),
    ("propiedades", "estado_registro"),
    ("alertas", "resuelto_automaticamente"),
    ("archivos_adjuntos", "estado"),
    ("parametros_sistema", "modificable"),
    ("arrendatarios", "estado_arrendatario"),
    ("seguros", "estado_seguro"),
    ("proveedores", "estado_registro"),
    ("asesores", "estado"),
    ("codeudores", "estado_registro"),
    ("contratos_arrendamientos", "alerta_vencimiento_contrato_a"),
    ("contratos_arrendamientos", "alerta_ipc"),
    ("rol_permisos", "activo"),
    ("contratos_mandatos", "alerta_vencimineto_contrato_m"),
    ("historial_estados", "requirio_aprobacion"),
    ("ipc", "estado_registro"),
    ("municipios", "estado_registro"),
    ("personas", "estado_registro"),
    ("propietarios", "estado_propietario"),
    ("plantillas_notificaciones", "estado"),
    ("usuarios", "estado_usuario"),
]

def migrate_final():
    print("Connecting to SOURCE (Local PostgreSQL)...")
    try:
        src_conn = psycopg2.connect(
            host=SRC_HOST, port=SRC_PORT, database=SRC_DB, user=SRC_USER, password=SRC_PASSWORD
        )
        src_cursor = src_conn.cursor(cursor_factory=RealDictCursor)
    except Exception as e:
        print(f"Error connecting to SOURCE: {e}")
        return

    print("Connecting to DESTINATION (Railway PostgreSQL)...")
    try:
        dest_conn = psycopg2.connect(DEST_URL)
        dest_conn.autocommit = False 
        dest_cursor = dest_conn.cursor()
    except Exception as e:
        print(f"Error connecting to DESTINATION: {e}")
        src_conn.close()
        return

    # 1. TRUNCATE ALL TABLES
    print("\n--- STEP 1: TRUNCATE TABLES ---")
    try:
        dest_cursor.execute("SET session_replication_role = 'replica';") 
        
        # Get list of all tables
        dest_cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        """)
        tables = [row[0] for row in dest_cursor.fetchall()]
        
        for table in tables:
            print(f"Truncating {table}...")
            dest_cursor.execute(f'TRUNCATE TABLE "{table}" CASCADE;')
        
        dest_conn.commit()
        print("Truncation complete.")
    except Exception as e:
        print(f"Error truncating: {e}")
        dest_conn.rollback()
        # Continue? If truncate fails, migration is risky. But let's try.

    # 2. FIX SCHEMA (BOOLEANS)
    print("\n--- STEP 2: FIX SCHEMA (BOOLEANS) ---")
    try:
        for table, col in BOOLEAN_COLUMNS:
            print(f"Fixing {table}.{col} -> BOOLEAN")
            # We use USING to cast if there was data, but table is empty now so simple cast works
            try:
                dest_cursor.execute(f'ALTER TABLE "{table}" ALTER COLUMN "{col}" TYPE boolean USING "{col}"::boolean;')
            except psycopg2.errors.UndefinedTable:
                print(f"  -> Table {table} does not exist in destination (skipping)")
                dest_conn.rollback()
            except psycopg2.errors.UndefinedColumn:
                print(f"  -> Column {col} does not exist in {table} (skipping)")
                dest_conn.rollback()
            except Exception as e:
                print(f"  -> Error fixing {table}.{col}: {e}")
                dest_conn.rollback()
        
        dest_conn.commit()
        print("Schema fix complete.")
    except Exception as e:
        print(f"Global error in schema fix: {e}")
        dest_conn.rollback()

    # 3. COPY DATA
    print("\n--- STEP 3: COPY DATA ---")
    
    # Get source tables
    src_cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
    """)
    src_tables = [row['table_name'] for row in src_cursor.fetchall()]

    # Tables to skip (managed by system or problematic)
    SKIP_TABLES = [] # Add if needed

    for table in src_tables:
        if table in SKIP_TABLES:
            continue
            
        print(f"Migrating {table}...")
        try:
            # Read Source
            src_cursor.execute(f'SELECT * FROM "{table}"')
            rows = src_cursor.fetchall()
            
            if not rows:
                print(f"  -> Skipping empty table {table}")
                continue

            columns = rows[0].keys()
            cols_str = ", ".join([f'"{c}"' for c in columns])
            placeholders = ", ".join(["%s"] * len(columns))
            
            insert_query = f'INSERT INTO "{table}" ({cols_str}) VALUES ({placeholders})'
            
            values = [list(row.values()) for row in rows]
            
            # Write Destination
            dest_cursor.executemany(insert_query, values)
            print(f"  -> Copied {len(rows)} rows.")
            
        except Exception as e:
            print(f"  -> Error migrating {table}: {e}")
            dest_conn.rollback()

    # Restore constraints
    dest_cursor.execute("SET session_replication_role = 'origin';")
    dest_conn.commit()
    
    print("\n--- MIGRATION COMPLETED ---")
    src_conn.close()
    dest_conn.close()

if __name__ == "__main__":
    migrate_final()
