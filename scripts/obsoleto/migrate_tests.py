import os

files_to_modify = [
    # Tests (7)
    "tests/integration/test_servicios_aplicacion/test_renovacion.py",
    "tests/integration/test_servicios_aplicacion/test_servicio_personas.py",
    "tests/integration/test_repositorios/test_repositorio_persona.py",
    "tests/integration/test_repositorios/test_filtros_persona_especificos.py",
    "tests/integration/test_repositorio_parametro.py",
    "tests/integration/test_repositorios/test_repositorio_propiedad.py",
    "scripts/verify_lote2_pagination.py", # This is one of the tests apparently? Let's also check others

    # Scripts (10 - let's find verify_*.py)
]

# Let's find the exact paths
import glob

all_test_scripts = glob.glob("tests/**/*.py", recursive=True)
all_verify_scripts = glob.glob("scripts/verify_*.py", recursive=True)

targets = [
    "test_renovacion.py",
    "test_servicio_personas.py",
    "test_repositorio_persona.py",
    "test_filtros_persona_especificos.py",
    "test_repositorio_parametro.py",
    "test_repositorio_propiedad.py",
]

to_process = []
for f in all_test_scripts:
    if os.path.basename(f) in targets:
        to_process.append(f)

for f in all_verify_scripts:
    to_process.append(f)

import re

for path in set(to_process):
    if not os.path.exists(path): continue
    
    with open(path, "r", encoding="utf-8") as file:
        content = file.read()
    
    # Replace the imports and class names
    new_content = re.sub(r'repositorio_([a-zA-Z0-9_]+)_sqlite', r'repositorio_\1_postgres', content)
    new_content = re.sub(r'Repositorio([a-zA-Z0-9_]+)SQLite', r'Repositorio\1Postgres', new_content)
    
    if content != new_content:
        with open(path, "w", encoding="utf-8") as file:
            file.write(new_content)
        print(f"Updated {path}")
