"""
Script de Migración: Agregar Campos de Administración a tabla PROPIEDADES

Agrega las siguientes columnas:
- TELEFONO_ADMINISTRACION TEXT
- TIPO_CUENTA_ADMINISTRACION TEXT
- NUMERO_CUENTA_ADMINISTRACION TEXT

Estos campos permiten almacenar información de contacto y datos bancarios
de la administración del edificio/conjunto para gestión de pagos.
"""

import sqlite3
import os
import sys

# Agregar path del proyecto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def ejecutar_migracion():
    """Ejecuta la migración para agregar campos de administración."""
    
    # Ruta a la base de datos (en raíz del proyecto)
    db_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "DB_Inmo_Velar.db"
    )
    
    print("=" * 60)
    print("MIGRACIÓN: Agregar Campos de Administración a PROPIEDADES")
    print("=" * 60)
    print(f"\nBase de datos: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"❌ ERROR: No se encontró la base de datos en {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar estado actual de la tabla
        print("\n1. Verificando estado actual de la tabla PROPIEDADES...")
        cursor.execute("PRAGMA table_info(PROPIEDADES)")
        columnas_actuales = {row[1] for row in cursor.fetchall()}
        print(f"   Columnas existentes: {len(columnas_actuales)}")
        
        # Columnas a agregar
        nuevas_columnas = [
            ("TELEFONO_ADMINISTRACION", "TEXT"),
            ("TIPO_CUENTA_ADMINISTRACION", "TEXT"),
            ("NUMERO_CUENTA_ADMINISTRACION", "TEXT")
        ]
        
        # Agregar columnas si no existen
        print("\n2. Agregando nuevas columnas...")
        columnas_agregadas = 0
        
        for columna, tipo in nuevas_columnas:
            if columna in columnas_actuales:
                print(f"   ⏭️  {columna} ya existe, omitiendo...")
            else:
                alter_sql = f"ALTER TABLE PROPIEDADES ADD COLUMN {columna} {tipo}"
                cursor.execute(alter_sql)
                print(f"   ✅ Agregada: {columna} ({tipo})")
                columnas_agregadas += 1
        
        conn.commit()
        
        # Verificar resultado
        print("\n3. Verificando resultado...")
        cursor.execute("PRAGMA table_info(PROPIEDADES)")
        columnas_finales = [row[1] for row in cursor.fetchall()]
        
        for columna, _ in nuevas_columnas:
            if columna in columnas_finales:
                print(f"   ✅ {columna}: OK")
            else:
                print(f"   ❌ {columna}: NO ENCONTRADA")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print(f"✅ MIGRACIÓN COMPLETADA - {columnas_agregadas} columnas agregadas")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR durante la migración: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    ejecutar_migracion()
