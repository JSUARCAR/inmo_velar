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

def get_db_connection(is_source=True):
    if is_source:
        return psycopg2.connect(
            host=SRC_HOST, port=SRC_PORT, database=SRC_DB, user=SRC_USER, password=SRC_PASSWORD
        )
    else:
        return psycopg2.connect(DEST_URL)

def run_migration():
    print("--- STARTING ROBUST MIGRATION V2 ---")
    
    # 1. Get Views from Local
    print("\n1. Extracting Views from Local DB...")
    src_conn = get_db_connection(True)
    src_cursor = src_conn.cursor()
    src_cursor.execute("SELECT viewname, definition FROM pg_views WHERE schemaname = 'public'")
    views = src_cursor.fetchall()
    print(f"   Found {len(views)} views.")
    src_conn.close()

    dest_conn = get_db_connection(False)
    dest_conn.autocommit = True # We will manage transactions manually or just auto
    dest_cursor = dest_conn.cursor()

    # 2. Drop Views on Railway
    print("\n2. Dropping Views on Railway (to unlock schema)...")
    for view_name, _ in views:
        try:
            dest_cursor.execute(f'DROP VIEW IF EXISTS "{view_name}" CASCADE')
            print(f"   Dropped {view_name}")
        except Exception as e:
            print(f"   Error dropping {view_name}: {e}")

    # 3. Truncate Tables
    print("\n3. Truncating Railway Tables...")
    try:
        dest_cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        """)
        tables = [row[0] for row in dest_cursor.fetchall()]
        
        # Disable constraints?
        dest_cursor.execute("SET session_replication_role = 'replica';")
        
        for table in tables:
            dest_cursor.execute(f'TRUNCATE TABLE "{table}" CASCADE')
        print("   Truncation complete.")
    except Exception as e:
        print(f"   Truncation error: {e}")

    # 4. Fix Schema (Booleans)
    print("\n4. Fixing Schema (Forcing BOOLEAN types)...")
    for table, col in BOOLEAN_COLUMNS:
        try:
            # Try ALTER first
            dest_cursor.execute(f'ALTER TABLE "{table}" ALTER COLUMN "{col}" TYPE boolean USING "{col}"::boolean')
            print(f"   Fixed {table}.{col}")
        except psycopg2.errors.UndefinedTable:
             print(f"   Table {table} missing (skipping).")
        except psycopg2.errors.UndefinedColumn:
             print(f"   Column {table}.{col} missing (skipping).")
        except Exception as e:
            # Fallback: Drop and Add
            print(f"   Error altering {table}.{col}: {e}. Trying DROP/ADD...")
            try:
                dest_cursor.execute(f'ALTER TABLE "{table}" DROP COLUMN IF EXISTS "{col}" CASCADE')
                dest_cursor.execute(f'ALTER TABLE "{table}" ADD COLUMN "{col}" BOOLEAN DEFAULT TRUE')
                print(f"   Re-created column {table}.{col}")
            except Exception as e2:
                print(f"   CRITICAL: Could not fix {table}.{col}: {e2}")

    # 5. Copy Data
    print("\n5. Copying Data from Local -> Railway...")
    src_conn = get_db_connection(True)
    src_cursor = src_conn.cursor(cursor_factory=RealDictCursor)
    
    # Get table list again from source to be sure
    src_cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
    """)
    src_tables = [row['table_name'] for row in src_cursor.fetchall()]
    
    # Sort tables to avoid FK issues? session_replication_role='replica' handles it
    
    for table in src_tables:
        print(f"   Migrating {table}...")
        try:
            # Read
            src_cursor.execute(f'SELECT * FROM "{table}"')
            rows = src_cursor.fetchall()
            
            if not rows:
                print(f"     -> Empty.")
                continue
                
            columns = rows[0].keys()
            cols_str = ", ".join([f'"{c}"' for c in columns])
            placeholders = ", ".join(["%s"] * len(columns))
            
            # Write
            values = [list(row.values()) for row in rows]
            insert_query = f'INSERT INTO "{table}" ({cols_str}) VALUES ({placeholders})'
            dest_cursor.executemany(insert_query, values)
            print(f"     -> Copied {len(rows)} rows.")
            
        except Exception as e:
            print(f"     -> ERROR: {e}")
            # Try to continue with other tables

    # 6. Re-create Views
    print("\n6. Re-creating Views...")
    for view_name, definition in views:
        # Postgres stores definition as "SELECT ...". We need "CREATE VIEW ... AS SELECT ..."
        # But definition might be just the SELECT part.
        # pg_views.definition is text of query.
        create_sql = f'CREATE OR REPLACE VIEW "{view_name}" AS {definition}'
        try:
            dest_cursor.execute(create_sql)
            print(f"   Created {view_name}")
        except Exception as e:
            print(f"   Error creating view {view_name}: {e}")

    # 7. Cleanup
    dest_cursor.execute("SET session_replication_role = 'origin';")
    src_conn.close()
    dest_conn.close()
    print("\n--- MIGRATION COMPLETE ---")

if __name__ == "__main__":
    run_migration()
