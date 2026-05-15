import sys
import os

# Añadir el directorio raíz al path para poder importar migraciones
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from migraciones.database_config import get_database_connection, print_config_info
    import psycopg2
except ImportError as e:
    print(f"Error al importar la configuración: {e}")
    sys.exit(1)

def vaciar_tablas_liquidaciones():
    """Vacía las tablas de liquidaciones en PostgreSQL (Railway)"""
    print_config_info()
    
    tablas = [
        "liquidaciones",
        "liquidaciones_asesores",
        "liquidaciones_contratos",
        "liquidaciones_propietarios"
    ]
    
    conn = None
    try:
        # Conectar a la base de datos
        print("\nConectando a la base de datos...")
        conn = get_database_connection()
        cursor = conn.cursor()
        
        # Unir nombres de tablas para la consulta
        nombres_tablas = ", ".join(tablas)
        
        print(f"Vaciando tablas: {nombres_tablas}...")
        
        # Ejecutar TRUNCATE con CASCADE
        # CASCADE asegura que se manejen las dependencias (foreign keys)
        sql = f"TRUNCATE TABLE {nombres_tablas} CASCADE;"
        cursor.execute(sql)
        
        # Confirmar los cambios
        conn.commit()
        print("✓ Tablas vaciadas exitosamente (CASCADE aplicado)")
        
        # Verificar conteo final
        print("\nVerificando estado final:")
        for tabla in tablas:
            cursor.execute(f"SELECT COUNT(*) FROM {tabla};")
            count = cursor.fetchone()[0]
            print(f"  - {tabla}: {count} registros")
            
        cursor.close()
        print("\n✓ Operación completada con éxito.")
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"\n[ERROR] Ocurrió un error al vaciar las tablas: {e}")
        sys.exit(1)
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    vaciar_tablas_liquidaciones()
