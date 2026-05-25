import os

def procesar_archivos():
    src_dir = os.path.join(os.path.dirname(__file__), "..", "..", "src")
    archivos_modificados = 0
    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if file has "Activo" inside single or double quotes
                # To be safer we replace 'Activo' with 'ACTIVO' and "Activo" with "ACTIVO"
                new_content = content.replace("'Activo'", "'ACTIVO'").replace('"Activo"', '"ACTIVO"')
                
                if new_content != content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    archivos_modificados += 1
                    print(f"Modificado: {filepath}")

    print(f"Total de archivos modificados: {archivos_modificados}")

if __name__ == "__main__":
    procesar_archivos()
