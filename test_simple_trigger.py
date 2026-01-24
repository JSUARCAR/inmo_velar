import psycopg2

# Config from shared_db_config
try:
    from shared_db_config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
except ImportError:
    import sys
    import os
    # Add root to sys.path if running from subdir
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    try:
        from shared_db_config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
    except ImportError:
        # Fallback to env vars directly if shared config missing
        from dotenv import load_dotenv
        load_dotenv()
        DB_HOST = os.getenv("DB_HOST", "localhost")
        DB_PORT = os.getenv("DB_PORT", "5432")
        DB_NAME = os.getenv("DB_NAME", "db_inmo_velar")
        DB_USER = os.getenv("DB_USER", "inmo_user")
        DB_PASSWORD = os.getenv("DB_PASSWORD", "7323")


print("Testing trigger function directly in database...")

try:
    conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
    conn.autocommit = True
    cursor = cursor()
    
    # First just recreate the function
    print("Step 1: Creating audit function...")
    cursor.execute("""
        DROP FUNCTION IF EXISTS func_auditoria_cambios() CASCADE;
        
        CREATE FUNCTION func_auditoria_cambios()
        RETURNS TRIGGER AS $$
        DECLARE
            v_usuario TEXT;
            v_id_registro BIGINT;
        BEGIN
            -- Simple version for testing
            v_usuario := COALESCE(NEW.updated_by, NEW.created_by, OLD.updated_by, OLD.created_by, 'SISTEMA_DB');
            v_id_registro := -1;  -- Simplified for test
            
            IF TG_OP = 'INSERT' THEN
                INSERT INTO auditoria_cambios (tabla, id_registro, tipo_operacion, campo_modificado, valor_anterior, valor_nuevo, usuario, fecha_cambio)
                VALUES (TG_TABLE_NAME, v_id_registro, 'INSERT', 'ALL', NULL, '(Registro Creado)', v_usuario, NOW()::VARCHAR);
                RETURN NEW;
            ELSIF TG_OP = 'UPDATE' THEN
                INSERT INTO auditoria_cambios (tabla, id_registro, tipo_operacion, campo_modificado, valor_anterior, valor_nuevo, usuario, fecha_cambio)
                VALUES (TG_TABLE_NAME, v_id_registro, 'UPDATE', 'TEST', 'OLD', 'NEW', v_usuario, NOW()::VARCHAR);
                RETURN NEW;
            ELSIF TG_OP = 'DELETE' THEN
                INSERT INTO auditoria_cambios (tabla, id_registro, tipo_operacion, campo_modificado, valor_anterior, valor_nuevo, usuario, fecha_cambio)
                VALUES (TG_TABLE_NAME, v_id_registro, 'DELETE', 'ALL', '(Registro Eliminado)', NULL, v_usuario, NOW()::VARCHAR);
                RETURN OLD;
            END IF;
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;
    """)
    print("✓ Function created!")
    
    # Now try creating ONE trigger
    print("Step 2: Creating test trigger on 'ipc' table...")
    cursor.execute("""
        CREATE TRIGGER trg_audit_ipc_test 
        AFTER INSERT OR UPDATE OR DELETE ON ipc 
        FOR EACH ROW EXECUTE FUNCTION func_auditoria_cambios();
    """)
    print("✓ Trigger created!")
    
    print("\n[SUCCESS] Basic test passed - triggers can be created!")
    conn.close()

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
