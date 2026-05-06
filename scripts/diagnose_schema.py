"""
Script de diagnóstico para inspeccionar tablas y esquemas en PostgreSQL.
"""
import sys
import os
from pathlib import Path

# Agregar directorio raíz
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from src.infraestructura.persistencia.database import db_manager

def inspect_tables():
    print("="*60)
    print("DIAGNÓSTICO DE SCHEMA DE BASE DE DATOS")
    print("="*60)
    
    try:
        conn = db_manager.obtener_conexion()
        cursor = conn.cursor()
        
        # 1. Obtener información de conexión
        print(f"Modo DB: {db_manager.db_mode}")
        if db_manager.db_mode == "PostgreSQL":
            dsn = conn.get_dsn_parameters()
            print(f"Base de datos: {dsn.get('dbname')}")
            print(f"Usuario: {dsn.get('user')}")
            
            # 2. Listar todas las tablas en el esquema public
            print("\n--- Tablas en esquema 'public' ---")
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """)
            tables = cursor.fetchall()
            if not tables:
                print("(No se encontraron tablas)")
            for t in tables:
                print(f"- {t[0]}")
                
            # 3. Buscar tablas que contengan 'permiso' en cualquier esquema
            print("\n--- Búsqueda de tablas 'permiso' (case insensitive) ---")
            cursor.execute("""
                SELECT table_schema, table_name 
                FROM information_schema.tables 
                WHERE table_name ILIKE '%permiso%'
                ORDER BY table_schema, table_name;
            """)
            matches = cursor.fetchall()
            if not matches:
                print("(No se encontraron coincidencias)")
            for m in matches:
                print(f"- {m[0]}.{m[1]}")
                
        else:
            # SQLite diagnosis
            print("Diagnóstico para SQLite no implementado en detalle.")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    inspect_tables()
