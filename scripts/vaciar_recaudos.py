import sys
import os
from pathlib import Path

# Asegurar que el directorio raíz esté en el PYTHONPATH para importar migraciones.database_config
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

try:
    from migraciones.database_config import get_database_connection, print_config_info
    import psycopg2
except ImportError as e:
    print(f"Error importando configuración: {e}")
    sys.exit(1)

def vaciar_recaudos():
    """Vacía la tabla recaudos de forma segura usando DELETE"""
    print_config_info()
    
    conn = None
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        
        # 1. Contar registros actuales
        cursor.execute("SELECT COUNT(*) FROM recaudos;")
        count_before = cursor.fetchone()[0]
        print(f"\nRegistros actuales en 'recaudos': {count_before}")
        
        if count_before == 0:
            print("La tabla ya está vacía. No hay nada que hacer.")
            return

        # 2. Ejecutar DELETE
        print("Vaciando tabla 'recaudos'...")
        cursor.execute("DELETE FROM recaudos;")
        
        # 3. Confirmar cambios
        conn.commit()
        print(f"✓ Éxito: Se han eliminado {count_before} registros de 'recaudos'.")
        
        # 4. Verificar
        cursor.execute("SELECT COUNT(*) FROM recaudos;")
        count_after = cursor.fetchone()[0]
        print(f"Registros finales: {count_after}")
        
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        print(f"\n[ERROR] Error de PostgreSQL: {e}")
        print("\nEs posible que la tabla tenga dependencias (claves foráneas) en otras tablas.")
        print("Sugerencia: Revisa las tablas 'recaudo_conceptos' o 'recaudo_arrendamiento'.")
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"\n[ERROR] Error inesperado: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    vaciar_recaudos()
