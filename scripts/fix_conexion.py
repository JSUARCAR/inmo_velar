"""
Script para arreglar get_connection -> obtener_conexion en todos los repositorios
"""
import os
from pathlib import Path

# Directorios a procesar
repo_dir = Path("src/infraestructura/persistencia")

# Buscar archivos
archivos = list(repo_dir.glob("repositorio_*.py"))

print(f"Encontrados {len(archivos)} archivos de repositorios")

for archivo in archivos:
    print(f"Procesando: {archivo.name}...")
    
    # Leer contenido
    with open(archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Reemplazar
    contenido_nuevo = contenido.replace('get_connection', 'obtener_conexion')
    
    # Escribir
    with open(archivo, 'w', encoding='utf-8') as f:
        f.write(contenido_nuevo)
    
    print(f"  [OK] {archivo.name}")

print("\n[OK] Todos los archivos actualizados")
