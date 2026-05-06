"""
Script de RECONSTRUCCIÓN FORZADA de la tabla ROL_PERMISOS.
Este script elimina cualquier versión anterior y la crea explícitamente en el esquema public.
"""
import sys
from pathlib import Path
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Agregar directorio raíz
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from src.infraestructura.persistencia.database import db_manager

def force_recreate():
    print("="*60)
    print("RECONSTRUCCIÓN FORZADA DE TABLA: public.rol_permisos")
    print("="*60)
    
    print(f"Modo detectado: {db_manager.db_mode} (PG: {db_manager.use_postgresql})")
    
    if not db_manager.use_postgresql:
        print("❌ Este script es solo para PostgreSQL.")
        return

    try:
        # Usar conexión directa psycopg2 para evitar wrappers
        dsn_params = db_manager.obtener_conexion().get_dsn_parameters()
        password = os.getenv('DB_PASSWORD')
        # Reconstruir DSN string o pasar params
        conn = psycopg2.connect(
            dbname=dsn_params['dbname'],
            user=dsn_params['user'],
            password=password,
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432')
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print(f"Conectado a: {dsn_params['dbname']} como {dsn_params['user']}")
        
        # 1. Eliminar versiones anteriores (case insensitive y quoted)
        print("\n1. Eliminando tablas antiguas...")
        try:
            cursor.execute('DROP TABLE IF EXISTS public."ROL_PERMISOS" CASCADE;')
            print("   - DROP public.\"ROL_PERMISOS\" (Quoted): OK")
        except Exception as e:
            print(f"   - Advertencia drop quoted: {e}")
            
        try:
            cursor.execute('DROP TABLE IF EXISTS public.rol_permisos CASCADE;')
            print("   - DROP public.rol_permisos (Lowercase): OK")
        except Exception as e:
            print(f"   - Advertencia drop lower: {e}")

        # 2. Crear tabla NUEVA (usando lowercase standard)
        print("\n2. Creando tabla public.rol_permisos...")
        sql_create = """
        CREATE TABLE public.rol_permisos (
            id_rol_permiso SERIAL PRIMARY KEY,
            rol VARCHAR(50) NOT NULL,
            id_permiso INTEGER NOT NULL,
            activo BOOLEAN DEFAULT TRUE,
            created_by VARCHAR(100),
            created_at TIMESTAMP DEFAULT NOW(),
            updated_by VARCHAR(100),
            updated_at TIMESTAMP,
            CONSTRAINT fk_rol_permisos_permiso FOREIGN KEY (id_permiso) 
                REFERENCES public.permisos(id_permiso) ON DELETE CASCADE,
            CONSTRAINT uk_rol_permisos_rol_permiso UNIQUE(rol, id_permiso)
        );
        """
        # Nota: Asumimos que la tabla 'permisos' existe. Si está en mayúsculas, podría fallar la FK.
        # Vamos a verificar 'permisos' primero.
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_name ILIKE 'permisos'")
        permisos_exists = cursor.fetchone()
        if not permisos_exists:
            print("❌ CRÍTICO: La tabla 'permisos' no se encuentra. Abortando.")
            return
        
        print(f"   - Tabla padre detectada: {permisos_exists[0]}")
        # Ajustar FK si es necesario (Postgres es case insensitive si unquoted)
        
        cursor.execute(sql_create)
        print("   ✅ Tabla creada correctamente.")

        # 3. Indices
        print("\n3. Creando índices...")
        cursor.execute("CREATE INDEX idx_rol_permisos_rol ON public.rol_permisos(rol);")
        cursor.execute("CREATE INDEX idx_rol_permisos_activo ON public.rol_permisos(rol, activo);")
        print("   ✅ Índices creados.")

        # 4. Permisos
        print("\n4. Otorgando permisos a inmo_user...")
        cursor.execute("GRANT ALL PRIVILEGES ON TABLE public.rol_permisos TO inmo_user;")
        cursor.execute("GRANT ALL PRIVILEGES ON SEQUENCE public.rol_permisos_id_rol_permiso_seq TO inmo_user;")
        print("   ✅ Permisos otorgados.")

        # 5. Verificación final
        print("\n5. Verificación final...")
        cursor.execute("SELECT to_regclass('public.rol_permisos');")
        res = cursor.fetchone()
        if res and res[0]:
            print(f"   ✅ CONFIRMADO: La tabla existe como '{res[0]}'")
        else:
            print("   ❌ ERROR: La tabla no aparece en to_regclass.")

        conn.close()

    except Exception as e:
        print(f"\n❌ ERROR FATAL: {e}")
        import traceback
        traceback.print_exc()

import os
if __name__ == "__main__":
    force_recreate()
