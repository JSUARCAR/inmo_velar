"""
Script de reparación para crear la tabla ROL_PERMISOS faltante.
"""
import sys
from pathlib import Path

# Agregar directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from src.infraestructura.persistencia.database import db_manager

def fix_missing_table():
    print("Iniciando reparación de tabla ROL_PERMISOS...")
    
    sql_create = """
    CREATE TABLE IF NOT EXISTS ROL_PERMISOS (
        ID_ROL_PERMISO SERIAL PRIMARY KEY,
        ROL VARCHAR(50) NOT NULL,
        ID_PERMISO INTEGER NOT NULL,
        ACTIVO BOOLEAN DEFAULT TRUE,
        CREATED_BY VARCHAR(100),
        CREATED_AT TIMESTAMP DEFAULT NOW(),
        UPDATED_BY VARCHAR(100),
        UPDATED_AT TIMESTAMP,
        CONSTRAINT fk_rol_permisos_permiso FOREIGN KEY (ID_PERMISO) 
            REFERENCES PERMISOS(ID_PERMISO) ON DELETE CASCADE,
        CONSTRAINT uk_rol_permisos_rol_permiso UNIQUE(ROL, ID_PERMISO)
    );
    
    CREATE INDEX IF NOT EXISTS idx_rol_permisos_rol ON ROL_PERMISOS(ROL);
    CREATE INDEX IF NOT EXISTS idx_rol_permisos_activo ON ROL_PERMISOS(ROL, ACTIVO);
    CREATE INDEX IF NOT EXISTS idx_rol_permisos_permiso ON ROL_PERMISOS(ID_PERMISO);
    """
    
    sql_grant = """
    DO $$
    BEGIN
        IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'inmo_user') THEN
            GRANT SELECT, INSERT, UPDATE, DELETE ON ROL_PERMISOS TO inmo_user;
            GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO inmo_user;
        END IF;
    END $$;
    """
    
    try:
        conn = db_manager.obtener_conexion()
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("1. Creando tabla ROL_PERMISOS...")
        cursor.execute(sql_create)
        print("   ✅ Tabla creada (o ya existía)")
        
        print("2. Asignando permisos a inmo_user...")
        cursor.execute(sql_grant)
        print("   ✅ Permisos asignados")
        
        print("\nVerificando existencia...")
        cursor.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'rol_permisos')")
        exists = cursor.fetchone()[0]
        
        if exists:
            print("✅ CONFIRMADO: La tabla 'rol_permisos' existe en la base de datos.")
        else:
            print("❌ ERROR: La tabla sigue sin aparecer en information_schema.")
            
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")

if __name__ == "__main__":
    fix_missing_table()
