"""
Script para diagnosticar y reparar permisos del esquema public.
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def fix_schema_permissions():
    """Diagnostica y repara permisos del esquema public."""
    
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', 5432)),
            database=os.getenv('DB_NAME', 'db_inmo_velar'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', '')
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("=" * 60)
        print("DIAGNÓSTICO Y REPARACIÓN DE PERMISOS")
        print(f"Usuario conectado: {os.getenv('DB_USER')}")
        print("=" * 60)
        
        # 1. Verificar permisos actuales del esquema
        print("\n1. Verificando permisos del esquema public...")
        cursor.execute("""
            SELECT nspname, nspacl 
            FROM pg_namespace 
            WHERE nspname = 'public'
        """)
        result = cursor.fetchone()
        print(f"   Esquema: {result[0]}")
        print(f"   ACL actual: {result[1]}")
        
        # 2. Otorgar permisos al usuario postgres
        print("\n2. Otorgando permisos CREATE al usuario postgres...")
        cursor.execute("""
            GRANT CREATE, USAGE ON SCHEMA public TO postgres
        """)
        print("   ✓ Permisos otorgados a postgres")
        
        # 3. Otorgar permisos al usuario de la aplicación si existe
        print("\n3. Otorgando permisos a inmo_user (si existe)...")
        try:
            cursor.execute("""
                GRANT CREATE, USAGE ON SCHEMA public TO inmo_user
            """)
            print("   ✓ Permisos otorgados a inmo_user")
        except Exception as e:
            print(f"   ⚠ Usuario inmo_user no existe o ya tiene permisos: {e}")
        
        # 4. Verificar permisos después
        print("\n4. Verificando permisos actualizados...")
        cursor.execute("""
            SELECT nspname, nspacl 
            FROM pg_namespace 
            WHERE nspname = 'public'
        """)
        result = cursor.fetchone()
        print(f"   ACL actualizada: {result[1]}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ PERMISOS REPARADOS EXITOSAMENTE")
        print("=" * 60)
        print("\nAhora puedes ejecutar: python scripts\\create_permissions_tables.py")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = fix_schema_permissions()
    exit(0 if success else 1)
