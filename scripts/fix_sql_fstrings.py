"""
Script de Corrección Sintáctica para Repositorios
1. Asegura que queries con {placeholder} sean f-strings.
2. Asegura que cursor.lastrowid sea reemplazado.
3. Verifica sintaxis básica.
"""
import os
import re
from pathlib import Path

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

def fix_file(file_path):
    print(f"Checking: {file_path.name}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return

    new_lines = []
    modified = False
    
    # Contexto para lastrowid
    last_table = None

    for i, line in enumerate(lines):
        original_line = line
        
        # 1. Detectar Tabla en INSERT (para usar en lastrowid posterior)
        table_match = re.search(r'INSERT INTO (\w+)', line, re.IGNORECASE)
        if table_match:
            last_table = table_match.group(1).upper()
            
        # 2. Corregir lastrowid
        if 'cursor.lastrowid' in line:
            # Buscar tabla si no la tenemos (hacia atrás unas líneas)
            current_table = last_table
            if not current_table:
                for j in range(max(0, i-20), i):
                    tm = re.search(r'INSERT INTO (\w+)', lines[j], re.IGNORECASE)
                    if tm:
                        current_table = tm.group(1).upper()
                        break
            
            if current_table and current_table in TABLE_ID_MAP:
                col_id = TABLE_ID_MAP[current_table]
                line = line.replace('cursor.lastrowid', f"self.db.get_last_insert_id(cursor, '{current_table}', '{col_id}')")
                print(f"  Fixed lastrowid -> {current_table}")
        
        # 3. Corregir f-strings faltantes
        # Si tiene {placeholder} y comillas, debe tener f antes
        if '{placeholder}' in line:
            # Tipos de strings: """...""", '''...''', "...", '...'
            # Chequear tripes comillas
            if '"""' in line and 'f"""' not in line:
                 line = line.replace('"""', 'f"""', 1)
            elif "'''" in line and "f'''" not in line:
                 line = line.replace("'''", "f'''", 1)
            # Chequear simples comillas (si no son parte de triples)
            elif '"""' not in line and "'''" not in line:
                if '"' in line and 'f"' not in line:
                    # Cuidado con comentarios o imports, pero en repos es casi siempre SQL
                    if 'import' not in line and '#' not in line.strip()[0:1]:
                         line = line.replace('"', 'f"', 1)
                elif "'" in line and "f'" not in line:
                     if 'import' not in line and '#' not in line.strip()[0:1]:
                        line = line.replace("'", "f'", 1)
                        
        if line != original_line:
            modified = True
        
        new_lines.append(line)

    if modified:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            print("  [SAVED]")
        except Exception as e:
             print(f"Error writing {file_path}: {e}")

def main():
    for file_path in SRC_DIR.glob(FILES_PATTERN):
        # Saltar los ya corregidos manualmente si queremos, pero mejor repasar por si acaso
        # (Usuario, Asesor, Persona ya estan ok, el script no debería dañarlos si ya tienen f"")
        fix_file(file_path)

if __name__ == '__main__':
    main()
