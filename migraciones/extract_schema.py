"""
Script para extraer el esquema completo de la base de datos SQLite
Genera un archivo JSON con toda la estructura para la migración
"""
import sqlite3
import json
from pathlib import Path

def extract_complete_schema(db_path):
    """Extrae el esquema completo de la base de datos SQLite"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    schema = {
        'tables': {},
        'views': [],
        'triggers': [],
        'indices': []
    }
    
    # 1. Obtener todas las tablas
    cursor.execute("""
        SELECT name, sql 
        FROM sqlite_master 
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """)
    
    tables = cursor.fetchall()
    
    for table_name, create_sql in tables:
        print(f"Procesando tabla: {table_name}")
        
        # Obtener información de columnas
        cursor.execute(f"PRAGMA table_info('{table_name}')")
        columns = cursor.fetchall()
        
        # Obtener claves foráneas
        cursor.execute(f"PRAGMA foreign_key_list('{table_name}')")
        foreign_keys = cursor.fetchall()
        
        schema['tables'][table_name] = {
            'create_sql': create_sql,
            'columns': [],
            'foreign_keys': []
        }
        
        for col in columns:
            cid, name, data_type, not_null, default_value, pk = col
            schema['tables'][table_name]['columns'].append({
                'cid': cid,
                'name': name,
                'type': data_type,
                'not_null': not_null,
                'default_value': default_value,
                'pk': pk
            })
        
        for fk in foreign_keys:
            fk_id, seq, table, from_col, to_col, on_update, on_delete, match = fk
            schema['tables'][table_name]['foreign_keys'].append({
                'table': table,
                'from': from_col,
                'to': to_col,
                'on_update': on_update,
                'on_delete': on_delete
            })
    
    # 2. Obtener todas las vistas
    cursor.execute("""
        SELECT name, sql 
        FROM sqlite_master 
        WHERE type='view'
        ORDER BY name
    """)
    
    for view_name, create_sql in cursor.fetchall():
        print(f"Procesando vista: {view_name}")
        schema['views'].append({
            'name': view_name,
            'sql': create_sql
        })
    
    # 3. Obtener todos los triggers
    cursor.execute("""
        SELECT name, tbl_name, sql 
        FROM sqlite_master 
        WHERE type='trigger'
        ORDER BY name
    """)
    
    for trigger_name, table_name, create_sql in cursor.fetchall():
        print(f"Procesando trigger: {trigger_name}")
        schema['triggers'].append({
            'name': trigger_name,
            'table': table_name,
            'sql': create_sql
        })
    
    # 4. Obtener todos los índices
    cursor.execute("""
        SELECT name, tbl_name, sql 
        FROM sqlite_master 
        WHERE type='index' AND sql IS NOT NULL
        ORDER BY name
    """)
    
    for index_name, table_name, create_sql in cursor.fetchall():
        print(f"Procesando índice: {index_name}")
        schema['indices'].append({
            'name': index_name,
            'table': table_name,
            'sql': create_sql
        })
    
    conn.close()
    return schema

if __name__ == '__main__':
    db_path = Path(__file__).parent / 'DB_Inmo_Velar.db'
    output_path = Path(__file__).parent / 'schema_extracted.json'
    
    print(f"Extrayendo esquema de: {db_path}")
    schema = extract_complete_schema(str(db_path))
    
    # Guardar esquema en JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(schema, f, indent=2, ensure_ascii=False)
    
    print(f"\n[OK] Esquema extraido exitosamente!")
    print(f"Guardado en: {output_path}")
    print(f"\nResumen:")
    print(f"   - Tablas: {len(schema['tables'])}")
    print(f"   - Vistas: {len(schema['views'])}")
    print(f"   - Triggers: {len(schema['triggers'])}")
    print(f"   - Índices: {len(schema['indices'])}")
