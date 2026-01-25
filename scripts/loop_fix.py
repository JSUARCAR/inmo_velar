"""
Auto-fix loop para errores de indentación.
Ejecuta compileall y auto_fix_indentation en bucle hasta que no haya errores.
"""
import os
import subprocess
import re
import sys
from pathlib import Path

# --- Inlining logic from auto_fix_indentation for simplicity ---

def get_indentation(line):
    return len(line) - len(line.lstrip())

def fix_file_indentation(file_path, error_line_num):
    print(f"Fixing {file_path.name} around line {error_line_num}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return

    if error_line_num > len(lines):
        return

    idx = error_line_num - 1
    target_indent = 8 
    initial_indent = get_indentation(lines[idx])
    
    if initial_indent <= target_indent:
        print(f"  Skipping: indent {initial_indent} seems correct (<= {target_indent})")
        # Forzar corrección si parece un bloque huérfano? 
        # A veces el error es 'unexpected indent' porque la linea anterior esta vacia o mal formata.
        # Pero confiemos en la lógica básica por ahora.
        return

    dedent_amount = 4
    lines_modified = 0
    i = idx
    while i < len(lines):
        line = lines[i]
        if not line.strip(): 
            i += 1
            continue
            
        current_indent = get_indentation(line)
        if current_indent < initial_indent:
            break
        
        if current_indent >= dedent_amount:
            lines[i] = line[dedent_amount:]
            lines_modified += 1
        i += 1
        
    if lines_modified > 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print(f"  Dedented {lines_modified} lines.")

def run_fix_cycle():
    # 1. Compile
    print("Running compileall...")
    result = subprocess.run(
        [sys.executable, '-m', 'compileall', 'src/infraestructura/persistencia/'],
        capture_output=True,
        text=True
    )
    
    output = result.stdout + result.stderr
    
    if result.returncode == 0:
        print("Compilation SUCCESS!")
        return True
        
    # 2. Parse errors
    matches = re.findall(r'[\("](src.*\.py)[",].*line (\d+)', output)
    if not matches:
        print("No matches found in output (syntax errors might vary).")
        print(output[:500])
        return True # Stop loop to check manually
        
    # Group by file
    files_to_fix = {}
    for path_str, line_str in matches:
        path = Path(path_str)
        line = int(line_str)
        files_to_fix[path] = line # Just take the last one or first? Compileall usually reports first per file.
        
    # 3. Fix
    count = 0
    for file_path, line_num in files_to_fix.items():
        fix_file_indentation(file_path, line_num)
        count += 1
        
    print(f"Fixed {count} files in this cycle.")
    return False

def main():
    max_cycles = 15
    for i in range(max_cycles):
        print(f"\n--- CYCLE {i+1} ---")
        success = run_fix_cycle()
        if success:
            break
    
    if not success:
        print("Failed to fix all errors after max cycles.")

if __name__ == '__main__':
    main()
