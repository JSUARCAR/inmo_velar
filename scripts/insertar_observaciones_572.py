"""
Script para insertar observaciones directamente en la BD
y verificar que los cambios funcionan.
"""

import psycopg2

DB_CONFIG = {
    "host": "hopper.proxy.rlwy.net",
    "port": 12937,
    "database": "railway",
    "user": "postgres",
    "password": "tBltIuhaUSMqQFvUMtSqIPFQZdXwpPtU"
}

def insertar_observaciones():
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("=" * 60)
        print("ACTUALIZANDO OBSERVACIONES LIQUIDACION #572")
        print("=" * 60)
        
        # 1. Verificar estado actual
        cursor.execute("""
            SELECT ID_LIQUIDACION, OBSERVACIONES, VALOR_INCIDENTES 
            FROM LIQUIDACIONES WHERE ID_LIQUIDACION = 572
        """)
        liq = cursor.fetchone()
        print(f"\nEstado ANTES:")
        print(f"  ID: {liq[0]}")
        print(f"  OBSERVACIONES: '{liq[1]}'")
        print(f"  VALOR_INCIDENTES: {liq[2]}")
        
        # 2. Verificar incidentes asociados
        cursor.execute("""
            SELECT ID_INCIDENTE FROM INCIDENTE_LIQUIDACION WHERE ID_LIQUIDACION = 572
        """)
        incidentes = cursor.fetchall()
        print(f"\nIncidentes asociados: {[i[0] for i in incidentes]}")
        
        # 3. Construir observaciones
        observaciones_nuevas = "\n".join([f"Inc #{i[0]}" for i in incidentes])
        print(f"\nObservaciones a insertar: '{observaciones_nuevas}'")
        
        # 4. Actualizar
        cursor.execute("""
            UPDATE LIQUIDACIONES 
            SET OBSERVACIONES = %s 
            WHERE ID_LIQUIDACION = 572
        """, (observaciones_nuevas,))
        
        conn.commit()
        print(f"\n[FILAS ACTUALIZADAS: {cursor.rowcount}]")
        
        # 5. Verificar después
        cursor.execute("""
            SELECT ID_LIQUIDACION, OBSERVACIONES, VALOR_INCIDENTES 
            FROM LIQUIDACIONES WHERE ID_LIQUIDACION = 572
        """)
        liq = cursor.fetchone()
        print(f"\nEstado DESPUES:")
        print(f"  ID: {liq[0]}")
        print(f"  OBSERVACIONES: '{liq[1]}'")
        print(f"  VALOR_INCIDENTES: {liq[2]}")
        
        print("\n" + "=" * 60)
        print("ACTUALIZACION COMPLETADA")
        print("=" * 60)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    insertar_observaciones()
