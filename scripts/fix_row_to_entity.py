"""
Script para asegurar que row_dict esté definido en _row_to_entity si se usa.
Corrige archivos donde la migración automática rompió la conversión.
"""
import re
from pathlib import Path

SRC_DIR = Path('src/infraestructura/persistencia')
FILES_PATTERN = 'repositorio_*_sqlite.py'

MISSING_LOGIC = """        # Manejar tanto sqlite3.Row como dict (PostgreSQL)
        if row is None:
            return None
        
        # Convertir a dict si es necesario
        if hasattr(row, 'keys'):
            row_dict = dict(row)
        else:
            row_dict = row
"""

def fix_file(file_path):
    print(f"Checking {file_path.name}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return

    if 'def _row_to_entity' not in content:
        return

    # Verificar si usa row_dict pero no lo define
    if 'row_dict' in content and 'row_dict =' not in content:
        print(f"  Fixing missing row_dict definition in {file_path.name}")
        
        # Insertar lógica al inicio de _row_to_entity
        # Buscar def _row_to_entity(self, row...):
        pattern = r'(def _row_to_entity.*?:)'
        match = re.search(pattern, content)
        if match:
             # Check for docstring
            post_def = content[match.end():]
            insertion_point = match.end()
            
            # Simple heuristic: insert after docstring if exists, else after def line
            docstring_match = re.match(r'\s*"""(.*?)"""', post_def, re.DOTALL)
            if docstring_match:
                insertion_point += docstring_match.end()
            else:
                docstring_match_single = re.match(r"\s*'''(.*?)'''", post_def, re.DOTALL)
                if docstring_match_single:
                    insertion_point += docstring_match_single.end()
            
            # Insertar
            new_content = content[:insertion_point] + '\n' + MISSING_LOGIC + content[insertion_point:]
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("  [FIXED]")
    else:
        # Check if logic is duplicated or partial?
        pass

def main():
    for file_path in SRC_DIR.glob(FILES_PATTERN):
        fix_file(file_path)

if __name__ == '__main__':
    main()
