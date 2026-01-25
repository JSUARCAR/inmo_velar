import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Conexión a PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="db_inmo_velar",
    user="postgres",
    password=os.getenv("DB_PASSWORD", "")
)

conn.autocommit = False  # Usar transacciones para seguridad

try:
    cursor = conn.cursor()
    
    print("="*70)
    print("SCRIPT DE LIMPIEZA DE DESCUENTOS DUPLICADOS")
    print("="*70)
    
    # Paso 1: Identificar liquidaciones afectadas
    print("\n[PASO 1] Analizando duplicados...")
    cursor.execute("""
        SELECT 
            id_liquidacion_asesor,
            COUNT(*) as total_descuentos
        FROM DESCUENTOS_ASESORES
        GROUP BY id_liquidacion_asesor
        HAVING COUNT(*) > 3
        ORDER BY total_descuentos DESC
    """)
    
    liquidaciones_afectadas = cursor.fetchall()
    
    if not liquidaciones_afectadas:
        print("\n✓ No se encontraron liquidaciones con duplicados excesivos.")
        cursor.close()
        conn.close()
        exit(0)
    
    print(f"\n⚠️  Encontradas {len(liquidaciones_afectadas)} liquidaciones con descuentos duplicados:\n")
    
    total_descuentos = 0
    for liq_id, count in liquidaciones_afectadas[:10]:  # Mostrar primeras 10
        print(f"   Liquidación {liq_id}: {count:,} descuentos")
        total_descuentos += count
    
    if len(liquidaciones_afectadas) > 10:
        print(f"   ... y {len(liquidaciones_afectadas) - 10} liquidaciones más")
    
    print(f"\n   TOTAL: {total_descuentos:,} descuentos en BD")
    
    # Paso 2: Contar cuántos se eliminarán
    print("\n[PASO 2] Calculando descuentos a eliminar...")
    
    cursor.execute("""
        SELECT COUNT(*) FROM DESCUENTOS_ASESORES
    """)
    total_actual = cursor.fetchone()[0]
    
    # Contar cuántos únicos quedarían
    cursor.execute("""
        WITH unicos AS (
            SELECT MIN(id_descuento_asesor) as id_min
            FROM DESCUENTOS_ASESORES
            GROUP BY id_liquidacion_asesor, tipo_descuento, descripcion_descuento, valor_descuento
        )
        SELECT COUNT(*) FROM unicos
    """)
    total_unicos = cursor.fetchone()[0]
    
    a_eliminar = total_actual - total_unicos
    
    print(f"\n   Descuentos actuales: {total_actual:,}")
    print(f"   Descuentos únicos: {total_unicos:,}")
    print(f"   A ELIMINAR: {a_eliminar:,}")
    
    # Paso 3: Confirmación
    print("\n" + "="*70)
    print("⚠️  CONFIRMACIÓN REQUERIDA")
    print("="*70)
    print(f"\nEsta operación eliminará {a_eliminar:,} registros duplicados de DESCUENTOS_ASESORES.")
    print("Se conservará UNA copia de cada descuento único (mismo tipo+descripción+valor).")
    print("\nEscribe 'SI ELIMINAR' para confirmar (distingue mayúsculas): ", end='')
    
    confirmacion = input()
    
    if confirmacion != "SI ELIMINAR":
        print("\n❌ Operación cancelada por el usuario.")
        conn.rollback()
        cursor.close()
        conn.close()
        exit(0)
    
    # Paso 4: Ejecutar limpieza
    print("\n[PASO 3] Ejecutando limpieza...")
    
    # Eliminar duplicados conservando el ID más bajo de cada grupo
    cursor.execute("""
        DELETE FROM DESCUENTOS_ASESORES
        WHERE id_descuento_asesor NOT IN (
            SELECT MIN(id_descuento_asesor)
            FROM DESCUENTOS_ASESORES
            GROUP BY id_liquidacion_asesor, tipo_descuento, descripcion_descuento, valor_descuento
        )
    """)
    
    eliminados = cursor.rowcount
    
    # Paso 5: Recalcular totales en liquidaciones
    print(f"\n[PASO 4] Recalculando totales de liquidaciones...")
    
    cursor.execute("""
        UPDATE LIQUIDACIONES_ASESORES la
        SET total_descuentos = COALESCE(
            (SELECT SUM(valor_descuento) 
             FROM DESCUENTOS_ASESORES da 
             WHERE da.id_liquidacion_asesor = la.id_liquidacion_asesor),
            0
        ),
        valor_neto = (comision_bruta + COALESCE(total_bonificaciones, 0)) - COALESCE(
            (SELECT SUM(valor_descuento) 
             FROM DESCUENTOS_ASESORES da 
             WHERE da.id_liquidacion_asesor = la.id_liquidacion_asesor),
            0
        )
    """)
    
    actualizados = cursor.rowcount
    
    # Commit
    conn.commit()
    
    # Paso 6: Verificación
    print("\n[PASO 5] Verificando resultado...")
    cursor.execute("SELECT COUNT(*) FROM DESCUENTOS_ASESORES")
    final_count = cursor.fetchone()[0]
    
    print("\n" + "="*70)
    print("✅ LIMPIEZA COMPLETADA EXITOSAMENTE")
    print("="*70)
    print(f"\n   Descuentos eliminados: {eliminados:,}")
    print(f"   Descuentos restantes: {final_count:,}")
    print(f"   Liquidaciones actualizadas: {actualizados:,}")
    print(f"\n✓ Los totales de descuentos y valores netos han sido recalculados.\n")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\n⚠️  Haciendo ROLLBACK de cambios...")
    conn.rollback()
    import traceback
    traceback.print_exc()
    
finally:
    cursor.close()
    conn.close()
    print("\n✓ Conexión cerrada.\n")
