import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="db_inmo_velar",
    user="postgres",
    password=os.getenv("DB_PASSWORD", "")
)

conn.autocommit = False

try:
    cursor = conn.cursor()
    
    print("="*70)
    print("RECALCULANDO TOTALES DE LIQUIDACIONES")
    print("="*70)
    
    print("\n[1] Actualizando total_descuentos y valor_neto_asesor...")
    
    cursor.execute("""
        UPDATE LIQUIDACIONES_ASESORES la
        SET total_descuentos = COALESCE(
            (SELECT SUM(valor_descuento) 
             FROM DESCUENTOS_ASESORES da 
             WHERE da.id_liquidacion_asesor = la.id_liquidacion_asesor),
            0
        ),
        valor_neto_asesor = (comision_bruta + COALESCE(total_bonificaciones, 0)) - COALESCE(
            (SELECT SUM(valor_descuento) 
             FROM DESCUENTOS_ASESORES da 
             WHERE da.id_liquidacion_asesor = la.id_liquidacion_asesor),
            0
        )
    """)
    
    actualizados = cursor.rowcount
    conn.commit()
    
    print(f"\n✅ Recálculo completado exitosamente")
    print(f"   Liquidaciones actualizadas: {actualizados:,}\n")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    conn.rollback()
    import traceback
    traceback.print_exc()
    
finally:
    cursor.close()
    conn.close()
    print("✓ Conexión cerrada.\n")
