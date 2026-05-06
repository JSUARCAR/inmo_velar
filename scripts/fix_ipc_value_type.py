
import sys
import os
import sqlite3

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.infraestructura.persistencia.database import db_manager

def migrate_db():
    print("Starting migration to fix IPC value type...")
    
    use_postgres = db_manager.use_postgresql
    print(f"Database Mode: {'PostgreSQL' if use_postgres else 'SQLite'}")
    
    try:
        if use_postgres:
            # PostgreSQL: Direct ALTER TABLE
            # We explicitly cast to ensure existing data is preserved
            script = """
            ALTER TABLE IPC 
            ALTER COLUMN VALOR_IPC TYPE DECIMAL(5,2);
            """
            print("Executing PostgreSQL migration...")
            db_manager.ejecutar_script(script)
            print("PostgreSQL migration completed.")
            
        else:
            # SQLite: Schema modification is limited.
            # Best robust way: Create new table, copy data, drop old, rename new.
            print("Executing SQLite migration (Full Table Rebuild)...")
            
            with db_manager.transaccion() as conn:
                cursor = conn.cursor()
                
                # Check if we need to migrate (check table info)
                cursor.execute("PRAGMA table_info(IPC)")
                columns = cursor.fetchall()
                valor_ipc_type = next((col['type'] for col in columns if col['name'] == 'VALOR_IPC'), 'UNKNOWN')
                
                print(f"Current VALOR_IPC type: {valor_ipc_type}")
                
                # Turn off foreign keys temporarily for table swap
                cursor.execute("PRAGMA foreign_keys = OFF;")
                
                # 1. Rename old table
                cursor.execute("ALTER TABLE IPC RENAME TO IPC_OLD;")
                
                # 2. Create new table with REAL type and explicit boolean check for ESTADO_REGISTRO (reinforcing previous fix)
                create_new_table = """
                CREATE TABLE IPC (
                    ID_IPC INTEGER PRIMARY KEY AUTOINCREMENT,
                    ANIO INTEGER UNIQUE NOT NULL,
                    VALOR_IPC REAL NOT NULL CHECK(VALOR_IPC >= 0 AND VALOR_IPC <= 10000),
                    FECHA_PUBLICACION TEXT,
                    ESTADO_REGISTRO INTEGER DEFAULT 1 CHECK(ESTADO_REGISTRO IN (0, 1)),
                    CREATED_AT TEXT DEFAULT (datetime('now', 'localtime')),
                    CREATED_BY TEXT
                );
                """
                cursor.execute(create_new_table)
                
                # 3. Copy data
                cursor.execute("""
                INSERT INTO IPC (ID_IPC, ANIO, VALOR_IPC, FECHA_PUBLICACION, ESTADO_REGISTRO, CREATED_AT, CREATED_BY)
                SELECT ID_IPC, ANIO, CAST(VALOR_IPC AS REAL), FECHA_PUBLICACION, ESTADO_REGISTRO, CREATED_AT, CREATED_BY
                FROM IPC_OLD;
                """)
                
                # 4. Verify data count matches
                cursor.execute("SELECT COUNT(*) FROM IPC_OLD")
                count_old = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM IPC")
                count_new = cursor.fetchone()[0]
                
                if count_old != count_new:
                    raise Exception(f"Migration mismatch! Old: {count_old}, New: {count_new}")
                
                # 5. Drop old table
                cursor.execute("DROP TABLE IPC_OLD;")
                
                # Turn FK back on
                cursor.execute("PRAGMA foreign_keys = ON;")
                
                print("SQLite migration completed.")
                
    except Exception as e:
        print(f"Migration FAILED: {e}")
        # In real scenario, transaction rollback handles DB state, but we log here.

if __name__ == "__main__":
    migrate_db()
