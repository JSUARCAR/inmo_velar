"""
Script para corregir automáticamente errores de indentación reportados por compileall.
Lee compile_errors.txt y reduce la indentación en los bloques afectados.
"""
import re
from pathlib import Path

def get_indentation(line):
    return len(line) - len(line.lstrip())

def fix_file_indentation(file_path, error_line_num):
    print(f"Fixing {file_path.name} around line {error_line_num}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    if error_line_num > len(lines):
        return

    # Índice 0-based
    idx = error_line_num - 1
    
    # Determinar indentación objetivo (la línea anterior no vacía suele tener la correcta, o ser la declaración de variables)
    # Buscamos hacia atrás una línea con menos indentación
    target_indent = 8 # Estándar dentro de método de clase en Python
    
    # Identificar el bloque a des-indentar
    # Empieza en idx. Termina cuando la indentación vuelve a ser menor o igual a target_indent (pero cuidado con lineas vacias)
    
    initial_indent = get_indentation(lines[idx])
    if initial_indent <= target_indent:
        print(f"  Skipping: indent {initial_indent} seems correct (<= {target_indent})")
        return

    # Reducimos 4 espacios
    dedent_amount = 4
    
    lines_modified = 0
    i = idx
    while i < len(lines):
        line = lines[i]
        if not line.strip(): # Línea vacía, ignorar o des-indentar igual
            i += 1
            continue
            
        current_indent = get_indentation(line)
        
        # Si la indentación es menor que la inicial del bloque, terminó el bloque
        # (A menos que sea cierre de paréntesis?)
        if current_indent < initial_indent:
            # Check if it is a closing parenthesis aligned with the start?
            # Usually closing parenthesis ) is indented same as start.
            if line.strip().startswith(')') and current_indent == initial_indent - 4:
                # It's part of the block but already dedented? No, usually dedent logic applies.
                pass
            else:
                 break
        
        # Aplicar des-indentación
        if current_indent >= dedent_amount:
            lines[i] = line[dedent_amount:]
            lines_modified += 1
        
        i += 1
        
    if lines_modified > 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print(f"  Dedented {lines_modified} lines.")

def main():
    error_file = Path('compile_errors.txt')
    if not error_file.exists():
        print("compile_errors.txt not found")
        return

    errors = []
    with open(error_file, 'r', encoding='utf8') as f:
        content = f.read()
        
    # Regex para extraer archivo y línea
    # *** Sorry: IndentationError: unexpected indent (src/..., line 71)
    # O File "src/...", line 118
    
    matches = re.findall(r'[\("](src.*\.py)[",].*line (\d+)', content)
    
    # Procesar matches (eliminar duplicados si hay múltiples errores en mismo archivo, 
    # pero cuidado, corregir uno puede cambiar lineas. Mejor procesar inverso o recargar.)
    
    # Vamos a agrupar por archivo
    files_to_fix = {}
    for path_str, line_str in matches:
        path = Path(path_str)
        line = int(line_str)
        if path not in files_to_fix:
            files_to_fix[path] = []
        files_to_fix[path].append(line)
        
    for file_path, lines_nums in files_to_fix.items():
        # Ordenar líneas y procesar.
        # En realidad, si hay múltiples bloques, mejor procesar uno por uno.
        # Pero si corregimos un bloque, las líneas siguientes no cambian de número (solo de indentación).
        for line_num in sorted(lines_nums):
            fix_file_indentation(file_path, line_num)

if __name__ == '__main__':
    main()
