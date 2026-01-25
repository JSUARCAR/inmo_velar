# SOLUCIÓN DE EMERGENCIA: Script para eliminar descuentos duplicados

import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="db_inmo_velar",
    user="postgres",
    password=""
)

try:
    cursor = conn.cursor()
    
    # Ver cuántos descuentos están duplicados
    cursor.execute("""
        SELECT ID_LIQUIDACION_ASESOR, COUNT(*) as total
        FROM DESCUENTOS_ASESORES
        GROUP BY ID_LIQUIDACION_ASESOR
        HAVING COUNT(*) > 5
        ORDER BY total DESC
    """)
    
    print("=== Liquidaciones con descuentos duplicados ===")
    for row in cursor.fetchall():
        print(f"Liquidación {row[0]}: {row[1]} descuentos")
    
    # Identificar duplicados exactos (mismo tipo, descripción, valor)
    print("\n¿Deseas eliminar TODOS los descuentos duplicados? (esto dejará solo 1 de cada tipo)")
    print("ADVERTENCIA: Esta acción eliminará registros de la base de datos")
    print("Escribe 'SI CONFIRMO' para proceder:")
    
    # Este script requiere confirmación manual
    # NO auto-ejecutar
    
except Exception as e:
    print(f"Error: {e}")
finally:
    cursor.close()
    conn.close()
