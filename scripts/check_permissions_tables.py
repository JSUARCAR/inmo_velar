"""
Verificación de tablas usando inmo_user.
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def check_tables():
    try:
        # Usar inmo_user con su contraseña
        db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 5432)),
            'database': os.getenv('DB_NAME', 'db_inmo_velar'),
            'user': 'inmo_user',  # Usuario con permisos establecidos
            'password': '7323'  # Contraseña del .env
        }
        
        print("=" * 60)
        print("VERIFICACIÓN DE TABLAS DE PERMISOS")
        print(f"Usuario: {db_config['user']}")
        print("=" * 60)
        
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('permisos', 'rol_permisos')
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        
        if tables:
            print(f"\n✅ {len(tables)} tabla(s) encontrada(s):")
            for table in tables:
                print(f"  - {table[0].upper()}")
                
                # Contar registros
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                count = cursor.fetchone()[0]
                print(f"    📊 Registros: {count}")
            
            print("\n" + "=" * 60)
            print("✅ TABLAS CREADAS EXITOSAMENTE")
            print("=" * 60)
            cursor.close()
            conn.close()
            return True
        else:
            print("\n❌ No se encontraron las tablas PERMISOS y ROL_PERMISOS")
            print("Por favor ejecuta el script SQL manualmente.")
            cursor.close()
            conn.close()
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    success = check_tables()
    exit(0 if success else 1)
