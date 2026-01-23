"""
Script agresivo para crear tablas de permisos - intenta múltiples métodos.
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def try_create_tables():
    """Intenta crear las tablas con diferentes estrategias."""
    
    db_name = os.getenv('DB_NAME', 'db_inmo_velar')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = int(os.getenv('DB_PORT', 5432))
    
    # Estrategias a probar
    strategies = [
        {'user': 'postgres', 'password': None, 'name': 'postgres sin contraseña'},
        {'user': 'postgres', 'password': '', 'name': 'postgres con string vacío'},
        {'user': 'postgres', 'password': 'postgres', 'name': 'postgres con contraseña por defecto'},
        {'user': 'inmo_user', 'password': '7323', 'name': 'inmo_user'}
    ]
    
    sql_create = """
    -- Tabla PERMISOS
    CREATE TABLE IF NOT EXISTS PERMISOS (
        ID_PERMISO SERIAL PRIMARY KEY,
        MODULO VARCHAR(100) NOT NULL,
        RUTA VARCHAR(200) NOT NULL,
        ACCION VARCHAR(20) NOT NULL,
        DESCRIPCION TEXT,
        CATEGORIA VARCHAR(50),
        CREATED_AT TIMESTAMP DEFAULT NOW(),
        UNIQUE(MODULO, ACCION)
    );
    
    CREATE INDEX IF NOT EXISTS idx_permisos_modulo ON PERMISOS(MODULO);
    CREATE INDEX IF NOT EXISTS idx_permisos_ruta ON PERMISOS(RUTA);
    
    -- Tabla ROL_PERMISOS
    CREATE TABLE IF NOT EXISTS ROL_PERMISOS (
        ID_ROL_PERMISO SERIAL PRIMARY KEY,
        ROL VARCHAR(50) NOT NULL,
        ID_PERMISO INTEGER NOT NULL,
        ACTIVO BOOLEAN DEFAULT TRUE,
        CREATED_BY VARCHAR(100),
        CREATED_AT TIMESTAMP DEFAULT NOW(),
        UPDATED_BY VARCHAR(100),
        UPDATED_AT TIMESTAMP,
        FOREIGN KEY (ID_PERMISO) REFERENCES PERMISOS(ID_PERMISO) ON DELETE CASCADE,
        UNIQUE(ROL, ID_PERMISO)
    );
    
    CREATE INDEX IF NOT EXISTS idx_rol_permisos_rol ON ROL_PERMISOS(ROL);
    CREATE INDEX IF NOT EXISTS idx_rol_permisos_activo ON ROL_PERMISOS(ACTIVO);
    
    -- Otorgar permisos
    DO $$
    BEGIN
        IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'inmo_user') THEN
            GRANT ALL ON PERMISOS TO inmo_user;
            GRANT ALL ON ROL_PERMISOS TO inmo_user;
            GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO inmo_user;
        END IF;
    END $$;
    """
    
    print("=" * 70)
    print("INTENTANDO CREAR TABLAS CON MÚLTIPLES ESTRATEGIAS")
    print("=" * 70)
    
    for strategy in strategies:
        print(f"\n🔄 Intentando: {strategy['name']}")
        
        try:
            # Construir parámetros de conexión
            conn_params = {
                'host': db_host,
                'port': db_port,
                'database': db_name,
                'user': strategy['user']
            }
            
            # Agregar password solo si no es None
            if strategy['password'] is not None:
                conn_params['password'] = strategy['password']
            
            conn = psycopg2.connect(**conn_params)
            conn.autocommit = True
            cursor = conn.cursor()
            
            print(f"   ✓ Conectado exitosamente")
            
            # Ejecutar CREATE TABLE
            cursor.execute(sql_create)
            print(f"   ✓ Tablas creadas")
            
            # Verificar
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_name IN ('permisos', 'rol_permisos')
            """)
            count = cursor.fetchone()[0]
            
            if count == 2:
                print(f"   ✅ ÉXITO: {count} tablas verificadas")
                cursor.close()
                conn.close()
                
                print("\n" + "=" * 70)
                print("✅ ¡TABLAS CREADAS EXITOSAMENTE!")
                print("=" * 70)
                return True
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            error_msg = str(e)
            if 'password' in error_msg.lower():
                print(f"   ✗ Error de autenticación")
            elif 'permission' in error_msg.lower() or 'permiso' in error_msg.lower():
                print(f"   ✗ Sin permisos CREATE")
            else:
                print(f"   ✗ Error: {error_msg[:100]}")
    
    print("\n" + "=" * 70)
    print("❌ TODAS LAS ESTRATEGIAS FALLARON")
    print("=" * 70)
    print("\nPor favor ejecuta manualmente el SQL en pgAdmin como superusuario.")
    return False

if __name__ == "__main__":
    success = try_create_tables()
    exit(0 if success else 1)
