"""
Script de Migración Masiva de Repositorios (SQLite -> Dual SQLite/PostgreSQL)
Actualiza sintaxis, placeholders y manejo de resultados.
"""
import os
import re
from pathlib import Path

# Configuración
SRC_DIR = Path('src/infraestructura/persistencia')
FILES_PATTERN = 'repositorio_*_sqlite.py'

# Mapeo de Tablas a Columnas ID (para lastrowid)
TABLE_ID_MAP = {
    'PROPIEDADES': 'ID_PROPIEDAD',
    'USUARIOS': 'ID_USUARIO',
    'PERSONAS': 'ID_PERSONA',
    'CLIENTES': 'ID_CLIENTE',
    'PROPIETARIOS': 'ID_PROPIETARIO',
    'ARRENDATARIOS': 'ID_ARRENDATARIO',
    'CODEUDORES': 'ID_CODEUDOR',
    'CONTRATOS_ARRENDAMIENTOS': 'ID_CONTRATO_A',
    'CONTRATOS_MANDATOS': 'ID_CONTRATO_M',
    'LIQUIDACIONES': 'ID_LIQUIDACION',
    'RECAUDOS': 'ID_RECAUDO',
    'MUNICIPIOS': 'ID_MUNICIPIO',
    'ASESORES': 'ID_ASESOR',
    'SEGUROS': 'ID_SEGURO',
    'POLIZAS': 'ID_POLIZA',
    'DESOCUPACIONES': 'ID_DESOCUPACION',
    'INCIDENTES': 'ID_INCIDENTE',
    'IPC': 'ID_IPC',
    'RENOVACIONES': 'ID_RENOVACION',
    'PROVEEDORES': 'ID_PROVEEDOR',
    'AUDITORIA': 'ID_AUDITORIA',
    'PARAMETROS': 'ID_PARAMETRO'
}

def process_file(file_path):
    print(f"Procesando: {file_path.name}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 1. Actualizar _row_to_entity para manejar diccionarios y Row
    if '_row_to_entity' in content:
        # Detectar indentación
        match = re.search(r'(\s+)def _row_to_entity', content)
        indent = match.group(1) if match else '    '
        
        # Nueva lógica para manejar dicts
        dict_logic = f"""
{indent}    # Manejar tanto sqlite3.Row como dict (PostgreSQL)
{indent}    if row is None:
{indent}        return None
{indent}    
{indent}    # Convertir a dict si es necesario
{indent}    if hasattr(row, 'keys'):
{indent}        row_dict = dict(row)
{indent}    else:
{indent}        row_dict = row
"""
        # Reemplazar acceso directo row['COL'] por row_dict.get('col') or row_dict.get('COL')
        # Esto es complejo de hacer con regex simple, vamos a inyectar la normalización al principio de la función
        # y luego reemplazar row[...] por row_dict.get(...)
        
        # Paso simplificado: Insertar la lógica al inicio de la función
        content = re.sub(
            r'(def _row_to_entity.*?:[^"]*?""".*?""")',
            r'\1' + dict_logic,
            content,
            flags=re.DOTALL
        )
        
        # Reemplazar usages: row['COLUMNA'] -> (row_dict.get('columna') or row_dict.get('COLUMNA'))
        # Nota: las claves en dict de Postgres suelen ser minúsculas
        def replace_access(m):
            col = m.group(1)
            col_lower = col.lower()
            return f"(row_dict.get('{col_lower}') or row_dict.get('{col}'))"
            
        content = re.sub(r"row\['(\w+)'\]", replace_access, content)

    # 2. Reemplazar Context Manager y Row Factory
    # with self.db.obtener_conexion() as conn:
    #     conn.row_factory = sqlite3.Row
    #     cursor = conn.cursor()
    
    # Patrón común en métodos de lectura
    pattern_read = r'with self\.db\.obtener_conexion\(\) as conn:\s+conn\.row_factory = sqlite3\.Row\s+cursor = conn\.cursor\(\)'
    replacement_read = """conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()"""
    
    content = re.sub(pattern_read, replacement_read, content)
    
    # Patrón alternativo (solo row_factory)
    content = re.sub(r'conn\.row_factory = sqlite3\.Row', '', content)
    
    # 3. Reemplazar cursor = conn.cursor() simple por get_dict_cursor + placeholder en lecturas
    # (Donde no matchéo el bloque grande)
    # Esto es arriesgado si no es lectura. Asumimos que si hay SELECT, necesitamos dict cursor.
    
    # 4. Manejar Métodos de Escritura (INSERT/UPDATE)
    # with self.db.obtener_conexion() as conn: -> conn = self.db.obtener_conexion()
    # cursor = conn.cursor()
    
    # Si encontramos ? en queries, necesitamos placeholder
    if '?' in content:
        # Asegurar que placeholder esté definido si usamos ?
        if 'placeholder =' not in content:
             # Estrategia: reemplazar 'cursor = conn.cursor()' por 'cursor = conn.cursor()\n        placeholder = self.db.get_placeholder()'
             content = re.sub(r'(cursor = conn\.cursor\(\))', r'\1\n            placeholder = self.db.get_placeholder()', content)

        # Reemplazar ? por {placeholder} y hacer f-strings
        # Buscar: cursor.execute("""... ? ...""", params)
        
        def replace_query(m):
            query = m.group(1)
            params = m.group(2)
            
            if '?' in query:
                new_query = query.replace('?', '{placeholder}')
                # Verificar si ya es f-string
                prefix = 'f' if not query.strip().startswith('f') else ''
                # Si empieza con """ o ", agregar f
                if query.strip().startswith('"""'):
                    new_query = f'f"""{new_query[3:-3]}"""'
                elif query.strip().startswith('"'):
                    new_query = f'f"{new_query[1:-1]}"'
                elif query.strip().startswith("'"):
                    new_query = f"f'{new_query[1:-1]}'"
                
                return f"cursor.execute({new_query}, {params}"
            return m.group(0)

        # Regex básica para cursor.execute(...)
        # Nota: Esto es frágil con multilineas complejas, pero los repos tienen estructura muy standard
        # cursor.execute(QUERY, PARAMS)
        # Intentemos reemplazar ? por {placeholder} en todo el archivo dentro de strings SQL?
        # Mejor: reemplazar '?' por '{placeholder}' SÓLO si hay cursor.execute cerca?
        pass

    # Estrategia Alternativa Robusta para Queries:
    # Reemplazar `?` por `{placeholder}` globalmente en el archivo NO ES SEGURO.
    # Pero en estos repositorios, ? se usa casi exclusivamente para binding SQL.
    # Vamos a usar una función que itera linea por linea para detectar contextos SQL.
    
    lines = content.split('\n')
    new_lines = []
    in_sql = False
    
    for line in lines:
        # Detectar placeholders ?
        if '?' in line and ('SELECT' in line or 'INSERT' in line or 'UPDATE' in line or 'VALUES' in line or 'WHERE' in line or 'SET' in line):
            line = line.replace('?', '{placeholder}')
            
        # Detectar inicio de cursor.execute con f-string
        if 'cursor.execute(' in line:
            if 'f"' not in line and "f'" not in line and 'f"""' not in line:
                 if '{placeholder}' in line or (len(new_lines) > 0 and '{placeholder}' in new_lines[-1]): 
                     # Convertir a f-string
                     line = line.replace('"""', 'f"""').replace("'''", "f'''")
                     if 'f"""' not in line and "f'''" not in line: # single line strings
                         if '"' in line: line = line.replace('"', 'f"', 1)
                         elif "'" in line:  line = line.replace("'", "f'", 1)
        
        # Si estamos dentro de un bloque SQL multilinea que ya fue marcado como f-string
        # y contiene {placeholder}, está bien.
        
        # 5. lastrowid
        # usuario.id = cursor.lastrowid
        if 'cursor.lastrowid' in line:
            # Buscar tabla en lineas anteriores
            table_name = None
            for prev_line in reversed(new_lines[-20:]): # Buscar hacia atrás
                match_table = re.search(r'INSERT INTO (\w+)', prev_line)
                if match_table:
                    table_name = match_table.group(1)
                    break
            
            if table_name and table_name in TABLE_ID_MAP:
                id_col = TABLE_ID_MAP[table_name]
                line = line.replace('cursor.lastrowid', f"self.db.get_last_insert_id(cursor, '{table_name}', '{id_col}')")
            else:
                print(f"  [WARN] No se pudo inferir tabla para lastrowid en línea: {line.strip()}")
        
        new_lines.append(line)

    content = '\n'.join(new_lines)
    
    # Arreglo final: Asegurarse que import sqlite3 no sea el único (aunque database manager abstrae, los tipos se usan)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("  [MODIFICADO]")
        return True
    else:
        print("  [SIN CAMBIOS]")
        return False

def main():
    print("Iniciando migración masiva...")
    count = 0
    for file_path in SRC_DIR.glob(FILES_PATTERN):
        if file_path.name == 'repositorio_usuario_sqlite.py':
            continue # Ya actualizado
            
        try:
            if process_file(file_path):
                count += 1
        except Exception as e:
            print(f"  [ERROR] {file_path.name}: {e}")
            import traceback
            traceback.print_exc()
            
    print(f"\nFinalizado. {count} archivos actualizados.")

if __name__ == '__main__':
    main()
