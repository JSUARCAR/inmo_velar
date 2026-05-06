"""
Script de Migración: Agregar Códigos CIU a tabla PROPIEDADES
Fecha: 2025-12-24
Descripción: Agrega tres columnas nuevas para almacenar códigos de servicios públicos:
             - CODIGO_ENERGIA (Código del servicio de energía eléctrica)
             - CODIGO_AGUA (Código del servicio de acueducto)
             - CODIGO_GAS (Código del servicio de gas natural)
"""

import sqlite3
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.infraestructura.persistencia.database import DatabaseManager


def ejecutar_migracion():
    """Ejecuta la migración para agregar columnas de códigos CIU."""
    
    print("=" * 60)
    print("MIGRACION: Agregar Codigos CIU a PROPIEDADES")
    print("=" * 60)
    
    db_manager = DatabaseManager()
    
    try:
        # Obtener conexión
        conexion = db_manager.obtener_conexion()
        
        # Verificar si las columnas ya existen
        print("\n1. Verificando estado actual de la tabla PROPIEDADES...")
        cursor = conexion.cursor()
        cursor.execute("PRAGMA table_info(PROPIEDADES)")
        columnas_existentes = [row[1] for row in cursor.fetchall()]
        
        print(f"   Columnas actuales: {len(columnas_existentes)}")
        
        columnas_nuevas = ["CODIGO_ENERGIA", "CODIGO_AGUA", "CODIGO_GAS"]
        columnas_a_agregar = [col for col in columnas_nuevas if col not in columnas_existentes]
        
        if not columnas_a_agregar:
            print("\n[OK] Las columnas ya existen. No se requiere migracion.")
            return True
        
        print(f"\n2. Columnas a agregar: {columnas_a_agregar}")
        
        # Agregar cada columna individualmente
        for columna in columnas_a_agregar:
            print(f"\n   Agregando columna: {columna}...")
            alter_sql = f"ALTER TABLE PROPIEDADES ADD COLUMN {columna} TEXT"
            cursor.execute(alter_sql)
            conexion.commit()
            print(f"   [OK] Columna {columna} agregada exitosamente")
        
        # Verificar que las columnas se agregaron correctamente
        print("\n3. Verificando migracion...")
        cursor.execute("PRAGMA table_info(PROPIEDADES)")
        columnas_finales = [row[1] for row in cursor.fetchall()]
        
        for columna in columnas_nuevas:
            if columna in columnas_finales:
                print(f"   [OK] {columna} - OK")
            else:
                print(f"   [ERROR] {columna} - FALTA")
                return False
        
        # Mostrar ejemplo de uso
        print("\n4. Ejemplo de uso:")
        print("   UPDATE PROPIEDADES SET")
        print("       CODIGO_ENERGIA = '123456',")
        print("       CODIGO_AGUA = 'AGUA-001',")
        print("       CODIGO_GAS = 'GAS-999'")
        print("   WHERE ID_PROPIEDAD = 1;")
        
        print("\n" + "=" * 60)
        print("[OK] MIGRACION COMPLETADA EXITOSAMENTE")
        print("=" * 60)
        
        return True
        
    except sqlite3.Error as e:
        print(f"\n[ERROR] Error durante la migracion: {e}")
        conexion.rollback()
        return False
    
    except Exception as e:
        print(f"\n[ERROR] Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        db_manager.cerrar_todas_conexiones()



if __name__ == "__main__":
    resultado = ejecutar_migracion()
    sys.exit(0 if resultado else 1)
