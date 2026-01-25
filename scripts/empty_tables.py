import psycopg2
from psycopg2 import sql

# Configuración de la base de datos obtenida del .env
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'db_inmo_velar',
    'user': 'inmo_user',
    'password': '7323'
}

def vaciar_tablas():
    """Vacía las tablas descuentos_asesores y liquidaciones_asesores"""
    try:
        # Conectar a la base de datos
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print(f"Conectado a la base de datos {DB_CONFIG['database']} como {DB_CONFIG['user']}")
        
        # Truncar las tablas
        print("\nVaciando tabla descuentos_asesores...")
        cursor.execute("TRUNCATE TABLE descuentos_asesores CASCADE;")
        print("✓ Tabla descuentos_asesores vaciada")
        
        print("\nVaciando tabla liquidaciones_asesores...")
        cursor.execute("TRUNCATE TABLE liquidaciones_asesores CASCADE;")
        print("✓ Tabla liquidaciones_asesores vaciada")
        
        # Confirmar los cambios
        conn.commit()
        print("\n✓ Cambios confirmados en la base de datos")
        
        # Verificar que las tablas están vacías
        cursor.execute("SELECT COUNT(*) FROM descuentos_asesores;")
        count_descuentos = cursor.fetchone()[0]
        print(f"\nRegistros en descuentos_asesores: {count_descuentos}")
        
        cursor.execute("SELECT COUNT(*) FROM liquidaciones_asesores;")
        count_liquidaciones = cursor.fetchone()[0]
        print(f"Registros en liquidaciones_asesores: {count_liquidaciones}")
        
        cursor.close()
        conn.close()
        print("\n✓ Operación completada exitosamente")
        
    except psycopg2.Error as e:
        print(f"Error de PostgreSQL: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    vaciar_tablas()
