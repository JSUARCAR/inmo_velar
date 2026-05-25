"""
Quick fix script to patch repositorio_seguro_sqlite.py for PostgreSQL boolean compatibility
"""
import re

file_path = r"src\infraestructura\persistencia\repositorio_seguro_sqlite.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Already done - WHERE ESTADO_SEGURO = 1 -> WHERE ESTADO_SEGURO = {placeholder}

# Fix 2: cursor.execute(query) -> cursor.execute(query, (True,)) when solo_activos is True
# Find the listar_todos method and fix the execute call
pattern1 = r'(if solo_activos:\s+query \+= f" WHERE ESTADO_SEGURO = \{placeholder\}"\s+query \+= " ORDER BY NOMBRE_SEGURO"\s+)cursor\.execute\(query\)'
replacement1 = r'\1if solo_activos:\n                cursor.execute(query, (True,))\n            else:\n                cursor.execute(query)'
content = re.sub(pattern1, replacement1, content, flags=re.MULTILINE | re.DOTALL)

# Fix 3: desactivar method - ESTADO_SEGURO = 0 
pattern2 = r'(def desactivar.*?cursor\.execute\(""".*?)ESTADO_SEGURO = 0,(.*?""", \()motivo,'
replacement2 = r'\1ESTADO_SEGURO = {placeholder},\2False, motivo,'
content = re.sub(pattern2, replacement2, content, flags=re.MULTILINE | re.DOTALL)

# Fix 4: activar method - ESTADO_SEGURO = 1
pattern3 = r'(def activar.*?cursor\.execute\(""".*?)ESTADO_SEGURO = 1,(.*?""", \()(ahora,'
replacement3 = r'\1ESTADO_SEGURO = {placeholder},\2True, \3'
content = re.sub(pattern3, replacement3, content, flags=re.MULTILINE | re.DOTALL)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Patched repositorio_seguro_sqlite.py successfully")
