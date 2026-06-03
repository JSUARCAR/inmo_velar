"""
Script para deshabilitar la creación de tablas (DDL) en modo PostgreSQL.
Inserta 'if self.db.use_postgresql: return' al inicio de métodos _crear_tabla* o _ensure_table*.
"""
import re
from pathlib import Path

SRC_DIR = Path('src/infraestructura/persistencia')
FILES_PATTERN = 'repositorio_*_sqlite.py'

def fix_file(file_path):
    print(f"Checking DDL in: {file_path.name}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return

    new_lines = []
    modified = False
    
    for i, line in enumerate(lines):
        new_lines.append(line)
        
        # Detectar definición de método de creación de tabla
        if re.search(r'def _(crear_tabla|ensure_table)', line):
            # Verificar si ya tiene el guard
            # Mirar siguientes líneas (simple check)
            has_guard = False
            for forward_line in lines[i+1:i+5]: # Check next few lines
                if 'if self.db.use_postgresql: return' in forward_line:
                    has_guard = True
                    break
            
            if not has_guard:
                # Insertar guard
                indent = line.split('def')[0] # Capturar indentación
                guard = f"{indent}    if self.db.use_postgresql:\n{indent}        return\n"
                new_lines.append(guard)
                modified = True
                print(f"  Inserted PostgreSQL guard in {line.strip()}")

    if modified:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            print("  [SAVED]")
        except Exception as e:
             print(f"Error writing {file_path}: {e}")

def main():
    for file_path in SRC_DIR.glob(FILES_PATTERN):
        fix_file(file_path)

if __name__ == '__main__':
    main()
